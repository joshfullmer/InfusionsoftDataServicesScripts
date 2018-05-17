"""
This application will transfer all data from a free trial app to a paid app.
It will automatically transfer Contacts, Tags, and Actions(Tasks, Notes, Appts)

"""
from infusionsoft.library import Infusionsoft

from constants import FIELDS, DATATYPES
# from constants import QJ154_APIKEY, TE361_APIKEY
from infusionsoft_actions import get_table, create_custom_field

SOURCE_APPNAME = 'nj459'  # 'qj154'
SOURCE_API_KEY = '4d3cc8d6c77537a76590859e4faf5e12'  # QJ154_APIKEY
DESTINATION_APPNAME = 'ws466'  # 'te361'
DESTINATION_API_KEY = '8b7001675c41c7602677f9473d8c24e3'  # Groovy1!

CONTACTS_WITH_TAG_IDS = []

# Initialize
src_infusionsoft = Infusionsoft(SOURCE_APPNAME, SOURCE_API_KEY)
dest_infusionsoft = Infusionsoft(DESTINATION_APPNAME, DESTINATION_API_KEY)

src_contact_id = create_custom_field(dest_infusionsoft,
                                     'Source App Contact ID')['Name']

# CONTACTS
# =============================================================================

# Create custom fields
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
                                    {'Values': custom_field.get('Values')})

        rename_mapping["_" + custom_field['Name']] = field['Name']

# Get list of contacts by provided ID number
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

# Transfer contacts
num_contacts_created = 0
contact_relationship = {}
contacts = get_table(src_infusionsoft, 'Contact', query, contact_fields)
for contact in contacts:
    if existing_contacts.get(int(contact['Id'])):
        print("Contact already exists: Contact ID {}".format(
            existing_contacts[contact['Id']]))
        contact_relationship[contact['Id']] = existing_contacts[contact['Id']]
        continue
    if contact['Id'] == contact['CompanyID']:
        print("The contact is a company (ID: {})... skipping".format(
            contact['CompanyID']))
        continue
    for key in contact_fields:
        if rename_mapping.get(key):
            contact[rename_mapping[key]] = contact.pop(key, None)
    contact['CompanyId'] = 0
    contact[src_contact_id] = str(contact['Id'])
    contact = {k: v for k, v in contact.items() if (v and v != 'null')}
    created_contact_id = dest_infusionsoft.ContactService('add', contact)
    contact_relationship[contact['Id']] = created_contact_id
    print("Contact created!  Contact ID:"
          " {} - {} {}".format(created_contact_id,
                               contact.get('FirstName', ''),
                               contact.get('LastName', '')))
    if contact.get('Email'):
        dest_infusionsoft.APIEmailService(
            'optIn',
            contact.get('Email'),
            'Transfer from Free Trial App')
    num_contacts_created += 1

# TAGS
# =============================================================================

# Get tags and tag categories to transfer
tags_applied = get_table(src_infusionsoft, 'ContactGroupAssign')
tags_to_create = []
for tag in tags_applied:
    if tag['GroupId'] not in tags_to_create:
        tags_to_create += [tag['GroupId']]

tags = get_table(src_infusionsoft, 'ContactGroup')
tag_categories = get_table(src_infusionsoft, 'ContactGroupCategory')

existing_tag_categories = {}
for tag_cat in get_table(dest_infusionsoft, 'ContactGroupCategory'):
    existing_tag_categories[tag_cat['CategoryName']] = tag_cat['Id']

existing_tags = {}
for tag in get_table(dest_infusionsoft, 'ContactGroup'):
    existing_tags[tag['GroupName']] = {'Id': tag['Id'],
                                       'GroupCategoryId': tag.get(
                                           'GroupCategoryId')}

# Create tag categories
num_categories_created = 0
category_relationship = {}
for tag_cat in tag_categories:
    if existing_tag_categories.get(tag_cat['CategoryName']):
        category_relationship[tag_cat['Id']] = existing_tag_categories[
            tag_cat['CategoryName']
        ]
        print("Category exists: {}".format(tag_cat['CategoryName']))
    else:
        category_relationship[tag_cat['Id']] = dest_infusionsoft.DataService(
            'add',
            'ContactGroupCategory',
            tag_cat
        )
        print("Need to make category: {}".format(tag_cat['CategoryName']))
        print("Created category ID: {}".format(
            category_relationship[tag_cat['Id']]))
        num_categories_created += 1

# Create tags
num_tags_created = 0
tag_relationship = {}
for tag in tags:
    if tag['Id'] not in tags_to_create:
        continue
    existing_tag = existing_tags.get(tag['GroupName'])
    if existing_tag:
        old_cat_match = category_relationship.get(tag['GroupCategoryId'])
        if not old_cat_match:
            old_cat_match = 0
        existing_cat = existing_tag.get('GroupCategoryId')
        if old_cat_match == existing_cat:
            tag_relationship[tag['Id']] = existing_tag['Id']
            print("Tag \"{}\" already exists: ID {}".format(tag['GroupName'],
                  existing_tag['Id']))
            continue
    if category_relationship.get(tag['GroupCategoryId']):
        tag['GroupCategoryId'] = category_relationship[tag['GroupCategoryId']]
    else:
        tag['GroupCategoryId'] = 0
    tag_id = dest_infusionsoft.DataService('add',
                                           'ContactGroup',
                                           tag)
    print("Tag \"{}\" created: ID {}".format(tag['GroupName'], tag_id))
    tag_relationship[tag['Id']] = tag_id
    num_tags_created += 1

# Get tag applications
existing_tag_apps = {}
for tag_app in get_table(dest_infusionsoft, "ContactGroupAssign"):
    if not existing_tag_apps.get(tag_app['ContactId']):
        existing_tag_apps[tag_app['ContactId']] = []
    existing_tag_apps[tag_app['ContactId']] += [tag_app['GroupId']]

# Transfer tag applications
num_tags_applied = 0
for tag_app in tags_applied:
    contact_id = contact_relationship.get(tag_app['ContactId'])
    if not contact_id:
        print("Contact ID {} doesn't exist.".format(tag_app['ContactId']))
        continue
    tag_id = tag_relationship[tag_app['GroupId']]
    if ((existing_tag_apps) and
            (tag_id in existing_tag_apps.get(contact_id, []))):
        print("Tag ID {} already applied.".format(tag_id))
        continue
    dest_infusionsoft.ContactService('addToGroup',
                                     contact_id,
                                     tag_id)
    print("Tag ID {} applied to Contact ID {}".format(tag_id, contact_id))
    num_tags_applied += 1

# CONTACT ACTIONS
# =============================================================================

# Get actions to transfer
src_action_id = create_custom_field(dest_infusionsoft,
                                    'Source App Action ID',
                                    tablename='ContactAction')['Name']

existing_actions = []
for action in get_table(dest_infusionsoft,
                        'ContactAction',
                        query={src_action_id: '_%'},
                        fields=['Id', src_action_id]):
    existing_actions += [int(action[src_action_id])]

user_id = get_table(dest_infusionsoft, 'User')[0]['Id']

# Create actions
num_actions_created = 0
for action in get_table(src_infusionsoft, 'ContactAction'):
    if action['Id'] in existing_actions:
        print("ContactAction {} already exists.".format(action['Id']))
        continue
    action['UserId'] = user_id
    if not contact_relationship.get(action['ContactId']):
        print("Contact ID {} doesn't exist".format(action['ContactId']))
        continue
    action['ContactId'] = contact_relationship[action['ContactId']]
    action[src_action_id] = str(action['Id'])
    action_id = dest_infusionsoft.DataService('add',
                                              'ContactAction',
                                              action)
    print("ContactAction ID {} created.".format(action_id))
    num_actions_created += 1

# PRODUCTS
# =============================================================================

existing_products = []
for product in get_table(dest_infusionsoft,
                         'Product',
                         query={'ProductName': '_%'},
                         fields=['ProductName']):
    existing_products += [product.get('ProductName')]

num_products_created = 0

for product in get_table(src_infusionsoft, 'Product'):
    if product.get('ProductName') in existing_products:
        print("Product \"{}\" exists.".format(product.get('ProductName')))
        continue
    product_id = dest_infusionsoft.DataService('add',
                                               'Product',
                                               product)
    print("Product ID {} created.".format(product_id))
    num_products_created += 1

# Report on data transferred
print("Data successfully transferred from {} to {}".format(
    SOURCE_APPNAME, DESTINATION_APPNAME
))
print("Number of contacts transferred: {}".format(num_contacts_created))
print("Number of tags created: {}".format(num_tags_created))
print("Number of tag categories created: {}".format(num_categories_created))
print("Number of tags applied: {}".format(num_tags_applied))
print("Number of contact actions created: {}".format(num_actions_created))
print("Number of products created: {}".format(num_products_created))
print("Number of campaigns transferred: ")
