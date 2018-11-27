import csv
from infusionsoft import InfusionsoftOAuth
from pprint import pprint
import requests

from constants import CF_FORM_ID, REGIONS
from database.utils import get_app_and_token


url = 'https://api.infusionsoft.com/crm/rest/v1'

fieldnames = ['Id', 'ObjectType', 'Error']


def adt():
    src_app, src_token = get_app_and_token('Source Application')
    dest_app, dest_token = get_app_and_token('Destination Application')

    src_headers = {'Authorization': 'Bearer ' + src_token}
    dest_headers = {'Authorization': 'Bearer ' + dest_token}

    # Create errors file
    with open('errors.csv', 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

    # Transfer Companies
    create_xmlrpc_id_custom_field(
        'Source App Account ID',
        'Company',
        dest_token
    )
    company_rel = transfer_companies(src_headers, dest_headers)

    # Transfer Contact Custom Fields
    cf_rel = transfer_custom_fields(src_headers, dest_headers)

    # Transfer Contacts
    create_rest_id_custom_field('Source App Contact ID', dest_headers)
    create_rest_id_custom_field('Source App Company ID', dest_headers)
    contact_rel = transfer_contacts(
        src_headers,
        dest_headers,
        company_rel,
        cf_rel,
    )

    # Transfer tags
    transfer_tags(src_headers, dest_headers, contact_rel)

    # TODO Transfer notes

    # TODO Transfer tasks


def create_rest_id_custom_field(fieldname, headers):
    ext = '/contacts/model'
    resp = requests.get(url+ext, headers=headers)
    labels = [cf.get('label') for cf in resp.json().get('custom_fields')]
    if fieldname not in labels:
        cf = {
            'field_type': 'Text',
            'label': fieldname
        }
        ext = '/contacts/model/customFields'
        resp = requests.post(url+ext, headers=headers, json=cf)
        cf_name = resp.json().get('label')
        print(f'Custom Field "{cf_name}" created.')


def create_xmlrpc_id_custom_field(fieldname, tablename, token):
    ifs = InfusionsoftOAuth(token)
    custom_field = ifs.DataService(
        'query',
        'DataFormField',
        1000,
        0,
        {'FormId': CF_FORM_ID.get(tablename),
         'Label': fieldname},
        ['Label']
    )
    if custom_field:
        return custom_field[0].get('Label')
    while True:
        tabs = ifs.DataService(
            'query',
            'DataFormTab',
            1000,
            0,
            {'FormId': CF_FORM_ID.get(tablename)},
            ['Id', 'TabName']
        )
        if tabs:
            break
        input(f'Create a tab and header for {tablename}, then hit Enter')
    tab_id = min([tab.get('Id') for tab in tabs])
    while True:
        groups = ifs.DataService(
            'query',
            'DataFormGroup',
            1000,
            0,
            {'TabId': tab_id},
            ['Id']
        )
        if groups:
            break
        input(f'Create a header for {tablename}, then hit Enter')
    group_id = min([group.get('Id') for group in groups])
    custom_field = ifs.DataService(
        'addCustomField',
        tablename,
        fieldname,
        'Text',
        group_id
    )
    print(f'Custom Field "{fieldname}" created.')


def transfer_companies(src_headers, dest_headers):
    # Companies are transferred first, so that IDs can be generated to connect
    # contacts to them

    # Prepare data for urls
    ext = '/companies/model'
    resp = requests.get(url+ext, headers=dest_headers)
    company_props = resp.json().get('optional_properties')
    custom_fields = resp.json().get('custom_fields')
    for cf in custom_fields:
        if cf.get('label') == 'Source App Account ID':
            company_cf_id = cf.get('id')
    ext = '/companies'
    props = 'optional_properties=' + ','.join(company_props)

    # Get existing company IDs
    next_url = None
    existing_ids = {}
    while True:
        if not next_url:
            resp = requests.get(url+ext+'?'+props, headers=dest_headers)
        else:
            resp = requests.get(next_url+'&'+props, headers=dest_headers)
        next_url = resp.json().get('next')
        companies = resp.json().get('companies')
        if not companies:
            break
        for company in companies:
            company_cfs = company.get('custom_fields')
            for cf in company_cfs:
                if cf.get('id') == company_cf_id and cf.get('content'):
                    existing_ids[int(cf.get('content'))] = company.get('id')

    # Transfer companies
    next_url = None
    extra_fields = ('email_opted_in', 'email_status', 'id')
    opt_in_reason = 'Contacts transferred from Free Trial'
    while True:
        if not next_url:
            resp = requests.get(url+ext+'?'+props, headers=src_headers)
        else:
            resp = requests.get(next_url+'&'+props, headers=src_headers)
        next_url = resp.json().get('next')
        companies = resp.json().get('companies')
        if not companies:
            break
        for company in companies:
            if company.get('id') in existing_ids:
                continue
            custom_fields = [{
                'content': company.get('id'),
                'id': company_cf_id,
            }]
            address = company.get('address')
            if address.get('region') and len(address.get('region')) == 2:
                address['region'] = REGIONS.get(address['region'], None)
            company['custom_fields'] = custom_fields
            company['opt_in_reason'] = opt_in_reason
            for field in extra_fields:
                company.pop(field, None)
            resp = requests.post(url+ext, headers=dest_headers, json=company)
            if resp.status_code == 201:
                company_id = resp.json().get('id')
                existing_ids[company.get('id')] = company_id
                print(f'Company ID {company_id} created.')
    return existing_ids


def transfer_custom_fields(src_headers, dest_headers):
    ext = '/contacts/model'

    # Get existing custom fields
    resp = requests.get(url+ext, headers=src_headers)
    src_custom_fields = resp.json().get('custom_fields')
    src_cf_d = {cf.get('label'): cf.get('id') for cf in src_custom_fields}

    # Get custom fields that have already been created
    resp = requests.get(url+ext, headers=dest_headers)
    dest_custom_fields = resp.json().get('custom_fields')
    dest_cf_labels = []
    cf_rel = {}
    for cf in dest_custom_fields:
        dest_cf_labels.append(cf.get('label'))
        src_cf_id = src_cf_d.get(cf.get('label'))
        if src_cf_id:
            cf_rel[src_cf_id] = cf.get('id')

    # Create custom fields in dest app
    ext = '/contacts/model/customFields'
    for cf in src_custom_fields:

        # Skip creating custom field if exists
        if cf.get('label') in dest_cf_labels:
            continue

        # Remove unnecessary keys from cf dictionary
        src_cf_id = cf.pop('id', None)
        cf.pop('record_type', None)
        options = cf.get('options')
        for option in options:
            option.pop('id', None)
            if 'options' in option.keys() and option.get('options'):
                for op in option.get('options'):
                    op.pop('id', None)

        # Replace options list with modified version without unnecesary fields
        cf['options'] = options

        # Create custom field and print result.
        resp = requests.post(url+ext, headers=dest_headers, json=cf)
        r_json = resp.json()
        cf_name = r_json.get('label')
        cf_id = r_json.get('id')
        cf_rel[src_cf_id] = cf_id
        print(f'Custom field "{cf_name}" created.')
    return cf_rel


def transfer_contacts(src_headers, dest_headers, company_rel, cf_rel):
    src_token = get_token_from_header(src_headers)
    dest_token = get_token_from_header(dest_headers)
    dest = InfusionsoftOAuth(dest_token)

    # Get custom fields
    ext = '/contacts/model'
    resp = requests.get(url+ext, headers=dest_headers)
    custom_fields = resp.json().get('custom_fields')
    for cf in custom_fields:
        if cf.get('label') == 'Source App Contact ID':
            contact_cf_id = cf.get('id')
        if cf.get('label') == 'Source App Company ID':
            company_cf_id = cf.get('id')
    optional_properties = resp.json().get('optional_properties')

    # Get user relationship
    ext = '/users'
    props = 'include_inactive=FALSE'
    resp = requests.get(url+ext+'?'+props, headers=src_headers)
    src_users = resp.json().get('users')
    resp = requests.get(url+ext+'?'+props, headers=dest_headers)
    dest_users = resp.json().get('users')
    user_rel = {}
    for s_user in src_users:
        for d_user in dest_users:
            if s_user.get('global_user_id') == d_user.get('global_user_id'):
                user_rel[s_user.get('id')] = d_user.get('id')

    # Begin contact handling
    ext = '/contacts'
    props = 'optional_properties=' + ','.join(optional_properties)

    # Get existing contact IDs
    next_url = None
    existing_ids = {}
    while True:
        if not next_url:
            resp = requests.get(url+ext+'?'+props, headers=dest_headers)
        else:
            resp = requests.get(next_url+'&'+props, headers=dest_headers)
        next_url = resp.json().get('next')
        contacts = resp.json().get('contacts')
        if not contacts:
            break
        for contact in contacts:
            contact_cfs = contact.get('custom_fields')
            for cf in contact_cfs:
                if cf.get('id') == contact_cf_id and cf.get('content'):
                    existing_ids[int(cf.get('content'))] = contact.get('id')

    # Transfer contacts
    next_url = None
    errors = {}
    lead_source_rel = {}
    extra_fields = ('tag_ids', 'relationships', )
    opt_in_reason = 'Contacts transferred from Free Trial'
    src_contact_types = set()
    src_prefixes = set()
    src_suffixes = set()
    while True:
        # Handle pagination
        if not next_url:
            resp = requests.get(url+ext+'?'+props, headers=src_headers)
        else:
            resp = requests.get(next_url+'&'+props, headers=src_headers)
        next_url = resp.json().get('next')
        contacts = resp.json().get('contacts')
        if not contacts:
            break
        for contact in contacts:
            if contact.get('id') in existing_ids:
                continue

            # Handle Custom Fields
            custom_fields = contact.get('custom_fields')
            new_cfs = []
            for cf in custom_fields:
                cf['id'] = cf_rel.get(cf['id'], 0)
                new_cfs.append(cf)
            new_cfs.append({'id': contact_cf_id, 'content': contact.get('id')})
            if contact.get('company'):
                company_id = contact.get('company').get('id')
                new_cfs.append({
                    'id': company_cf_id,
                    'content': company_id
                })
                contact['company'] = {'id': company_rel[company_id]}
            contact['custom_fields'] = new_cfs

            # Handle Addresses
            addresses = contact.get('addresses')
            new_addresses = []
            for address in addresses:
                if address.get('region') and len(address.get('region')) == 2:
                    address['region'] = REGIONS.get(address['region'], None)
                new_addresses.append(address)
            contact['addresses'] = new_addresses

            # Handle Prefix
            prefix = contact.get('prefix')
            if prefix == 'null':
                contact['prefix'] = None
            if contact.get('prefix'):
                src_prefixes.add(contact['prefix'])

            # Handle Suffix
            suffix = contact.get('suffix')
            if suffix == 'null':
                contact['suffix'] = None
            if contact.get('suffix'):
                src_suffixes = contact['suffix']

            # Handle Contact Type
            contact_type = contact.get('contact_type')
            if contact_type == 'null':
                contact['contact_type'] = None
            if contact.get('contact_type'):
                src_contact_types.add(contact['contact_type'])

            # Handle Website
            website = contact.get('website')
            if website and website[0:4] != 'http':
                website = 'http://' + website
                contact['website'] = website

            # Handle Lead Source
            lead_source_id = contact.get('lead_source_id')
            if lead_source_id:
                if not lead_source_rel.get(lead_source_id):
                    lead_source_rel[lead_source_id] = get_lead_source_by_id(
                        lead_source_id,
                        src_token,
                        dest_token,
                    )
                contact['lead_source_id'] = lead_source_rel[lead_source_id]

            # Handle Owner
            owner_id = contact.get('owner_id')
            if owner_id:
                contact['owner_id'] = user_rel.get(owner_id, 0)

            # Add Opt In
            contact['opt_in_reason'] = opt_in_reason

            # Remove unnecessary fields
            for field in extra_fields:
                contact.pop(field, None)

            # Transfer Contact
            resp = requests.post(url+ext, headers=dest_headers, json=contact)

            # Detect success
            if resp.status_code == 201:
                contact_id = resp.json().get('id')
                existing_ids[contact.get('id')] = contact_id
                print(f'Contact ID {contact_id} created.')
            else:
                message = resp.json().get('message')
                with open('errors.csv', 'a', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames)

                    for error in message.split(', '):
                        data = {
                            'Id': contact.get('id'),
                            'ObjectType': 'Contact',
                            'Error': error
                        }
                        writer.writerow(data)
                        errors[error] = errors.get(error, [])
                        errors[error].append(contact.get('id'))
    if 'Contact Type is invalid' in errors:
        ext = '/setting/contact/optionTypes'
        resp = requests.get(url+ext, headers=dest_headers)
        dest_contact_types = set(resp.json().get('value').split(','))
        new_contact_types = src_contact_types - dest_contact_types
        print('Please create the following Contact Types:\n')
        print('\n'.join(new_contact_types))
        input('\nPress Enter when complete')
    if 'Prefix is invalid' in errors:
        dest_prefixes = set(dest.DataService(
            'getAppSetting',
            'Contact',
            'optiontitles'
        ).split(','))
        new_prefixes = src_prefixes - dest_prefixes
        print('Please create the following Titles:\n')
        print('\n'.join(new_prefixes))
        input('\nPress Enter when complete')
    if 'Suffix is invalid' in errors:
        dest_suffixes = set(dest.DataService(
            'getAppSetting',
            'Contact',
            'optionsuffixes'
        ).split(','))
        new_suffixes = src_suffixes - dest_suffixes
        print('Please create the following Suffixes:\n')
        print('\n'.join(new_suffixes))
        input('\nPress Enter when complete')
    return existing_ids


def transfer_tags(src_headers, dest_headers, contact_rel):
    # Get existing tags
    ext = '/tags'
    next_url = ''
    dest_tags = {}
    while True:
        if not next_url:
            resp = requests.get(url+ext, headers=dest_headers)
        else:
            resp = requests.get(next_url, headers=dest_headers)
        next_url = resp.json().get('next')
        tags = resp.json().get('tags')
        if not tags:
            break
        for tag in tags:
            tag_name = get_tag_full_name(tag)
            dest_tags[tag_name] = tag.get('id')

    # Get existing tag categories
    dest_token = get_token_from_header(dest_headers)
    dest = InfusionsoftOAuth(dest_token)
    cats = dest.DataService(
        'query',
        'ContactGroupCategory',
        1000,
        0,
        {},
        ['Id', 'CategoryName']
    )
    dest_cats = {cat.get('CategoryName'): cat.get('Id') for cat in cats}

    # Create Tags
    next_url = ''
    tag_rel = {}
    while True:
        if not next_url:
            resp = requests.get(url+ext, headers=src_headers)
        else:
            resp = requests.get(next_url, headers=src_headers)

        next_url = resp.json().get('next')
        tags = resp.json().get('tags')
        if not tags:
            break

        for tag in tags:
            # Check if tag exists
            tag_full_name = get_tag_full_name(tag)
            if tag_full_name in dest_tags:
                tag_rel[tag.get('id')] = dest_tags.get(tag_full_name)
                continue

            # Check if tag category exists
            if tag.get('category'):
                category_name = tag['category'].get('name')
                if not dest_cats.get(category_name):
                    ext = '/tags/categories'
                    data = {'name': category_name}
                    resp = requests.post(
                        url+ext,
                        headers=dest_headers,
                        json=data
                    )
                    pprint(resp.json())
                    dest_cats[category_name] = resp.json().get('id')
                category = {
                    'id': dest_cats.get(category_name)
                }
                tag['category'] = category

            # Create tag
            src_tag_id = tag.pop('id', None)
            ext = '/tags'
            resp = requests.post(url+ext, headers=dest_headers, json=tag)
            tag_rel[src_tag_id] = resp.json().get('id')
            print(f'Tag ID {resp.json().get("id")} created.')

    # Tag Contacts
    for src_tag, dest_tag in tag_rel.items():
        # Get list of tagged contacts
        ext = f'/tags/{src_tag}/contacts'
        next_url = ''
        contact_ids = []
        while True:
            if not next_url:
                resp = requests.get(url+ext, headers=src_headers)
            else:
                resp = requests.get(next_url, headers=src_headers)
            next_url = resp.json().get('next')
            contacts = resp.json().get('contacts')
            if not contacts:
                break

            for contact in contacts:
                contact_id = contact.get('contact').get('id')
                dest_contact_id = contact_rel.get(contact_id)
                if dest_contact_id:
                    contact_ids.append(dest_contact_id)

        if contact_ids:
            ext = f'/tags/{dest_tag}/contacts'

            # Split call into 100s if more than 100 contacts need the tag
            if len(contact_ids) > 100:
                start = 0
                end = 100
                while True:
                    ids = contact_ids[start:end]
                    if not ids:
                        break
                    data = {'ids': ids}
                    resp = requests.post(
                        url+ext,
                        headers=dest_headers,
                        json=data
                    )
                    start += 100
                    end += 100
            else:
                data = {'ids': contact_ids}
                resp = requests.post(url+ext, headers=dest_headers, json=data)
            print(f'Tag ID {dest_tag} applied to {len(contact_ids)} contacts')


def get_token_from_header(headers):
    auth = headers.get('Authorization')
    return auth.split()[1]


def get_lead_source_by_id(lead_source_id, src_token, dest_token):
    src = InfusionsoftOAuth(src_token)
    dest = InfusionsoftOAuth(dest_token)

    src_lead_source = src.DataService(
        'query',
        'LeadSource',
        1000,
        0,
        {'Id': lead_source_id},
        ['Id', 'Name', 'LeadSourceCategoryId']
    )[0]
    src_name = src_lead_source.get('Name')
    dest_lead_source = dest.DataService(
        'query',
        'LeadSource',
        1000,
        0,
        {'Name': src_name},
        ['Id', 'Name', 'LeadSourceCategoryId']
    )
    if dest_lead_source:
        return dest_lead_source[0].get('Id')
    else:
        return dest.DataService(
            'add',
            'LeadSource',
            {'Name': src_name}
        )


def get_tag_full_name(tag):
    category = ''
    if tag.get('category'):
        category = tag['category'].get('name') + ' -> '
    tag_name = category + tag.get('name')
    return tag_name


if __name__ == '__main__':
    src_app, src_token = get_app_and_token('Source Application')
    dest_app, dest_token = get_app_and_token('Destination Application')
    src_headers = {'Authorization': 'Bearer ' + src_token}
    dest_headers = {'Authorization': 'Bearer ' + dest_token}
    ext = '/appointments'
    props = 'contact_id=4515'
    resp = requests.get(url+ext+'?'+props, headers=src_headers)
    pprint(resp.json())
