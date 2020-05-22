from base64 import b64decode
import csv
import datetime as dt
import glob
import os
import requests
import shutil
import zipfile

from database.models import Service
from database.utils import get_app_and_token

rest_url = 'https://api.infusionsoft.com/crm/rest/v1/emails'


def ehe():
    appname, token = get_app_and_token('Appname and Auth Code')

    cwd = os.getcwd()
    app_dir = cwd + '/email_history_export/emails/' + appname
    email_dir = app_dir + '/emails'
    os.makedirs(email_dir, exist_ok=True)

    input(f'Exported emails will be placed in the following directory:\n'
          f'{app_dir}\n\nPress Enter to begin the email export')

    service, _ = Service.get_or_create(
        name='ehe',
        appname=appname,
        status='In Progress'
    )

    headers = {"Authorization": "Bearer " + token}

    email_ids = get_email_ids(headers)
    lastrecord = service.lastrecord
    if lastrecord:
        email_ids = list(filter(lambda x: x > lastrecord, email_ids))
    response = requests.get(f'{rest_url}/{email_ids[0]}', headers=headers)
    r_json = response.json()
    fieldnames = list(r_json.keys())

    email_csv = f'{app_dir}/email.csv'
    csv_exists = os.path.isfile(email_csv)

    # Simultaneously write email meta data to CSV and download email
    with open(email_csv, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not csv_exists:
            writer.writeheader()

        email_count = 0
        total_emails = len(email_ids)
        durations = []
        for email_id in email_ids:
            start = dt.datetime.now()
            email_url = f'{rest_url}/{email_id}'
            response = requests.get(email_url, headers=headers)
            r_json = response.json()
            html_content = r_json.pop('html_content', None)
            for element in r_json:
                if 'html_content' in element:
                    del element['html_content']
            writer.writerow(r_json)
            filepath = f'{email_dir}/{email_id}.html'
            with open(filepath, 'wb') as file:
                file.write(b64decode(html_content))
            email_count += 1
            print(f'Email ID: {email_id} exported.')
            print(f'Email #{email_count} of {total_emails}')
            service.lastrecord = email_id
            service.lastupdated = dt.datetime.now()
            service.save()
            durations += [dt.datetime.now() - start]
            average_duration = sum(durations, dt.timedelta(0)) / len(durations)
            erd = average_duration * (total_emails - email_count)
            etc = dt.datetime.now() + erd
            print(f'Estimated remaining duration: {erd}')
            print(f'Estimated time of completion: {etc}\n')

    now = dt.datetime.now()
    print(f'Completed on: {now}')
    now_str = now.strftime('%Y%m%d%H%M%S')
    file = zipfile.ZipFile(f'{app_dir}/emails_{now_str}.zip', 'w')
    for name in glob.glob(f'{email_dir}/*'):
        file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    file.close()

    if os.path.exists(email_dir) and os.path.isdir(email_dir):
        shutil.rmtree(email_dir)

    service.status = 'Complete'
    service.save()


def get_email_ids(headers):
    out = []
    next_url = ''
    while True:
        response = requests.get(next_url or rest_url, headers=headers)
        r_json = response.json()
        if not r_json.get('emails'):
            break
        out += [email.get('id') for email in r_json.get('emails')]
        next_url = r_json.get('next')
    return sorted(out)
