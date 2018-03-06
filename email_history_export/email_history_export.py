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
appname = 'jg351'
api_key = '147271c4053bcee09571853d90f3ca8d'

infusionsoft = Infusionsoft(appname, api_key)

file_path = "output/{}_emails/".format(appname)

os.makedirs(file_path, exist_ok=True)

# Gets all files from FileBox that have been given through the SQL
# query from above, and writes all of the files individually
for id in FILE_IDS:
    file = open("output/{}_emails/email_{}.html".format(appname, id), "w")

    string = infusionsoft.FileService('getFile', id)

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
