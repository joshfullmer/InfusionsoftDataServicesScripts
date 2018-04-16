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
from dateutil.relativedelta import relativedelta
import csv
import glob
import json
import os
import zipfile

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
                                       'Source App Order ID'
                                       'Job')['Name']

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
        print(order)
        if isinstance(order, str):
            break
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
    subscriptions = get_table(
        src_infusionsoft,
        'RecurringOrder')

    credit_cards = {}
    for cc in get_table(
            src_infusionsoft,
            'CreditCard',
            {},
            ['Id',
             'ContactId',
             'Last4',
             'ExpirationMonth',
             'ExpirationYear',
             'NameOnCard']):
        key = "{} - {} - {}/{} - {}".format(
            contact_relationship.get(cc.get('ContactId')),
            cc.get('Last4'),
            cc.get('ExpirationMonth'),
            cc.get('ExpirationYear'),
            cc.get('NameOnCard'))
        credit_cards[key] = cc['Id']

    cc_relationship = {}
    for cc in get_table(
            dest_infusionsoft,
            'CreditCard',
            {},
            ['Id',
             'ContactId',
             'Last4',
             'ExpirationMonth',
             'ExpirationYear',
             'NameOnCard']):
        key = "{} - {} - {}/{} - {}".format(
            cc.get('ContactId'),
            cc.get('Last4'),
            cc.get('ExpirationMonth'),
            cc.get('ExpirationYear'),
            cc.get('NameOnCard'))
        if credit_cards.get(key):
            cc_relationship[credit_cards[key]] = cc['Id']

    fieldnames = [
        'ContactId',
        'SubscriptionPlanId',
        'ProductId',
        'ProgramId',
        'CC1',
        'PaymentGatewayId',
        'Frequency',
        'BillingCycle',
        'BillingAmt',
        'PromoCode',
        'Status',
        'StartDate',
        'EndDate',
        'ReasonStopped',
        'PaidThruDate',
        'NextBillDate',
        'AutoCharge',
        'MaxRetry',
        'NumDaysBetweenRetry']

    with open("{}subscriptions.csv".format(dir_path),
              'w',
              newline='') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            extrasaction='ignore')
        writer.writeheader()

        for sub in subscriptions:
            if not contact_relationship.get(sub['ContactId']):
                continue
            sub['ContactId'] = contact_relationship.get(sub.get('ContactId'))
            sub['SubscriptionPlanId'] = sub_plan_relationship.get(sub.get(
                'SubscriptionPlanId'))
            sub['ProductId'] = product_relationship.get(sub.get('ProductId'))
            sub['ProgramId'] = sub_plan_relationship.get(sub.get('ProgramId'))
            if cc_relationship.get(sub.get('CC1')):
                sub['CC1'] = cc_relationship.get(sub.get('CC1'))
            elif cc_relationship.get(sub.get('CC2')):
                sub['CC2'] = cc_relationship.get(sub.get('CC2'))
            else:
                sub['CC1'] = 0
            sub['PaymentGatewayId'] = "SEE DESTINATION APP"
            if sub.get('AutoCharge') == 1:
                sub['AutoCharge'] = 'Yes'
            else:
                sub['AutoCharge'] = 'No'
            sub = convert_dict_dates_to_string(sub)

            pay_date_shift = relativedelta()
            if sub['BillingCycle'] == '1':
                pay_date_shift.years = sub.get('Frequency')
            elif sub['BillingCycle'] == '2':
                pay_date_shift.months = sub.get('Frequency')
            elif sub['BillingCycle'] == '3':
                pay_date_shift.weeks = sub.get('Frequency')
            elif sub['BillingCycle'] == '6':
                pay_date_shift.days = sub.get('Frequency')

            if not sub.get('PaidThruDate') and sub.get('NextBillDate'):
                sub['PaidThruDate'] = sub.get('NextBillDate') - pay_date_shift

            if config.SUBSCRIPTION_CUT_OFF_DATE:
                cut_off = datetime.datetime.strptime(
                    config.SUBSCRIPTION_CUT_OFF_DATE,
                    '%Y/%m/%d')
                if (sub.get('NextBillDate') <= cut_off and
                        sub['Status'] == 'Active'):
                    while sub.get('PaidThruDate') <= cut_off:
                        sub['PaidThruDate'] = (sub.get('PaidThruDate') +
                                               pay_date_shift)
            writer.writerow(sub)

# ZIPFILE
# =============================================================================

# Generate ZIP file for all csvs created, then delete the CSVs
zipf = zipfile.ZipFile("{}{}_to_{}_step2.zip".format(
    dir_path,
    config.SOURCE_APPNAME,
    config.DESTINATION_APPNAME), 'w')

for name in glob.glob("{}*.csv".format(dir_path)):
    zipf.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    try:
        os.remove(name)
    except OSError:
        pass
