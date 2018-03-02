"""
Step 2 generates up to 6 CSVs:
- tags_for_contacts.csv
- notes.csv
- tasks_appointments.csv
- opportunities.csv
- orders_no_items.csv
- subscriptions.csv

"""
import datetime
import csv
import json
import os

from infusionsoft.library import Infusionsoft

import config
from constants import FIELDS, DATATYPES
from infusionsoft_actions import get_table, create_custom_field
from tools import convert_dict_dates_to_string


dir_path = "output/{} -- {}/".format(config.SOURCE_APPNAME,
                                     config.DESTINATION_APPNAME)
os.makedirs(dir_path, exist_ok=True)

src_infusionsoft = Infusionsoft(config.SOURCE_APPNAME, config.SOURCE_API_KEY)
dest_infusionsoft = Infusionsoft(config.DESTINATION_APPNAME,
                                 config.DESTINATION_API_KEY)

# ESTABLISH EXISTING RELATIONSHIPS
# =============================================================================
src_contact_id = create_custom_field(dest_infusionsoft,
                                     'Source App Contact ID')['Name']

contact_relationship = {}
for contact in get_table(dest_infusionsoft,
                         'Contact',
                         {src_contact_id: "_%"},
                         ['Id', src_contact_id]):
    contact_relationship[int(contact[src_contact_id])] = contact['Id']

user_relationship = {}
if os.path.isfile("{}user_relationship.json".format(dir_path)):
    with open("{}user_relationship.json".format(dir_path), 'r') as fp:
        user_relationship = json.load(fp)
user_relationship = {int(k): v for k, v in user_relationship.items()}

tag_relationship = {}
if os.path.isfile("{}tags.json".format(dir_path)):
    with open("{}tags.json".format(dir_path), 'r') as fp:
        tag_relationship = json.load(fp)
tag_relationship = {int(k): int(v) for k, v in tag_relationship.items()}

product_relationship = {}
if os.path.isfile("{}product_relationship.json".format(dir_path)):
    with open("{}product_relationship.json".format(dir_path), 'r') as fp:
        product_relationship = json.load(fp)
product_relationship = {int(k): int(v) for k, v in
                        product_relationship.items()}

sub_plan_relationship = {}
if os.path.isfile("{}sub_plan_relationship.json".format(dir_path)):
    with open("{}sub_plan_relationship.json".format(dir_path), 'r') as fp:
        sub_plan_relationship = json.load(fp)
sub_plan_relationship = {int(k): int(v) for k, v in
                         sub_plan_relationship.items()}


# TAGS FOR CONTACTS
# =============================================================================

if config.TAGS:
    tag_apps = get_table(src_infusionsoft,
                         'ContactGroupAssign',
                         {},
                         ['ContactId', 'GroupId', 'Contact.CompanyID'])

    with open("{}tags_for_contacts.csv".format(dir_path),
              'w', newline='') as csvfile:
        fieldnames = ['ContactId', 'GroupId']
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()

        for tag_app in tag_apps:
            contact_exists = contact_relationship.get(tag_app['ContactId'])
            contact_is_company = (tag_app['ContactId'] ==
                                  tag_app.get('Contact.CompanyId'))
            if not contact_exists or contact_is_company:
                continue
            tag_app['GroupId'] = tag_relationship[tag_app['GroupId']]
            tag_app['ContactId'] = contact_relationship[tag_app['ContactId']]
            writer.writerow(tag_app)

# NOTES
# =============================================================================

src_action_id = create_custom_field(dest_infusionsoft,
                                    'Source App Action ID',
                                    'ContactAction',
                                    'Text')['Name']

if config.NOTES:
    notes = get_table(src_infusionsoft,
                      'ContactAction',
                      {'ObjectType': 'Note'})

    existing_notes = []
    for note in get_table(dest_infusionsoft,
                          'ContactAction',
                          {src_action_id: "_%",
                           'ObjectType': 'Note'},
                          [src_action_id]):
        if note == 'ERROR':
            break
        existing_notes += [int(note[src_action_id])]

    with open("{}notes.csv".format(dir_path), 'w', newline='') as csvfile:
        fieldnames = list(set().union(*(d.keys() for d in notes)))
        fieldnames += [src_action_id]
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()

        for note in notes:
            contact_exists = contact_relationship.get(note['ContactId'])
            note_exists = note['Id'] in existing_notes
            if not contact_exists or note_exists:
                continue
            note[src_action_id] = str(note['Id'])
            note['ContactId'] = contact_relationship[note['ContactId']]
            user_id = user_relationship.get(note['UserID'])
            if user_id and user_id != 0:
                note['UserID'] = user_relationship[note['UserID']]
            note = convert_dict_dates_to_string(note)
            writer.writerow(note)


# TASKS & APPOINTMENTS
# =============================================================================

if config.TASKS_APPOINTMENTS:
    tasks = get_table(
        src_infusionsoft,
        'ContactAction',
        {'ObjectType': 'Task'})
    appointments = get_table(
        src_infusionsoft,
        'ContactAction',
        {'ObjectType': 'Appointment'})

    actions = tasks + appointments

    existing_tasks = []
    for task in get_table(src_infusionsoft,
                          'ContactAction',
                          {src_action_id: "_%",
                           'ObjectType': 'Task'},
                          [src_action_id]):
        if task == 'ERROR':
            break
        existing_tasks += [int(task[src_action_id])]

    existing_appts = []
    for appt in get_table(src_infusionsoft,
                          'ContactAction',
                          {src_action_id: "_%",
                           'ObjectType': 'Appointment'},
                          [src_action_id]):
        if appt == 'ERROR':
            break
        existing_tasks += [int(appt[src_action_id])]

    existing_actions = existing_tasks + existing_appts

    default_user_id = dest_infusionsoft.DataService(
        'getAppSetting',
        'Templates',
        'defuserid')
    default_user = get_table(
        dest_infusionsoft,
        'User',
        {'Id': default_user_id})[0]
    default_user_name = "{} {}".format(
        default_user['FirstName'],
        default_user['LastName'])

    with open("{}tasks_appointments.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        fieldnames = list(set().union(*(d.keys() for d in actions)))
        fieldnames += [src_action_id]
        writer = csv.DictWriter(csvfile,
                                fieldnames=fieldnames,
                                extrasaction='ignore')
        writer.writeheader()

        for action in actions:
            contact_exists = contact_relationship.get(action['ContactId'])
            action_exists = action['Id'] in existing_actions
            if not contact_exists or action_exists:
                continue
            action[src_action_id] = str(action['Id'])
            action['ContactId'] = contact_relationship[action['ContactId']]
            action['UserID'] = (user_relationship.get('UserID') or
                                default_user_name)
            action = convert_dict_dates_to_string(action)
            writer.writerow(action)


# OPPORTUNITIES
# =============================================================================

if config.OPPORTUNITIES:
    src_opp_id = create_custom_field(dest_infusionsoft,
                                     'Source App Opportunity ID')['Name']

    opp_custom_fields = get_table(src_infusionsoft,
                                  'DataFormField',
                                  {'FormId': -4})
    opp_fields = FIELDS['Lead'][:]
    opp_fields += ["_" + cf['Name'] for cf in opp_custom_fields]
    opportunities = get_table(src_infusionsoft, 'Lead', {}, opp_fields)

    stage_relationship = {}
    for stage in get_table(src_infusionsoft, 'Stage'):
        stage_relationship[stage['Id']] = stage['StageName']

    rename_mapping = {}
    for cf in opp_custom_fields:
        if cf['DataType'] == -23:
            continue
        field = create_custom_field(
            dest_infusionsoft,
            cf['Label'],
            'Lead',
            DATATYPES[cf['DataType']],
            cf.get('Values'))
        rename_mapping["_" + cf['Name']] = field['Name']

    existing_opps = []
    for opp in get_table(dest_infusionsoft,
                         'Lead',
                         {src_opp_id: "_%"},
                         [src_opp_id]):
        existing_opps += [int(opp[src_opp_id])]

    with open("{}opportunities.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        fieldnames = list(set().union(*(d.keys() for d in opportunities)))
        fieldnames += [src_opp_id]
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            extrasaction='ignore')
        writer.writeheader()

        for opp in opportunities:
            opp_exists = opp['Id'] in existing_opps
            contact_exists = contact_relationship.get(opp['ContactID'])
            if not contact_exists or opp_exists:
                continue
            for key in opp_fields:
                if rename_mapping.get(key):
                    opp[rename_mapping[key]] = opp.pop(key, None)
            opp['ContactID'] = contact_relationship[opp['ContactID']]
            opp['StageID'] = stage_relationship.get(opp['StageID'])
            opp['UserID'] = user_relationship[opp['UserID']]
            opp[src_opp_id] = str(opp['Id'])
            opp = convert_dict_dates_to_string(opp)
            writer.writerow(opp)


# ORDERS
# =============================================================================

if config.ORDERS:
    src_order_id = create_custom_field(dest_infusionsoft,
                                       'Source App Order ID')['Name']

    order_custom_fields = get_table(src_infusionsoft,
                                    'DataFormField',
                                    {'FormId': -9})
    order_fields = FIELDS['Job'][:]
    order_fields += ["_" + cf['Name'] for cf in order_custom_fields]
    orders = get_table(src_infusionsoft, 'Job', {}, order_fields)

    rename_mapping = {}
    for cf in order_custom_fields:
        if cf['DataType'] == -23:
            continue
        field = create_custom_field(
            dest_infusionsoft,
            cf['Label'],
            'Job',
            DATATYPES[cf['DataType']],
            cf.get('Values'))
        rename_mapping["_" + cf['Name']] = field['Name']

    existing_orders = []
    for order in get_table(dest_infusionsoft,
                           'Job',
                           {src_order_id: "_%"},
                           [src_order_id]):
        existing_orders += [int(order[src_order_id])]

    with open("{}orders_no_items.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        fieldnames = list(set().union(*(d.keys() for d in orders)))
        fieldnames += [src_order_id]
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            extrasaction='ignore')
        writer.writeheader()

        for order in orders:
            contact_exists = contact_relationship.get(order['ContactId'])
            sub_order = order['JobRecurringId'] != 0
            order_exists = order['Id'] in existing_orders
            if not contact_exists or sub_order or order_exists:
                continue
            for key in order_fields:
                if rename_mapping.get(key):
                    order[rename_mapping[key]] = order.pop(key, None)
            order['ProductId'] = product_relationship.get(order['ProductId'])
            order['DueDate'] = order.get('DueDate') or datetime.datetime.now()
            order['ContactId'] = contact_relationship[order['ContactId']]
            order[src_order_id] = order['Id']
            order = convert_dict_dates_to_string(order)
            writer.writerow(order)


# SUBSCRIPTIONS
# =============================================================================

if config.SUBSCRIPTIONS:
    pass
