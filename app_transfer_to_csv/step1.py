"""
Step 1 generates up to 4 CSVs:
- contacts.csv
- companies.csv
- tags.csv
- email_opt_outs.csv

Step 1 will also create contact custom fields.
"""

import csv
import glob
import json
import os
import re
import zipfile

from infusionsoft.library import Infusionsoft

import config
from constants import FIELDS, DATATYPES, OPT_OUT_STATUSES
from tools import convert_dict_dates_to_string
from infusionsoft_actions import get_table, create_custom_field

dir_path = "output/{} -- {}/".format(config.SOURCE_APPNAME,
                                     config.DESTINATION_APPNAME)
os.makedirs(dir_path, exist_ok=True)

src_infusionsoft = Infusionsoft(config.SOURCE_APPNAME, config.SOURCE_API_KEY)
dest_infusionsoft = Infusionsoft(config.DESTINATION_APPNAME,
                                 config.DESTINATION_API_KEY)

# CONTACTS
# =============================================================================
if config.CONTACTS:
    # Create Source App Contact ID custom field
    src_contact_id = create_custom_field(dest_infusionsoft,
                                         'Source App Contact ID')['Name']
    if config.COMPANIES:
        src_company_id = create_custom_field(dest_infusionsoft,
                                             'Source App Company ID')['Name']

    # Generates full list of contact fields, including custom fields
    contact_fields = FIELDS['Contact'][:]
    custom_fields = get_table(src_infusionsoft, 'DataFormField')
    for custom_field in custom_fields:
        if custom_field['FormId'] == -1 and custom_field['DataType'] != 23:
            contact_fields += ["_{}".format(custom_field['Name'])]

    # Generates query criteria if there are tags to limit the transfer
    contact_ids = []
    if config.CONTACTS_WITH_TAG_IDS:
        for tag in get_table(src_infusionsoft,
                             'ContactGroupAssign',
                             {},
                             ['ContactId', 'GroupId']):
            if tag['GroupId'] in config.CONTACTS_WITH_TAG_IDS:
                contact_ids += [tag['ContactId']]
        contact_ids = set(contact_ids)

    # Gets Source Contacts
    print(contact_fields)
    all_contacts = get_table(src_infusionsoft, 'Contact', {}, contact_fields)
    contacts = []
    for contact in all_contacts:
        if contact.get('Id') in contact_ids:
            contacts.append(contact)

    # Limit the custom fields to create to only those fields that have data
    fields_with_data = set().union(*(contact.keys() for contact in contacts))
    regex = re.compile(r'_')
    cfs_to_import = [cf for cf in fields_with_data if regex.match(cf)]

    # Create custom fields
    rename_mapping = {}
    for custom_field in custom_fields:

        # Make sure the field is a contact field and not a drilldown
        if custom_field['FormId'] == -1 and custom_field['DataType'] != 23:
            if config.CREATE_CUSTOM_FIELDS:
                if ("_" + custom_field['Name']) not in cfs_to_import:
                    print("Custom field {} has no data.".format(
                        custom_field['Name']))
                    continue
                field = create_custom_field(
                    dest_infusionsoft,
                    custom_field['Label'],
                    'Contact',
                    DATATYPES[custom_field['DataType']],
                    custom_field.get('Values'))
                rename_mapping["_" + custom_field['Name']] = field['Name']

    # Checks for contacts that already exist by FKID in Source App Contact Id
    # custom field
    existing_contacts = {}
    for contact_id in get_table(dest_infusionsoft,
                                'Contact',
                                {src_contact_id: "_%"},
                                ['Id', src_contact_id]):
        existing_contacts[int(contact_id[src_contact_id])] = contact_id['Id']

    # Create tag for indicating contacts have been transferred
    dest_category_id = dest_infusionsoft.DataService(
        'query',
        'ContactGroupCategory',
        1000,
        0,
        {'CategoryName': 'Application Transfer'},
        ['Id'])
    dest_tag_id = None
    if dest_category_id:
        dest_tag_id = dest_infusionsoft.DataService(
            'query',
            'ContactGroup',
            1000,
            0,
            {'GroupCategoryId': dest_category_id[0]['Id'],
             'GroupName': "Data from {}".format(config.SOURCE_APPNAME)},
            ['Id']
        )
    if dest_category_id:
        tag_cat_id = dest_category_id[0]['Id']
    else:
        tag_cat_id = dest_infusionsoft.DataService(
            'add',
            'ContactGroupCategory',
            {'CategoryName': 'Application Transfer'}
        )
    if not dest_tag_id:
        dest_infusionsoft.DataService(
            'add',
            'ContactGroup',
            {'GroupCategoryId': tag_cat_id,
             'GroupName': "Data from {}".format(config.SOURCE_APPNAME)
             }
        )

    user_relationship = {}
    for user in get_table(src_infusionsoft,
                          'User',
                          {},
                          ['Id', 'FirstName', 'LastName']):
        user_relationship[user['Id']] = "{} {}".format(
            user['FirstName'],
            user['LastName']
        )
    with open("{}user_relationship.json".format(dir_path), 'w') as fp:
        json.dump(user_relationship, fp)

    # Add all contacts to CSV
    num_contacts_created = 0
    emails = []
    with open("{}contacts.csv".format(dir_path),
              "w",
              newline='',
              encoding='utf-8') as csvfile:

        # Generate fieldnames for CSV
        all_fieldnames = (FIELDS['Contact'][:] +
                          cfs_to_import +
                          ["TransferTag", src_contact_id])
        if config.COMPANIES:
            all_fieldnames += [src_company_id]
        bad_fieldnames = ['ContactNotes',
                          'AccountId',
                          'CreatedBy',
                          'Groups',
                          'Id',
                          'LastUpdated',
                          'LastUpdatedBy',
                          'LeadSourceId',
                          'Validated']
        fieldnames = [x for x in all_fieldnames if x not in bad_fieldnames]

        # Ignore fields that aren't included in the headers
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for contact in contacts:

            # Skip contacts that already exist
            if existing_contacts.get(contact['Id']):
                print("Contact already exists: Contact ID {}".format(
                    existing_contacts[contact['Id']]))
                continue

            # Skip contacts that are companies
            if contact['Id'] == contact['CompanyID']:
                print("The contact is a company (ID: {})... skipping".format(
                    contact['CompanyID']))
                continue
            for key in contact_fields:
                if rename_mapping.get(key):
                    contact[rename_mapping[key]] = contact.pop(key, None)
            contact[src_contact_id] = str(contact['Id'])
            contact['OwnerId'] = user_relationship.get(contact.get('OwnerId'))
            contact['TransferTag'] = "Data from {}".format(
                config.SOURCE_APPNAME)
            if config.COMPANIES:
                contact[src_company_id] = str(contact['CompanyID'])
            else:
                contact['CompanyId'] = 0

            # Remove null values
            contact = {k: v for k, v in contact.items() if (v and v != 'null')}

            # Convert dates
            contact = convert_dict_dates_to_string(contact)
            writer.writerow(contact)
            if contact.get('Email'):
                emails += [contact['Email']]
            num_contacts_created += 1
        print("Contact CSV created with {} contacts".format(
            num_contacts_created))

    # Create list of opted out emails
    with open("{}email_opt_outs.csv".format(dir_path),
              "w",
              newline='',
              encoding='utf-8') as csvfile:
        fieldnames = FIELDS['EmailAddStatus'][:]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for email_status in get_table(src_infusionsoft, 'EmailAddStatus'):
            if (email_status['Type'] in OPT_OUT_STATUSES and
                    email_status['Email'] in emails):
                email_status = convert_dict_dates_to_string(email_status)
                writer.writerow(email_status)
        print("Email Opt Outs CSV created.")


# COMPANIES
# =============================================================================
if config.COMPANIES:
    src_account_id = create_custom_field(dest_infusionsoft,
                                         'Source App Company ID',
                                         'Company')['Name']

    # Generates full list of company fields, including custom fields
    company_fields = FIELDS['Company'][:]
    custom_fields = get_table(src_infusionsoft, 'DataFormField')
    for custom_field in custom_fields:
        if custom_field['FormId'] == -6 and custom_field['DataType'] != 23:
            company_fields += ["_{}".format(custom_field['Name'])]

    # Gets Source Companies
    companies = get_table(src_infusionsoft, 'Company', {}, company_fields)

    # Limit the custom fields to create to only those fields that have data
    fields_with_data = set().union(*(company.keys() for company in companies))
    regex = re.compile(r'_')
    cfs_to_import = [cf for cf in fields_with_data if regex.match(cf)]

    # Create custom fields
    rename_mapping = {}
    for custom_field in custom_fields:

        # Make sure the field is a company field and not a drilldown
        if custom_field['FormId'] == -6 and custom_field['DataType'] != 23:
            if config.CREATE_CUSTOM_FIELDS:
                if ("_" + custom_field['Name']) not in cfs_to_import:
                    print("Custom field {} has no data.".format(
                        custom_field['Name']))
                    continue
                field = create_custom_field(
                    dest_infusionsoft,
                    custom_field['Label'],
                    'Company',
                    DATATYPES[custom_field['DataType']],
                    custom_field.get('Values'))
                rename_mapping["_" + custom_field['Name']] = field['Name']

    # Checks for companies that already exist by FKID in Source App Company Id
    # custom field
    existing_companies = {}
    for company_id in get_table(dest_infusionsoft,
                                'Company',
                                {src_account_id: "_%"},
                                ['Id', src_account_id]):
        existing_companies[int(company_id[src_account_id])] = company_id['Id']

    # Create companies
    num_companies_created = 0
    company_relationship = {}
    with open("{}companies.csv".format(dir_path),
              "w",
              newline='',
              encoding='utf-8') as csvfile:

        # Generate fieldnames for CSV
        fieldnames = (FIELDS['Company'][:] +
                      cfs_to_import +
                      [src_account_id])

        # Ignore fields that aren't included in the headers
        writer = csv.DictWriter(
            csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for company in companies:

            # Skip contacts that already exist
            if existing_companies.get(company['Id']):
                print("Company already exists: Contact ID {}".format(
                    existing_companies[company['Id']]))
                company_relationship[company['Id']] = existing_companies[
                    company['Id']]
                continue

            for key in company_fields:
                if rename_mapping.get(key):
                    company[rename_mapping[key]] = company.pop(key, None)
            company[src_account_id] = str(company['Id'])

            # Remove null values
            company = {k: v for k, v in company.items() if (v and v != 'null')}

            # Convert dates
            company = convert_dict_dates_to_string(company)
            writer.writerow(company)
            num_companies_created += 1
        print("Contact CSV created with {} companies".format(
            num_companies_created))

# TAGS
# =============================================================================

if config.TAGS:
    categories = get_table(src_infusionsoft, 'ContactGroupCategory')
    tags = get_table(src_infusionsoft, 'ContactGroup')

    # Find tags that need to be created. In other words, skip tags that aren't
    # applied to contacts
    tags_on_contacts = []
    for contact in contacts:
        if contact.get('Groups'):
            tags_on_contacts += [int(tag) for tag in contact[
                'Groups'].split(",")]
    tags_on_contacts = list(set(tags_on_contacts))

    # Get existing categories so dupes aren't created.
    existing_categories = {}
    for category in get_table(dest_infusionsoft, 'ContactGroupCategory'):
        existing_categories[category['CategoryName']] = category['Id']

    # Get existing tags so dupes aren't created.
    existing_tags = {}
    for tag in get_table(dest_infusionsoft, 'ContactGroup'):
        existing_tags[tag['GroupName']] = tag['Id']

    # Create category if it doesn't exist
    category_relationship = {}
    categories_reversed = {}
    for category in categories:
        category_relationship[category['Id']] = (existing_categories.get(
            category.get('CategoryName')) or
            dest_infusionsoft.DataService(
                'add', 'ContactGroupCategory', category)
            )
        categories_reversed[category['Id']] = category['CategoryName']

    # Create tags if they don't exist, or create a CSV of tags for importing,
    # based on the config.TAGS setting
    tag_relationship = {}
    if config.TAGS_CSV:
        with open("{}tags.csv".format(dir_path), "w", newline='') as csvfile:
            fieldnames = FIELDS['ContactGroup'][:] + ['CategoryName']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for tag in tags:
                if tag['GroupCategoryId'] == 0:
                    tag['CategoryName'] = ''
                else:
                    tag['CategoryName'] = categories_reversed[
                        tag['GroupCategoryId']]
                writer.writerow(tag)
            print("Tags CSV created.")
    else:
        for tag in tags:
            if tag['GroupCategoryId'] != 0:
                tag['GroupCategoryId'] = category_relationship[
                    tag['GroupCategoryId']]
            tag_relationship[tag['Id']] = (existing_tags.get(
                tag['GroupName']) or
                dest_infusionsoft.DataService('add', 'ContactGroup', tag))
        print("Tags added via API")
        with open("{}tags.json".format(dir_path), 'w') as fp:
            json.dump(tag_relationship, fp, sort_keys=True, indent=4)

# PRODUCTS
# =============================================================================

if config.PRODUCTS:
    products = get_table(src_infusionsoft, 'Product')
    product_categories = get_table(src_infusionsoft, 'ProductCategory')
    category_assigns = get_table(src_infusionsoft, 'ProductCategoryAssign')
    sub_plans = get_table(src_infusionsoft, 'SubscriptionPlan')

    # Get existing products and categories to skip making those that exist
    existing_products = {}
    for product in get_table(dest_infusionsoft, 'Product'):
        existing_products[product['ProductName']] = product['Id']

    existing_product_categories = {}
    for category in get_table(dest_infusionsoft, 'ProductCategory'):
        existing_product_categories[
            category['CategoryDisplayName']] = category['Id']

    existing_sub_plans = get_table(dest_infusionsoft, 'SubscriptionPlan')
    existing_cat_assigns = get_table(
        dest_infusionsoft,
        'ProductCategoryAssign'
    )

    # Create products and generate relationship
    # Save relationship to json for access in further steps
    product_relationship = {}
    for product in products:
        if product['Id'] not in config.PRODUCTS_TO_SKIP:
            product_relationship[product['Id']] = (existing_products.get(
                product['ProductName']) or
                dest_infusionsoft.DataService('add', 'Product', product))

    with open("{}product_relationship.json".format(dir_path), 'w') as fp:
        json.dump(product_relationship, fp, sort_keys=True, indent=4)

    # Create sub plans and generate relationship
    # Save relationship to json for access in further steps
    sub_plan_relationship = {}
    for plan in sub_plans:
        if plan['ProductId'] in config.PRODUCTS_TO_SKIP:
            continue
        skip = False
        for ex_plan in existing_sub_plans:
            same_price = plan['PlanPrice'] == ex_plan['PlanPrice']
            same_cycles = plan['NumberOfCycles'] == ex_plan['NumberOfCycles']
            same_product = product_relationship.get(
                plan['ProductId']) == ex_plan['ProductId']
            skip = same_price and same_cycles and same_product
            if skip:
                sub_plan_relationship[plan['Id']] = ex_plan['Id']
                break
        plan['ProductId'] = product_relationship.get(plan['ProductId'])
        if not plan['ProductId'] or skip:
            continue
        sub_plan_relationship[plan['Id']] = dest_infusionsoft.DataService(
            'add',
            'SubscriptionPlan',
            plan)

    with open("{}sub_plan_relationship.json".format(dir_path), 'w') as fp:
        json.dump(sub_plan_relationship, fp, sort_keys=True, indent=4)

    # Create product categories
    prod_cat_relationship = {}
    for prod_cat in product_categories:
        prod_cat_relationship[
            prod_cat['Id']] = existing_product_categories.get(
            prod_cat['CategoryDisplayName']) or dest_infusionsoft.DataService(
                'add',
                'ProductCategory',
                prod_cat)

    # Assign products to categories
    for cat_assign in category_assigns:
        skip = False
        for ex_cat in existing_cat_assigns:
            same_product = product_relationship.get(
                cat_assign['ProductId']) == ex_cat['ProductId']
            same_cat = prod_cat_relationship.get(
                cat_assign['ProductCategoryId']) == ex_cat['ProductCategoryId']
            cat_exists = prod_cat_relationship.get(
                cat_assign['ProductCategoryId'])
            skip = same_product and (same_cat or not cat_exists)
            if skip:
                break
        if skip:
            continue
        cat_assign['ProductId'] = product_relationship[cat_assign['ProductId']]
        cat_assign['ProductCategoryId'] = prod_cat_relationship[
            cat_assign['ProductCategoryId']]
        dest_infusionsoft.DataService(
            'add',
            'ProductCategoryAssign',
            cat_assign)

# Generate ZIP file for all csvs created, then delete the CSVs
zipf = zipfile.ZipFile("{}{}_to_{}_step1.zip".format(
    dir_path,
    config.SOURCE_APPNAME,
    config.DESTINATION_APPNAME), 'w')

for name in glob.glob("{}*.csv".format(dir_path)):
    zipf.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    try:
        os.remove(name)
    except OSError:
        pass
