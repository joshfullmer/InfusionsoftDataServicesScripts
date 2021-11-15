from base64 import b64decode
import csv
import datetime as dt
import glob
import os
import requests
import shutil
import zipfile
import re

from database.utils import get_app_and_token
from database.models import Service

rest_url = 'https://api.infusionsoft.com/crm/rest/v1/files'


def fae():
    appname, token = get_app_and_token('Appname and Auth Code')

    cwd = os.getcwd()
    app_dir = cwd + '/file_attachment_export/attachments/' + appname
    attach_dir = app_dir + '/attachments'
    os.makedirs(attach_dir, exist_ok=True)

    input(f'Exported files will be placed in the following directory:\n'
          f'{app_dir}\n\nPress Enter to begin file export')

    service, _ = Service.get_or_create(
        name='fae',
        appname=appname,
        status='In Progress'
    )

    headers = {"Authorization": "Bearer " + token}

    file_ids = get_file_ids(headers)
    last_record = service.lastrecord
    if last_record:
        file_ids = list(filter(lambda x: x > last_record, file_ids))

    # Handle fieldnames
    print(f'Requesting {rest_url}')
    response1 = requests.get(f'{rest_url}', headers=headers)
    print(response1.json().get('files')[0])
    print(len(response1.json().get('files')))
    first_id = response1.json().get('files')[0].get('id')
    response2 = requests.get(f'{rest_url}/{first_id}', headers=headers)
    print(response2.json())
    if response2.json().get('message') == 'General error':
        print('General error encountered with first file, trying next.')
        print(response1.json().get('files')[1])
        first_id = response1.json().get('files')[1].get('id')
        response2 = requests.get(f'{rest_url}/{first_id}', headers=headers)
        print(response2.json())
    fieldnames = list(response2.json().get('file_descriptor').keys())

    attachment_csv = f'{app_dir}/attachment.csv'
    csv_exists = os.path.isfile(attachment_csv)

    # Simultaneously write file meta data to CSV and download file
    with open(attachment_csv, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not csv_exists:
            writer.writeheader()

        for file_id in file_ids:
            file_url = f'{rest_url}/{file_id}?optional_properties=file_data'
            response = requests.get(file_url, headers=headers)
            r_json = response.json()
            
            if r_json.get('message'):
                if r_json['message'] == 'User does not have permission to view this File':
                    print(f'Skipping File ID: {file_id}')
                else:
                    print(
                        f'File ID {file_id} encountered error: ' + r_json['message'])
                continue
            has502 = re.search(r'502', str(response))
            if has502:
                if has502:
                    print(f'Skipping File ID: {file_id}')
                else:
                    print(f'File ID {file_id} encountered error: ' + r_json['message'])
                continue
            #print(r_json.get('file_descriptor').get('id'))
            badid = r_json.get('file_descriptor').get('id')
            badidlist = []
            if badid in badidlist:
                if badid in badidlist:
                    print(f'Skipping File ID: {file_id}')
                else:
                    print(f'File ID {file_id} encountered error: ' + r_json['message'])
                continue
            #print(r_json.get('file_descriptor'))
            #print(r_json.get('file_descriptor').get('file_name'))
            writer.writerow(r_json.get('file_descriptor'))
            filename = r_json.get('file_descriptor').get('file_name')
            filepath = f'{attach_dir}/{file_id}_{filename}'
            try:
                with open(filepath, 'wb') as file:
                    file.write(b64decode(r_json.get('file_data')))
            except:
                with open(f'{attach_dir}/{file_id}', 'wb') as file:
                    file.write(b64decode(r_json.get('file_data')))
            print(f'File ID: {file_id} exported.')
            service.lastrecord = file_id
            service.lastupdated = dt.datetime.now()
            service.save()

    # Compress all files to ZIP
    now = dt.datetime.now()
    now_str = now.strftime('%Y%m%d%H%M%S')
    file = zipfile.ZipFile(f'{app_dir}/attachments_{now_str}.zip', 'w')
    for name in glob.glob(f'{attach_dir}/*'):
        file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
    file.close()

    if os.path.exists(attach_dir) and os.path.isdir(attach_dir):
        shutil.rmtree(attach_dir)

    service.status = 'Complete'
    service.save()


def get_file_ids(headers):
    print(f'Getting File IDs from API')
    out = []
    next_url = ''
    while True:
        response = requests.get(
            next_url or rest_url,
            headers=headers
        )
        r_json = response.json()
        if not r_json.get('files'):
            break
        out += [file.get('id') for file in r_json.get('files')]
        next_url = r_json.get('next')
    return sorted(out)
