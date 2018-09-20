import base64
import csv
import datetime
import glob
import os
import re
import shutil
import zipfile

from email_rest_actions import get_all_emails, get_email

now = datetime.datetime.now()

token = 'w9uhbhkkywnznh5ng87j4889'

email_ids = [email.get('id') for email in get_all_emails(token)]
email_count = len(email_ids)

csv_filename = f'emails_{datetime.datetime.strftime(now,"%Y%m%d")}.csv'
fieldnames = list(get_email(token, email_ids[0]).keys())
fieldnames.remove("html_content")
os.makedirs("emails/", exist_ok=True)

with open(csv_filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    writer.writeheader()
    count = 0
    for email_id in sorted(email_ids):
        count += 1
        print(f"Email ID {email_id}: {count} of {email_count}")
        email = get_email(token, email_id)
        html = email.pop('html_content', None)
        if html:
            html = base64.b64decode(html).decode('utf-8')
            html_filename = f"emails/Email_{email_id}.html"
            with open(html_filename, "w") as f:
                f.write(html)

        plain = email.get('plain_content', '')
        if plain:
            plain = base64.b64decode(plain).decode('utf-8')
            plain = re.sub(r'[\r\n]+', '', plain)
            email['plain_content'] = plain.strip()
        writer.writerow(email)

print(f"Time ellapsed: {datetime.datetime.now() - now}")

today = datetime.datetime.today()
today_str = today.strftime("%Y%m%d")
file = zipfile.ZipFile(f"emails_{today_str}.zip", "w")
for name in glob.glob("emails/*"):
    file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
file.close()

dirpath = "emails/"
if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)
