import base64
import csv
import datetime
import glob
import os
import requests
import shutil
import zipfile

token = "xh7xna9dgxgxedwf79ryqgdd"
rest_url = "https://api.infusionsoft.com/crm/rest/v1"
headers = {"Authorization": "Bearer " + token}


def get_file_ids():
    out = []
    next_url = ""
    while True:
        response = requests.get(
            next_url or rest_url + "/files",
            headers=headers)
        if not response.json().get('files'):
            break
        out += [file.get('id') for file in response.json().get('files')]
        next_url = response.json().get('next')
    return out


file_ids = get_file_ids()
response = requests.get(f"{rest_url}/files/{file_ids[0]}", headers=headers)
fieldnames = list(response.json().get("file_descriptor").keys())
os.makedirs("output/", exist_ok=True)
with open("attachments_data.csv", "w", newline='') as csvf:
    writer = csv.DictWriter(csvf, fieldnames=fieldnames)
    writer.writeheader()

    for file_id in sorted(file_ids):
        url = f"{rest_url}/files/{file_id}?optional_properties=file_data"
        response = requests.get(url, headers=headers)
        writer.writerow(response.json().get('file_descriptor'))
        file_name = response.json().get('file_descriptor').get('file_name')
        filename = f"output/{file_id}_{file_name}"
        file = open(filename, "wb")
        file.write(base64.b64decode(response.json().get('file_data')))
        file.close()
        print(f"File ID: {file_id} complete.")

today = datetime.datetime.today()
today_str = today.strftime("%Y%m%d")
file = zipfile.ZipFile(f"files_{today_str}.zip", "w")
for name in glob.glob("output/*"):
    file.write(name, os.path.basename(name), zipfile.ZIP_DEFLATED)
file.close()

dirpath = "output/"
if os.path.exists(dirpath) and os.path.isdir(dirpath):
    shutil.rmtree(dirpath)
