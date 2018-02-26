"""
This program will export all of the files from the given Infusionsoft
application that have been modified using the below SQL and indicated to
be email history files.

The output will be a ZIP file that contains each individual email history
file as a .html file

Make sure to add the comma separated list of email file attachment IDs
in 'file_ids.py' that is given from the SQL

SQL
====================
# Export Email History

# Select the email data
SELECT EmailSent.Id,EmailSent.ContactId,EmailSent.EmailAddress,
EmailSent.DateCreated AS 'DateSent',Mail.Subject,Mail.FromAddress,Mail.FromName,MailContent.FileBoxId AS 'EmailMessageId'
FROM EmailSent
INNER JOIN MailContent
ON EmailSent.EmailId=MailContent.EmailId
INNER JOIN Mail
ON EmailSent.EmailId=Mail.Id WHERE MailContent.FileBoxId > 0;

# Always backup in case you jack it up
CREATE TABLE FileBox_20180214 AS (SELECT * FROM FileBox);
# Creates an ID to use
CREATE TABLE FileBoxEmailId_20180214 AS (SELECT Id FROM FileBox WHERE FileName LIKE 'email%');

# Changes a few columns to work with export
UPDATE FileBox
SET FileName=CONCAT(FileName,'.html'),
Category = 'docs',
Extension = 'html'
WHERE Id IN (SELECT Id FROM FileBoxEmailId_20180214);

# This changes everything back
UPDATE FileBox
SET FileName=LEFT(FileName,LENGTH(FileName)-5),
Category = 'email',
Extension = '',
FileBoxType = 3
WHERE Id IN (SELECT Id FROM FileBoxEmailId_20180214);

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
