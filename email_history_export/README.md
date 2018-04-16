# Instructions

This program will export all of the files from the given Infusionsoft
application that have been modified using the below SQL and indicated to
be email history files.

The output will be a ZIP file that contains each individual email history
file as a .html file

Make sure to add the comma separated list of email file attachment IDs
in 'file_ids.py' that is given from the SQL

## SQL

### Export Email History

#### Select the email data
```sql
SELECT EmailSent.Id,EmailSent.ContactId,EmailSent.EmailAddress,
EmailSent.DateCreated AS 'DateSent',Mail.Subject,Mail.FromAddress,Mail.FromName,MailContent.FileBoxId AS 'EmailMessageId'
FROM EmailSent
INNER JOIN MailContent
ON EmailSent.EmailId=MailContent.EmailId
INNER JOIN Mail
ON EmailSent.EmailId=Mail.Id WHERE MailContent.FileBoxId > 0;
```

#### Always backup in case you jack it up
```sql
CREATE TABLE FileBox_20180214 AS (SELECT * FROM FileBox);
```

#### Creates an ID to use
```sql
CREATE TABLE FileBoxEmailId_20180214 AS (SELECT Id FROM FileBox WHERE FileName LIKE 'email%');
```
Put these IDs in the 'file_ids.py'

#### Changes a few columns to work with export
```sql
UPDATE FileBox
SET FileName=CONCAT(FileName,'.html'),
Category = 'docs',
Extension = 'html'
WHERE Id IN (SELECT Id FROM FileBoxEmailId_20180214);
```

#### This changes everything back
```sql
UPDATE FileBox
SET FileName=LEFT(FileName,LENGTH(FileName)-5),
Category = 'email',
Extension = '',
FileBoxType = 3
WHERE Id IN (SELECT Id FROM FileBoxEmailId_20180214);
```