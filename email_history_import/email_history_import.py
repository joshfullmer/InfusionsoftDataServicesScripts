from base64 import b64encode
import csv
import datetime as dt
import os
import requests

from database.models import Service
from database.utils import get_app_and_token


def ehi():
    # TODO: needs refinement from actual email history import project
    appname, token = get_app_and_token('Appname and Auth Code')

    cwd = os.getcwd()
    app_dir = cwd + '/email_history_import/emails/' + appname
    email_dir = app_dir + '/emails'
    os.makedirs(email_dir, exist_ok=True)
    input(f'Put the folder and CSV into the following directory:\n'
          f'{app_dir}\n\nPress Enter when the files have been moved.')

    # Check for folder and CSV
    # Check if there are files in the emails folder
    # Check if a CSV is present
    # Check if CSV has expected column headers
    csv_filename = ''
    while True:
        file_count = len(os.listdir(email_dir))
        if file_count <= 0:
            q = input(f'Please upload files to the \'emails\' folder in '
                      f'the appropriate application folder: emails/'
                      f'{appname}/emails\nEnter q to quit')
            if q.lower() == 'q':
                break
            else:
                continue
        for root, dirs, files in os.walk(app_dir):
            for file in files:
                if not csv_filename and file.endswith('.csv'):
                    with open(os.path.join(app_dir, file), 'r') as f:
                        csv_filename = f.name
        if not csv_filename:
            q = input(f'Please upload the CSV to the \'{appname}\' folder in '
                      f'the appropriate application folder: emails/'
                      f'{appname}\nEnter q to quit')
            if q.lower() == 'q':
                break
            else:
                continue
        with open(csv_filename, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames)
        exp_headers = {
            'contact_id',
            'headers',
            'html_content',
            'opened_date',
            'plain_content',
            'received_date',
            'sent_date',
            'sent_from_address',
            'sent_from_reply_address',
            'sent_to_address',
            'sent_to_bcc_addresses',
            'sent_to_cc_addresses',
            'subject'
        }
        if headers & exp_headers != headers:
            header_str = ', '.join(exp_headers)
            q = input(f'Please ensure that all of the following columns '
                      f'appear in the CSV:\n{header_str}')
            if q.lower() == 'q':
                break
            else:
                continue
        break

        service, _ = Service.get_or_create(
            name='ehi',
            appname=appname,
            status='In Progress'
        )

        # Import email history
        with open(csv_filename, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)

            filenum = 0
            for row in reader:
                filenum += 1
                if service.lastrecord and service.lastrecord >= filenum:
                    continue
                html_filepath = os.path.join(email_dir, row['html_content'])
                plain_filepath = os.path.join(email_dir, row['plain_content'])
                html_isfile = os.path.isfile(html_filepath)
                plain_isfile = os.path.isfile(plain_filepath)
                file_exists = html_isfile or plain_isfile
                if not file_exists:
                    continue

                headers = {
                    "Authorization": "Bearer " + token,
                    "Content-Type": "application/json;charset=UTF-8",
                    "Accept": "application/json, */*"
                }
                if html_isfile:
                    file = open(html_filepath, 'rb')
                    file_data = b64encode(file.read()).decode('ascii')
                    file.close()
                else:
                    file = open(plain_filepath, 'rb')
                    file_data = b64encode(file.read()).decode('ascii')
                    file.close()
                contact_id = int(row.get('contact_id'))
                body = {
                    'contact_id': contact_id,
                    'headers': row.get('headers'),
                    'html_content': file_data,
                    'opened_date': row.get('opened_date'),
                    'plain_content': '',
                    'received_date': row.get('received_date'),
                    'sent_date': row.get('sent_date'),
                    'sent_from_address': row.get('sent_from_address'),
                    'sent_from_reply_address': row.get(
                        'sent_from_reply_address'
                    ),
                    'sent_to_address': row.get('sent_to_address'),
                    'sent_to_bcc_addresses': row.get('sent_to_bcc_addresses'),
                    'sent_to_cc_addresses': row.get('sent_to_cc_addresses'),
                    'subject': row.get('subject'),
                }
                url = 'https://api.infusionsoft.com/crm/rest/v1/emails'
                response = requests.post(url, headers=headers, json=body)
                email_id = response.json().get('id')
                if response.status_code == 200:
                    print(f'Email #{filenum}')
                    print(f'Contact ID: {contact_id} - Email ID: {email_id}')
                    print(f'Email recorded!\n')

                service.lastrecord = filenum
                service.lastupdated = dt.datetime.now()
                service.save()

    service.status = 'Complete'
    service.save()

    print('Email History Import complete!')
