"""
This program exports all email history items and puts them into a zipfile
that's found in the '/output' folder.

"""

from file_ids import FILE_IDS

from infusionsoft.library import Infusionsoft

import zipfile
import glob
import base64
import os
import shutil

# Initiation
appname = 'aps'
api_key = '009d934d1ce9ce27de31278901a360ff'

infusionsoft = Infusionsoft(appname, api_key)

file_path = "output/{}_emails/".format(appname)

os.makedirs(file_path, exist_ok=True)

# Gets all files from FileBox that have been given through the SQL
# query from above, and writes all of the files individually
for id in FILE_IDS:
    file = open("output/{}_emails/email_{}.html".format(appname, id), "w")

    string = infusionsoft.FileService('getFile', id)

    if isinstance(string, tuple):
        if string[0] == 'ERROR':
            print(string[1])
            break

    file.write(base64.b64decode(string).decode('utf-8'))

    file.close()

    print("This is the current File ID: {}".format(id))

# Adds all emails to a ZIP file
file = zipfile.ZipFile("output/{}_emails.zip".format(appname), "w")

for name in glob.glob("output/{}_emails/*".format(appname)):
    file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)

# Deletes the individual email files, leaving only the ZIP as output
dirpath = os.path.join("output", "{}_emails".format(appname))
if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)
