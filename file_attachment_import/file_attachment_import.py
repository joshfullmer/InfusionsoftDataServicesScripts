"""
This application will import files from a folder of attachments and
a CSV that outlines the filename and who the file should be attached
to.

INSTRUCTIONS
============

1. Set the appname and API key below
2. Add the attachments to the attachments folder, in a
   folder called "APPNAME_attachments/"
3. Add the attachments CSV to the attachments folder,
   named "APPNAME_attachments.csv", with the following required fields
   a. Contact ID as 'id'
   b. Desired filename as 'filename'
   c. Filename as is exists in the folder as 'filepath'
      I. This may be the same as 'b.'
   d. File extension as 'extension'
4. Run in terminal.
"""
import base64
import csv
import os

from infusionsoft.library import Infusionsoft

from constants import QJ154_APIKEY, SUPPORTED_FILE_TYPES

# SET APPNAME AND API KEY
appname = 'qj154'
api_key = QJ154_APIKEY

infusionsoft = Infusionsoft(appname, api_key)

dir_path = "attachments/{}_attachments".format(appname)

if not os.path.isdir(dir_path):
    raise NotADirectoryError("Please put the files in "
                             "'attachments/{}_attachments'".format(appname))

csv_path = "attachments/{}_attachments.csv".format(appname)

if not os.path.isfile(csv_path):
    raise FileNotFoundError("Please name the CSV '{}_attachments.csv' "
                            "and put it in 'attachments/'".format(appname))

with open(csv_path, newline='', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.DictReader(f)

    if sorted(reader.fieldnames) != sorted(['id', 'filename',
                                            'filepath', 'extension']):
        raise ValueError("Incorrect column header names.  Must be:"
                         "'id', 'filename', 'filepath', and 'extension'")

    file_num = 0
    for row in reader:
        file_num += 1
        file_path = "/".join([dir_path, row['filepath']])

        if ((not os.path.isfile(file_path)) or
                (os.path.getsize(file_path)/2**20 > 9.5) or
                (row.get('extension') is None) or
                (row['extension'] == '') or
                (row['extension'].lower() not in SUPPORTED_FILE_TYPES)):
            continue

        print("")
        print("File #{}".format(file_num))
        print("{} - {}".format(file_path,
                               os.path.isfile(file_path)))
        print("Filesize (in MB): {}".format(os.path.getsize(file_path)/2**20))
        print("{}: {}".format(row['id'], row['filename']))
        print("Supported File Type? {}".format(row['extension'].lower()
                                               in SUPPORTED_FILE_TYPES))

        file = open(file_path, 'rb')
        resp = infusionsoft.FileService('uploadFile',
                                        int(row['id']),
                                        row['filename'],
                                        base64.b64encode(file.read())
                                              .decode('ascii'))
        print("File created! FileBoxId: {}".format(resp))
