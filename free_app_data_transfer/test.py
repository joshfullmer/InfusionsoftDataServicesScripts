import base64
import pprint
import requests

token = 'k4m2yx93rvau7aev67yauaft'

headers = {'Authorization': "Bearer " + token}
response = requests.get(
    'https://api.infusionsoft.com/crm/rest/v1/emails/2048',
    headers=headers)
resp_json = response.json()

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(resp_json)
html_content = resp_json.get('html_content')
decoded_html = base64.b64decode(html_content)
print(decoded_html)

response = requests.get(
    '''https://api.infusionsoft.com/crm/rest/v1/
       companies?optional_properties=custom_fields''',
    headers=headers)
pp.pprint(response.json())
