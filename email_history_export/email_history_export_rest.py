import base64
import csv
import datetime
import re

from rest_actions import get_all_emails, get_email, strip_tags

now = datetime.datetime.now()

token = 'k4m2yx93rvau7aev67yauaft'

email_ids = [email.get('id') for email in get_all_emails(token)]
email_count = len(email_ids)

filename = f'output_{datetime.datetime.strftime(now,"%Y_%m_%d")}.csv'
fieldnames = list(get_email(token, email_ids[0]).keys())

with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)

    writer.writeheader()
    count = 0
    for id in email_ids:
        count += 1
        print(f"Email ID {id}: {count} of {email_count}")
        email = get_email(token, id)
        html = email.get('html_content')
        html = base64.b64decode(html).decode('utf-8')
        html = strip_tags(html)
        html = re.sub(r'^\s+$', '', html)
        html = re.sub(r'[\r\n]+', '\n', html)
        html = html.strip()
        if len(html) > 32767:
            html = html[:32767]
        email['html_content'] = html
        if id == email_ids[0]:
            for c in html:
                print(c)
            print(email['html_content'])

        plain = email.get('plain_content', '')
        if plain:
            plain = base64.b64decode(plain).decode('utf-8')
            plain = re.sub(r'[\r\n]+', '', plain)
            email['plain_content'] = plain.strip()
        writer.writerow(email)

print(datetime.datetime.now() - now)
