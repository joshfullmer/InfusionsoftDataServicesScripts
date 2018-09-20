from infusionsoft.library import Infusionsoft

from constants import FIELDS
from infusionsoft_actions import get_table

# QJ154_APIKEY = '1979978dc08730f121747d50003c8513'
SOURCE_APPNAME = 'nq473'  # 'qj154'
SOURCE_API_KEY = ''  # QJ154_APIKEY
DESTINATION_APPNAME = 'db473'  # 'te361'
DESTINATION_API_KEY = ''  # TE361_APIKEY

src_ifs = Infusionsoft(SOURCE_APPNAME, SOURCE_API_KEY)
dest_ifs = Infusionsoft(DESTINATION_APPNAME, DESTINATION_API_KEY)

custom_fields = get_table(src_ifs, 'DataFormField')
for custom_field in custom_fields:
    if custom_field['FormId'] == -1 and custom_field['DataType'] == 21:

        query = {'Label': custom_field['Label'], 'FormId': -1, 'DataType': 21}
        existing_fields = dest_ifs.DataService('query',
                                               'DataFormField',
                                               1000,
                                               0,
                                               query,
                                               FIELDS['DataFormField'])

        existing_field = []
        for f in existing_fields:
            if f['FormId'] == -1:
                existing_field += [f]

        field_id = existing_field[0]['Id'] if existing_field else 0

        if custom_field.get('Values') and field_id:
            r = dest_ifs.DataService('updateCustomField',
                                     field_id,
                                     {'Values': custom_field.get('Values')})
            print(r)

            print(f'Custom field ID {field_id} updated.')
