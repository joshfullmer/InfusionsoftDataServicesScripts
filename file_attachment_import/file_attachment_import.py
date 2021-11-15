from base64 import b64encode
import csv
import datetime as dt
import os
import requests

from constants import SUPPORTED_FILE_TYPES
from database.utils import get_app_and_token
from database.models import Service


def clear():
    os.system('cls') if os.name == 'nt' else os.system('clear')


def fai():
    appname, token = get_app_and_token('Appname and Auth Code')
    # clear()
    cwd = os.getcwd()
    app_dir = cwd + '\\file_attachment_import\\attachments\\' + appname
    attach_dir = app_dir + '\\attachments'
    os.makedirs(attach_dir, exist_ok=True)
    input(f'Put the folder and CSV into the following directory:\n'
          f'{app_dir}\n\nPress Enter when the files have been moved.')

    # Check for folder and CSV
    # Check if there are files in the attachments folder
    # Check if a CSV is present
    # Check if CSV has expected column headers
    csv_filename = ''
    while True:
        file_count = len(os.listdir(attach_dir))
        if file_count <= 0:
            q = input(f'Please upload files to the \'attachments\' folder in'
                      f'the appropriate application folder: attachments/'
                      f'{appname}\\attachments\nEnter q to quit')
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
            q = input(f'Please upload the CSV to the \'{appname}\' folder in'
                      f'the appropriate application folder: attachments\\'
                      f'{appname}\nEnter q to quit')
            if q.lower() == 'q':
                break
            else:
                continue
        with open(csv_filename, 'r', encoding='utf-8-sig') as csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames)
        exp_headers = {'id', 'filename', 'filepath', 'extension'}
        if headers & exp_headers != headers:
            header_str = ', '.join(exp_headers)
            q = input(f'Please ensure that all four of the following columns '
                      f'appear in the CSV:\n{header_str}')
            if q.lower() == 'q':
                break
            else:
                continue
        break

    service, _ = Service.get_or_create(
        name='fai',
        appname=appname,
        status='In Progress'
    )

    # Import files
    with open(csv_filename, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)

        filenum = 0
        for row in reader:
            filenum += 1
            if service.lastrecord and service.lastrecord >= filenum:
                #print(service.lastrecord)
                continue
            filepath = os.path.join(attach_dir, row['filepath'])
            skip = ((not os.path.isfile(filepath)) or
                    (os.path.getsize(filepath)/2**20 > 9.5) or
                    (row.get('extension') is None) or
                    (row['extension'] == '') or
                    (row['extension'].lower() not in SUPPORTED_FILE_TYPES))
            #print(skip)
            if skip:
                reason = ""

                if (not os.path.isfile(filepath)):
                    reason = "file doesn't exist"
                if (os.path.getsize(filepath)/2**20 > 9.5):
                    reason = "file too big"
                if (row.get('extension') is None) or (row['extension'] == ''):
                    reason = "no file extension"
                if (row['extension'].lower() not in SUPPORTED_FILE_TYPES):
                    reason = f"filetype '{row['extension']}' not supported"

                print("skipping: " + str(filenum) + " due to the following reason:")
                print(reason)
                continue
            headers = {
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json;charset=UTF-8",
                "Accept": "application/json, */*"
            }
            file = open(os.path.join(attach_dir, row['filepath']), 'rb')
            file_data = b64encode(file.read()).decode('ascii')
            file.close()
            contact_id = int(row['id'])
            #print(contact_id)
            filename = row['filename']
            print(f'Filename: {filename}')
            body = {
                'file_name': filename,
                'file_data': file_data,

                # 'contact_id': 0, # contact_id,
                'is_public': True,
                'file_association': 'COMPANY', # 'CONTACT',
            }
            url = 'https://api.infusionsoft.com/crm/rest/v1/files'
            
            try:
                resp = requests.post(url, headers=headers, json=body)
                # print(resp)
                print(resp.text)
                if resp.json().get('message'):
                    print(resp.json())
                file_id = resp.json().get('file_descriptor').get('id')
                if resp.status_code == 200:
                    print(f'File #{filenum}')
                    print(f'{filepath} - {os.path.isfile(filepath)}')
                    print(f'Filesize in MB: {os.path.getsize(filepath)/2**20}')
                    print(f'{contact_id}: {filename}')
                    print(f'File uploaded! FileBoxId: {file_id}\n')
            except Exception as e:
                print("!!ERROR ON ID: {}".format(filename))
            service.lastrecord = filenum
            service.lastupdated = dt.datetime.now()
            service.save()

    service.status = 'Complete'
    service.save()

    print('File Attachment Import Complete!') 


if __name__ == '__main__':
    fai()
