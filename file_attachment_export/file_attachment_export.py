"""
This application will download all of the file attachments
connected to contacts (not emails, or company files)
and puts all of those files into a ZIP file.

The ZIP file will also have a "files.csv" which will outline
all of the other details about the files, including who they were
attached to, by contact ID
"""
import base64
import csv
import glob
import os
import re
import shutil
import zipfile

from infusionsoft.library import Infusionsoft

import constants
from infusionsoft_actions import get_table

# Initialization
appname = 'qj154'
api_key = constants.QJ154_APIKEY

infusionsoft = Infusionsoft(appname, api_key)

# Get contact IDs, so we can exclude files not attached to contacts
contact_ids = []
for contact in get_table(infusionsoft, 'Contact', fields=['Id']):
    contact_ids += [contact['Id']]

# Get all files, then exclude those not attached to contacts
files = []
for file in get_table(infusionsoft, 'FileBox'):
    if file['ContactId'] in contact_ids:
        files += [file]

dir_path = "output/{}_files/".format(appname)

os.makedirs(dir_path, exist_ok=True)

# Write each file's details to CSV
with open("{}files.csv".format(dir_path), "w", newline='') as csvfile:
    fieldnames = constants.FIELDS['FileBox']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through each file, download it, decode it, then write it
    for file in files:
        file['FileName'] = re.sub(r'\/', "-", file['FileName'])
        file_path = "{}{}_{}".format(
            dir_path,
            file['ContactId'],
            file['FileName'])

        # Skip if the file isn't supported, or if the file already exists
        # by the same filename
        if (file['Extension'] not in constants.SUPPORTED_FILE_TYPES and
                os.path.isfile(file_path)):
            continue
        file_data = infusionsoft.FileService('getFile', file['Id'])
        current_file = open(file_path, "wb")
        current_file.write(base64.b64decode(file_data))
        current_file.close()
        writer.writerow(file)

# Add all files to the zip file
zipf = zipfile.ZipFile("output/{}_files.zip".format(appname), "w")

for name in glob.glob("{}*".format(dir_path)):
    zipf.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)

# Delete original files, leaving on the zip file
if os.path.exists(dir_path) and os.path.isdir(dir_path):
    shutil.rmtree(dir_path)

print("\nThe ZIP file for the customer is in the following location:")
print(os.path.abspath("output/{}_files.zip".format(appname)))
print("")
