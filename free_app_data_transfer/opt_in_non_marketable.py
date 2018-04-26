from infusionsoft.library import Infusionsoft

from constants import FIELDS
from infusionsoft_actions import get_table

APPNAME = 'fr404'
API_KEY = '38dfb85bd28747255962d5e9b417e6d4'

ifs = Infusionsoft(APPNAME, API_KEY)

contact_emails = list(map(lambda x: x.get('Email'), get_table(
    ifs,
    'Contact',
    query={'Email': '_%'},
    fields=['Email']
)))

emails = list(map(lambda x: x.get('Email'), get_table(
    ifs,
    'EmailAddStatus',
    query={'Type': 'NonMarketable'},
    fields=['Email', 'Type'])))

num_opted_in = 0
for email in emails:
    if email in contact_emails:
        num_opted_in += 1
        ifs.APIEmailService(
            'optIn',
            email,
            'Transfer from Free Trial App')
        print('{} successfully opted in!'.format(email))

print("{} emails opted in.".format(num_opted_in))
