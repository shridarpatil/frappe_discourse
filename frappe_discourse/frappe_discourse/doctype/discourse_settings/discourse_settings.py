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



sso_secret = b'discourse.sso.secret'


class DiscourseSettings(Document):
    pass


@frappe.whitelist(allow_guest=True)
def discourse_login():
    # frappe.local.response["type"] = "redirect"
    if frappe.session.user == 'Guest':
        redirect_url = '/api/method/frappe_discourse.frappe_discourse.doctype.discourse_settings.discourse_settings.discourse_login' # noqa
        frappe.local.response["type"] = "redirect"
        frappe.local.response["location"]  = f'/login?redirect-to={redirect_url}?sig={frappe.local.form_dict.get("sig")}' # noqa

    else:

        sig = str((b64decode(frappe.local.form_dict.get("sig"))),'utf-8').split(':')
        client_id = sig[0]
        secret = sig[1]

        settings = frappe.get_doc("Discourse Settings", client_id)
        client_secret = settings.get_password("client_secret")

        if client_secret == secret:
            our_signature = sign(make_payload())

            # return ({ "sig": our_signature, "status": our_signature==sig})

            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"]  = f'{settings.redirect_url}?sig={our_signature}'
        else:
            frappe.throw("Invalid credentials")
    return


def make_payload():
    print(type(urlencode({"name": frappe.session.user_fullname, "email": frappe.session.user_email, "user": frappe.session.user    })))

    return b64encode(bytes(urlencode({
        "name": frappe.session.user_fullname,
        "email": frappe.session.user_email,
        "user": str(frappe.session.user)
    }), encoding='utf-8'))


def sign(payload_b64):
    return hmac.new(sso_secret, payload_b64, hashlib.sha256).hexdigest()