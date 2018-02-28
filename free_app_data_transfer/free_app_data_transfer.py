from infusionsoft.library import Infusionsoft

from constants import (QJ154_APIKEY, TE361_APIKEY, FIELDS, DATATYPES)
from infusionsoft_actions import get_table, create_custom_field

SOURCE_APPNAME = 'qj154'
SOURCE_API_KEY = QJ154_APIKEY
DESTINATION_APPNAME = 'te361'
DESTINATION_API_KEY = TE361_APIKEY

CONTACTS_WITH_TAG_IDS = []

src_infusionsoft = Infusionsoft(SOURCE_APPNAME, SOURCE_API_KEY)
dest_infusionsoft = Infusionsoft(DESTINATION_APPNAME, DESTINATION_API_KEY)

"""
Contacts
Contact Custom Fields
Tags
Tag Assign
Contact Action
"""

src_contact_id = create_custom_field(dest_infusionsoft,
                                     'Source App Contact ID')['Name']

contact_fields = FIELDS['Contact'][:]
custom_fields = get_table(src_infusionsoft, 'DataFormField')
rename_mapping = {}
for custom_field in custom_fields:
    if custom_field['FormId'] == -1 and custom_field['DataType'] != 23:
        contact_fields += ["_{}".format(custom_field['Name'])]

        field = create_custom_field(dest_infusionsoft,
                                    custom_field['Label'],
                                    'Contact',
                                    DATATYPES[custom_field['DataType']],
                                    custom_field.get('Values'))

        rename_mapping["_" + custom_field['Name']] = field['Name']

query = {}
if CONTACTS_WITH_TAG_IDS:
    contact_ids = []
    for tag in get_table(src_infusionsoft,
                         'ContactGroupAssign',
                         {},
                         ['ContactId', 'GroupId']):
        if tag['GroupId'] in CONTACTS_WITH_TAG_IDS:
            contact_ids += [tag['ContactId']]
    query['Id'] = list(set(contact_ids))

existing_contacts = {}
for contact_id in get_table(dest_infusionsoft,
                            'Contact',
                            {src_contact_id: '_%'},
                            ['Id', src_contact_id]):
    existing_contacts[int(contact_id[src_contact_id])] = contact_id['Id']

contact_fields.remove("_Listboxtest")

contacts = get_table(src_infusionsoft, 'Contact', query, contact_fields)
for contact in contacts:
    if existing_contacts.get(int(contact['Id'])):
        print("Contact already exists: Contact ID {}".format(
            existing_contacts[contact['Id']]))
        continue
    if contact['Id'] == contact['CompanyID']:
        print("The contact is a company (ID: {})... skipping".format(
            contact['CompanyID']))
        continue
    for key in contact_fields:
        if rename_mapping.get(key):
            contact[rename_mapping[key]] = contact.pop(key, None)
    contact[src_contact_id] = str(contact['Id'])
    contact = {k: v for k, v in contact.items() if (v and v != 'null')}
    created_contact_id = dest_infusionsoft.ContactService('add', contact)
    print("Contact created!  Contact ID:"
          " {} - {} {}".format(created_contact_id,
                               contact.get('FirstName'),
                               contact.get('LastName')))

# TODO
# Determine which tags need to be created (based on contacts imported)
# Create tags from above determination
# Apply tags to contacts
tags = get_table(src_infusionsoft, 'ContactGroupAssign')