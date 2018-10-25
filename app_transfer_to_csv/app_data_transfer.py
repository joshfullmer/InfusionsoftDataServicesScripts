from pprint import pprint
import requests

from database.utils import get_app_and_token


def adt():
    src_app, src_token = get_app_and_token('Source Application')
    dest_app, dest_token = get_app_and_token('Destination Application')

    url = 'https://api.infusionsoft.com/crm/rest/v1'
    ext = '/contacts/model'
    src_headers = {'Authorization': 'Bearer ' + src_token}
    dest_headers = {'Authorization': 'Bearer ' + dest_token}
    resp = requests.get(url+ext, headers=src_headers)
    src_custom_fields = resp.json().get('custom_fields')
    resp = requests.get(url+ext, headers=dest_headers)
    dest_custom_fields = resp.json().get('custom_fields')
    dest_cf_labels = [cf.get('label') for cf in dest_custom_fields]
    ext = '/contacts/model/customFields'
    for cf in src_custom_fields:
        if cf.get('label') in dest_cf_labels:
            continue
        cf.pop('id', None)
        cf.pop('record_type', None)
        print(cf)
        options = cf.get('options')
        for option in options:
            option.pop('id', None)
            if 'options' in option.keys() and option.get('options'):
                for op in option.get('options'):
                    op.pop('id', None)
        cf['options'] = options
        resp = requests.post(url+ext, headers=dest_headers, json=cf)
        print(resp)
        pprint(resp.json())
