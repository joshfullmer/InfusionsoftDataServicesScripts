from services.exceptions import InfusionsoftAPIError
from services.constants import DATATYPES, FIELDS
from services.custom_fields import create_custom_field
from services.tables import get_table


def begin(source, destination):
    """Handles the automatic transfer of data from one app to another through
    the Infusionsoft API"""

    contact_mapping, contact_count = transfer_contacts(source, destination)
    tag_mapping, tag_count, category_count = transfer_tags(source, destination)
    tag_apply_count = apply_tags(
        source,
        destination,
        contact_mapping,
        tag_mapping)
    action_count = transfer_actions(source, destination, contact_mapping)
    product_count = transfer_products(source, destination)
    return {
        'contacts': contact_count,
        'tags': tag_count,
        'tag_categories': category_count,
        'tag_apps': tag_apply_count,
        'contact_actions': action_count,
        'products': product_count}


def transfer_contacts(source, destination):

    # Create custom field to store contact ID
    src_contact_cf = create_custom_field(
        destination,
        'Source App Contact ID')['Name']

    # Create contact custom fields and add created fields to list of contact
    # query fields
    contact_fields = FIELDS['Contact'][:]
    custom_fields = get_table(source, 'DataFormField', {'FormId': -1})
    field_mapping = {}
    for cf in custom_fields:
        if cf['DataType'] == 23:
            continue

        field = create_custom_field(
            destination,
            cf['Label'],
            'Contact',
            DATATYPES[cf['DataType']],
            {'Values': cf.get('Values')})

        contact_fields.append(f'_{cf["Name"]}')
        field_mapping[f'_{cf["Name"]}'] = field['Name']

    # Get existing contacts so as not to create duplicates
    existing_contacts = {}
    existing_contact_list = get_table(
        destination,
        'Contact',
        {src_contact_cf: '_%'},
        ['Id', src_contact_cf])
    for contact_id in existing_contact_list:
        existing_contacts[int(contact_id[src_contact_cf])] = contact_id['Id']

    # Transfer contacts
    contact_count = 0
    contact_mapping = {}
    contacts = get_table(source, 'Contact', fields=contact_fields)
    for contact in contacts:

        # Check if contact needs to be transferred
        if existing_contacts.get(contact['Id']):
            contact_mapping[contact['Id']] = existing_contacts[contact['Id']]
            continue
        if contact['Id'] == contact['CompanyID']:
            continue

        # Handle field mapping for custom fields
        for key in contact_fields:
            if field_mapping.get(key):
                contact[field_mapping[key]] = contact.pop(key, None)

        # Clean up some field values
        contact['CompanyID'] = 0
        contact[src_contact_cf] = str(contact['Id'])
        contact = {k: v for k, v in contact.items() if (v and v != 'null')}

        # Create contact
        contact_id = destination.ContactService('add', contact)
        if isinstance(contact_id, tuple):
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: Error adding contact: {contact_id[1]}')

        # Map old contact to new
        contact_mapping[contact['Id']] = contact_id

        # Opt in transferred contacts
        if contact.get('Email'):
            optin_success = destination.APIEmailService(
                'optIn',
                contact.get('Email'),
                'Transfer from Free Trial App')
            if isinstance(optin_success, tuple):
                raise InfusionsoftAPIError(
                    f'InfusionsoftAPIError: could not optin contact:'
                    f'{optin_success[1]}')
        contact_count += 1

    return contact_mapping, contact_count


def transfer_tags(source, destination):

    ########################################################
    # Create tags in the destination app if they don't exist
    ########################################################

    # Get tags and tag categories to transfer
    tags_applied = get_table(source, 'ContactGroupAssign')
    tags_to_create = list({tag['GroupId'] for tag in tags_applied})

    tags = get_table(source, 'ContactGroup')
    tag_categories = get_table(source, 'ContactGroupCategory')

    existing_tag_categories = {}
    for tag_cat in get_table(destination, 'ContactGroupCategory'):
        existing_tag_categories[tag_cat['CategoryName']] = tag_cat['Id']

    existing_tags = {}
    for tag in get_table(destination, 'ContactGroup'):
        existing_tags[tag['GroupName']] = {'Id': tag['Id'],
                                           'GroupCategoryId': tag.get(
                                               'GroupCategoryId')}

    # Create tag categories
    category_count = 0
    category_mapping = {}
    for tag_cat in tag_categories:

        # Check if category exists
        # If it does, add it to the mapping. Else create it.
        if existing_tag_categories.get(tag_cat['CategoryName']):
            category_mapping[tag_cat['Id']] = existing_tag_categories[
                tag_cat['CategoryName']]
        else:
            created_category = destination.DataService(
                'add',
                'ContactGroupCategory',
                tag_cat)
            if isinstance(created_category, tuple):
                raise InfusionsoftAPIError(
                    'InfusionsoftAPIError: tag category could not be created: '
                    f'{created_category[1]}')
            category_mapping[tag_cat['Id']] = created_category
            category_count += 1

    # Create tags in destination app
    tag_count = 0
    tag_mapping = {}
    for tag in tags:

        # Check if tag is applied to contacts
        if tag['Id'] not in tags_to_create:
            continue

        # Check if tag exists in destination on same category
        existing_tag = existing_tags.get(tag['GroupName'])
        if existing_tag:
            category_match = category_mapping.get(tag['GroupCategoryId'])
            if not category_match:
                category_match = 0
            existing_cat = existing_tag.get('GroupCategoryId')
            if category_match == existing_cat:
                tag_mapping[tag['Id']] = existing_tag['Id']
                continue

        # Get new category ID from category mapping
        if category_mapping.get(tag['GroupCategoryId']):
            tag['GroupCategoryId'] = category_mapping[tag['GroupCategoryId']]
        else:
            tag['GroupCategoryId'] = 0

        # Create tag
        tag_id = destination.DataService(
            'add',
            'ContactGroup',
            tag)
        if isinstance(tag, tuple):
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: '
                f'tag can not be created: {tag_id[1]}')
        tag_mapping[tag['Id']] = tag_id
        tag_count += 1

    return tag_mapping, tag_count, category_count


def apply_tags(source, destination, contact_mapping, tag_mapping):

    ###############################################################
    # Applies tags to contacts if they haven't already been applied
    ###############################################################

    # Get existing tag applications
    existing_tag_apps = {}
    for tag_app in get_table(destination, 'ContactGroupAssign'):
        if not existing_tag_apps.get(tag_app['ContactId']):
            existing_tag_apps[tag_app['ContactId']] = []
        existing_tag_apps[tag_app['ContactId']].append(tag_app['GroupId'])

    # Apply tags if they haven't already been applied
    num_tags_applied = 0
    for tag_app in get_table(source, 'ContactGroupAssign'):
        contact_id = contact_mapping.get(tag_app['ContactId'])
        if not contact_id:
            continue
        tag_id = tag_mapping[tag_app['GroupId']]
        if ((existing_tag_apps) and
                (tag_id in existing_tag_apps.get(contact_id, []))):
            continue

        created_tag = destination.ContactService(
            'addToGroup',
            contact_id,
            tag_id)
        if isinstance(created_tag, tuple):
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: '
                f'tag could not be applied: {created_tag[1]}')
        num_tags_applied += 1

    return num_tags_applied


def transfer_actions(source, destination, contact_mapping):

    ############################################################
    # Transfers contact actions (tasks, notes, and appointments)
    ############################################################

    src_action_cf = create_custom_field(
        destination,
        'Source App Action ID',
        'ContactAction')['Name']

    dest_actions = get_table(
        destination,
        'ContactAction',
        {src_action_cf: '_%'},
        ['Id', src_action_cf])
    existing_actions = [int(action[src_action_cf]) for action in dest_actions]

    user_id = get_table(destination, 'User')[0]['Id']

    action_count = 0
    for action in get_table(source, 'ContactAction'):
        if action['Id'] in existing_actions:
            continue
        if not contact_mapping.get(action['ContactId']):
            continue
        action['UserID'] = user_id
        action['ContactId'] = contact_mapping[action['ContactId']]
        action[src_action_cf] = str(action['Id'])
        action_id = destination.DataService(
            'add',
            'ContactAction',
            action)
        if isinstance(action_id, tuple):
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError: '
                f'contact action could not be created: {action_id[1]}')
        action_count += 1

    return action_count


def transfer_products(source, destination):

    #########################################################
    # Transfer all products that don't exist by the same name
    #########################################################

    dest_products = get_table(
        destination,
        'Product',
        {'ProductName': '_%'},
        ['ProductName'])
    existing_products = [prod.get('ProductName') for prod in dest_products]

    product_count = 0
    for product in get_table(source, 'Product'):
        if product.get('ProductName') in existing_products:
            continue
        product_id = destination.DataService(
            'add',
            'Product',
            product)
        if isinstance(product_id, tuple):
            raise InfusionsoftAPIError(
                f'InfusionsoftAPIError:'
                f' product could not be created: {product_id[1]}')
        product_count += 1

    return product_count
