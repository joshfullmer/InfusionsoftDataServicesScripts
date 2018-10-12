import datetime as dt
import requests
from urllib.parse import urlencode

from database.models import Instance


def get_app_and_api(message):
    print(message)
    appname = input('Appname: ')
    apikey = Instance.get_apikey(appname)
    if apikey:
        resp = input('API key found. Use this one? (yN)')
        if resp.lower() == 'n':
            apikey = None
    if not apikey:
        apikey = input('API key: ')
    Instance.create_or_update(appname, apikey)
    return appname, apikey


def get_app_and_token(message):
    print(message)
    appname = input('Appname: ')
    instance, _ = Instance.get_or_create(appname=appname)
    if instance.access_token:
        expired = instance.access_token_expiry < dt.datetime.now()
        if expired:
            instance = Instance.update_token(appname)
    else:
        url = 'https://signin.infusionsoft.com/app/oauth/authorize'
        redirect_uri = 'https://infusionsoftdataservices.herokuapp.com/code/'
        url_params = urlencode({
            'client_id': 'nndwt7ass8w95kqfgh2utw9h',
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'full',
        })
        url += f'?{url_params}'
        print(f'Go to this URL: {url}\nAuthorize the app')
        auth_code = input('Paste the authorization code: ')
        url = 'https://api.infusionsoft.com/token'
        params = {
            'client_id': 'nndwt7ass8w95kqfgh2utw9h',
            'client_secret': 'fWew3CY7zp',
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }
        resp = requests.post(url, params)
        r_json = resp.json()
        instance = Instance.create_or_update(
            appname,
            access_token=r_json.get('access_token'),
            refresh_token=r_json.get('refresh_token'),
        )
    return appname, instance.access_token
