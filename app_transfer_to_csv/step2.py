"""
Step 2 generates up to 6 CSVs:
- tags_for_contacts.csv
- notes.csv
- tasks_appointments.csv
- opportunities.csv
- orders_no_items.csv
- subscriptions.csv

"""
import csv
import json
import os

from infusionsoft.library import Infusionsoft

import config
from infusionsoft_actions import get_table, create_custom_field
from tools import convert_dict_dates_to_string


dir_path = "output/{} >> {}/".format(config.SOURCE_APPNAME,
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
        {'ObjectType': 'Task'}
    )
    appointments = get_table(
        src_infusionsoft,
        'ContactAction',
        {'ObjectType': 'Appointment'}
    )

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

    print(existing_actions)

    default_user_id = dest_infusionsoft.DataService(
        'getAppSetting',
        'Templates',
        'defuserid'
    )
    default_user = get_table(
        dest_infusionsoft,
        'User',
        {'Id': default_user_id}
    )[0]
    default_user_name = "{} {}".format(
        default_user['FirstName'],
        default_user['LastName']
    )

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
