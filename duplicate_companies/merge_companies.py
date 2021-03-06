import datetime
from infusionsoft.library import Infusionsoft, InfusionsoftOAuth
import pandas as pd

from constants import FIELDS
from infusionsoft_actions import get_table

APPNAME = 'hk477'
API_KEY = '7e3e6381bcf8bf37a65191e2ad0257b37bf04cc974444c98e52712a1afdd3e4e'
# ACCESS_TOKEN = 'z3sfk68fqrynjr33dwbewghq'

ifs = Infusionsoft(APPNAME, API_KEY)
# ifs = InfusionsoftOAuth(ACCESS_TOKEN)

df = pd.read_csv('duplicate_companies (exact).csv')
df = df.dropna()

company_fields = FIELDS['Company'][:]
company_cfs = get_table(ifs, 'DataFormField', {'FormId': -6}, ['Name'])
company_fields += list(map(lambda x: "_" + x.get('Name'), company_cfs))

deleted_companies = []

start = datetime.datetime.now()

for index, row in df.iterrows():
    orig_id = int(row.orig_id)
    dupe_id = int(row.dupe_id)
    print("\nMerging {} with {}".format(orig_id, dupe_id))
    orig_comp = ifs.DataService('load', 'Company', orig_id, company_fields)
    dupe_comp = ifs.DataService('load', 'Company', dupe_id, company_fields)

    if isinstance(orig_comp, tuple) or isinstance(dupe_comp, tuple):
        print(f"{orig_id} or {dupe_id} already merged.")
        continue

    if orig_id in deleted_companies or dupe_id in deleted_companies:
        print("{} already merged.".format(orig_id))
        continue

    orig_name = orig_comp.get('Company')

    # Reassign contacts
    contacts = []
    for contact in get_table(
            ifs,
            'Contact',
            query={'CompanyId': dupe_id},
            fields=['Id']):
        if contact.get('Id') != dupe_id:
            contacts += [contact]

    for contact in contacts:
        ifs.DataService(
            'update',
            'Contact',
            contact.get('Id'),
            {'AccountId': orig_id, 'CompanyId': orig_id, 'Company': orig_name})

    # Reassign Actions
    actions = get_table(
        ifs,
        'ContactAction',
        query={'ContactId': dupe_id},
        fields=['Id'])
    for action in actions:
        ifs.DataService(
            'update',
            'ContactAction',
            action.get('Id'),
            {'ContactId': orig_id})

    # Reassign opportunities
    opps = get_table(
        ifs,
        'Lead',
        query={'ContactID': dupe_id},
        fields=['Id'])
    for opp in opps:
        ifs.DataService(
            'update',
            'Lead',
            opp.get('Id'),
            {'ContactID': orig_id})

    # Reapply tags
    tags = get_table(
        ifs,
        'ContactGroupAssign',
        query={'ContactId': dupe_id},
        fields=['GroupId'])
    for tag in tags:
        ifs.ContactService('addToGroup', orig_id, tag.get('GroupId'))

    # Update company fields
    fields = {}
    for field in company_fields:
        if orig_comp.get(field) or dupe_comp.get(field):
            fields[field] = orig_comp.get(field) or dupe_comp.get(field)
    ifs.DataService('update', 'Company', orig_id, fields)

    # Delete dupe company
    ifs.DataService('delete', 'Company', dupe_id)
    print("{} deleted and merged with {}.".format(dupe_id, orig_id))
    deleted_companies += [dupe_id]

print(datetime.datetime.now() - start)
