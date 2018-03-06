# SUMMARY

This application will import files from a folder of attachments and
a CSV that outlines the filename and who the file should be attached
to.

# INSTRUCTIONS

1. Set the appname and API key in 'file_attachment_import.py'
2. Add the attachments to the attachments folder, in a folder called "APPNAME_attachments/"
3. Add the attachments CSV to the attachments folder, named "APPNAME_attachments.csv", with the following required fields
    1. Contact ID as 'id'
    2. Desired filename as 'filename'
    3. Filename as is exists in the folder as 'filepath'
        1. This may be the same as 3.2
    4. File extension as 'extension'
4. Run in terminal.