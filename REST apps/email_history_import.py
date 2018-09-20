import base64
import datetime
import requests

token = "t43xfaedjrumqtrk39v3vrdz"
rest_url = "https://api.infusionsoft.com/crm/rest/v1"
headers = {"Authorization": "Bearer " + token,
           "Content-Type": "application/json;charset=UTF-8",
           "Accept": "application/json, */*"}

date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S-0700")

data = {
    "contact_id": 4,
    "html_content": base64.encodestring(b"<p>Hello</p>").decode("utf-8"),
    "opened_date": date,
    "plain_content": base64.encodestring(b"Hello").decode("utf-8"),
    "received_date": date,
    "sent_date": date,
    "sent_from_address": "joshfullmer@me.com",
    "sent_to_address": "josh.fullmer@infusionsoft.com",
    "subject": "API Test"
}

response = requests.post(rest_url + "/emails", headers=headers, json=data)

print(response.json())
