from infusionsoft.library import Infusionsoft
from infusionsoft_actions import get_table

APPNAME = 'wb420'
API_KEY = '9796f2d8f3a7f058fd6c9f9a9061e73e'

ifs = Infusionsoft(APPNAME, API_KEY)

contacts = get_table(ifs, 'Contact', fields=['Id', 'Company', 'AccountId'])
contact_companies = set(map(lambda x: x.get('Company'), contacts)) - {None, }

existing_companies = get_table(ifs, 'Company', fields=['Company'])
existing_companies = list(map(lambda x: x.get('Company'), existing_companies))

for com in contact_companies:
    if com not in existing_companies:
        com_id = ifs.DataService('add', 'Company', {'Company': com})
        print("Company '{}' ID {} created.".format(com, com_id))

companies = get_table(ifs, 'Company', fields=['Id', 'Company'])
companies = {c.get('Company'): c.get('Id') for c in companies}

for con in contacts:
    if con.get('AccountId') == 0 and con.get('Company'):
        ifs.DataService(
            'update',
            'Contact',
            con.get('Id'),
            {'AccountId': companies.get(con.get('Company'))})
        print("Contact ID {} updated.".format(con.get('Id')))
