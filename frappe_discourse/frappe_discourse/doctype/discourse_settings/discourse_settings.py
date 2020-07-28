# -*- coding: utf-8 -*-
# Copyright (c) 2020, Shridhar Patil and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import hmac
from base64 import b64decode, b64encode
from urllib.parse import urlencode
import hashlib
from urllib.parse import parse_qs


class DiscourseSettings(Document):
    pass


@frappe.whitelist(allow_guest=True)
def discourse_login():
    """Generate signature for discourse sso."""
    if frappe.session.user == 'Guest':
        print(frappe.local.form_dict)
        redirect_url = '/api/method/frappe_discourse.frappe_discourse.doctype.discourse_settings.discourse_settings.discourse_login' # noqa
        frappe.local.response["type"] = "redirect"
        client = frappe.local.form_dict.get("client")
        sig = frappe.local.form_dict.get("sig")
        sso = frappe.local.form_dict.get("sso")

        # creating this because frappe redirect-to uses single param
        client = f'{client}||{sig}||{sso}'
        frappe.local.response["location"]  = f'/login?redirect-to={redirect_url}?client_redirect={client}' # noqa

    else:

        if frappe.local.form_dict.get('client_redirect'):
            data = frappe.local.form_dict.get('client_redirect').split('||')
            client = data[0]
            sig = data[1]
            sso = data[2]
        else:
            client = frappe.local.form_dict.get("client")
            sig = frappe.local.form_dict.get('sig')
            sso = frappe.local.form_dict.get('sso')

        # Get client id and client secret from the base64 encoded string
        client_data = str((b64decode(client)),'utf-8').split(':')
        client_id = client_data[0]
        secret = client_data[1]

        # fetch client secret from the client and sso secret for the given client
        settings = frappe.get_doc("Discourse Settings", client_id)
        client_secret = settings.get_password("client_secret")
        sso_secret = settings.get_password("sso_secret")

        # parse sso
        url = decode_dict(parse_qs(b64decode(sso)))
        nonce = url['nonce'][0].decode("utf-8")
        return_sso_url = url['return_sso_url'][0].decode("utf-8")

        # Generate signature
        if signature_is_valid(
            b64encode(bytes(urlencode({
                "nonce": nonce,
                "return_sso_url": return_sso_url
            }), encoding='utf-8')),
            sso_secret,
            sig
        ):

            if client_secret == secret:
                # Generate payload to pass to discourse
                new_payload = make_payload(nonce)
                our_signature = sign(new_payload, sso_secret)
                frappe.local.response["type"] = "redirect"
                frappe.local.response["location"]  = f'{settings.redirect_url}?sig={our_signature}&sso={new_payload.decode("utf-8")}'
                return

        frappe.throw("Invalid credentials")


def make_payload(nonce):
    """Payload to generate signature."""
    user = frappe.get_doc("User", frappe.session.user)

    return b64encode(bytes(urlencode({
        "nonce": nonce,
        "name": user.full_name,
        "email": user.email,
        "external_id": frappe.session.user
    }), encoding='utf-8'))


def sign(payload_b64, sso_secret):
    return hmac.new(bytes(sso_secret, 'utf-8'), payload_b64, hashlib.sha256).hexdigest()



def decode_dict(d):
    """Decode dict."""
    result = {}
    for key, value in d.items():
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, dict):
            value = decode_dict(value)
        result.update({key: value})
    return result


def signature_is_valid(payload, secret, their_sig):
    """Validate signature."""
    our_sig = sign(payload, secret)

    return hmac.compare_digest(their_sig, our_sig)