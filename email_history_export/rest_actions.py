import requests
from html.parser import HTMLParser


def get_all_emails(token):
    offset = 0
    emails = []
    headers = {'Authorization': "Bearer " + token}

    while True:
        url = f'''https://api.infusionsoft.com/crm/rest/v1/
                  emails?offset={offset}'''
        response = requests.get(
            url,
            headers=headers)
        json = response.json()
        if json.get('count') < offset:
            break
        emails += json.get('emails')
        offset += 1000

    return emails


def get_email(token, id):
    url = f'https://api.infusionsoft.com/crm/rest/v1/emails/{id}'
    headers = {'Authorization': "Bearer " + token}
    return requests.get(url, headers=headers).json()


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
