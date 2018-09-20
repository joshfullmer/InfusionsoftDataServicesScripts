from base64 import b64encode
import requests


API_URL = 'https://api.infusionsoft.com/crm/rest/v1/'


def get_access_token_response(request, code):
    params = {
        'client_id': 'nndwt7ass8w95kqfgh2utw9h',
        'client_secret': 'fWew3CY7zp',
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': request.build_absolute_uri('?'),
    }
    response = requests.post(
        'https://api.infusionsoft.com/token',
        params,
    )
    return response


def get_refresh_token_response(refresh_token):
    b64_cred = b64encode(b'nndwt7ass8w95kqfgh2utw9h:fWew3CY7zp')
    authorization = 'Basic ' + b64_cred.decode('utf-8')
    params = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
    }
    headers = {
        'Authorization': authorization
    }
    response = requests.post(
        'https://api.infusionsoft.com/token',
        params,
        headers=headers,
    )
    return response
