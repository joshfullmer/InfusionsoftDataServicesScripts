from services.exceptions import InfusionsoftAPIError
from services.constants import DATATYPES, FIELDS
from services.custom_fields import create_custom_field
from services.tables import get_table


def begin(source, destination):
    """Handles the automatic transfer of data from one app to another through
    the Infusionsoft API"""

    contact_relationship = transfer_contacts(source, destination)

    print(len(contact_relationship))


def transfer_contacts(source, destination):
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
                f'InfusionsoftAPIError: Error adding contact: {contact_id}')

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
                    f'InfusionsoftAPIError: {optin_success[1]}')
        contact_count += 1

    return contact_mapping
