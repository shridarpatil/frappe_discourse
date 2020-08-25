## Frappe Discourse


Simple frappe app to setup Single sign-on for discource.

### Install
Run the following command to install the app

`bench get-app https://github.com/shridarpatil/frappe_discourse.git`

`bench install-app frappe_discourse`

### Setup
Register a client in `Discourse Settings` DocType with client id, client secret and sso secret.

![image](https://user-images.githubusercontent.com/11792643/88766285-60a54e80-d195-11ea-8b4e-c4956cb2f8e1.png)


Next: Add the url in discouse sso with parameter client.
`https://<sitename>/api/method/frappe_discourse.frappe_discourse.doctype.discourse_settings.discourse_settings.discourse_login?client=<token>`
token is base64 incoded string of client id and client secret b64encode(client_id:client_secret)



![discourse_sso](https://user-images.githubusercontent.com/11792643/88766210-43708000-d195-11ea-80f2-e612cf0b8d4b.gif)


#### License

MIT# frappe_discourse
