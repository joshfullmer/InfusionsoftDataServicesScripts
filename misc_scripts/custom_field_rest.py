import pprint
import requests


token = 'qff7pav7rayyfyae4rqstge5'
headers = {"Authorization": "Bearer " + token,
           "Content-Type": "application/json;charset=UTF-8",
           "Accept": "application/json, */*"}
url = 'https://api.infusionsoft.com/crm/rest/v1/'

data = {
    'field_type': 'Text',
    'label': 'REST API Custom Field',
}

response = requests.get(
    url + 'contacts/4?optional_properties=custom_fields',
    headers=headers
)
pprint.pprint(response.json())
response = requests.get(
    url + 'contacts/model',
    headers=headers
)
pprint.pprint(response.json())
