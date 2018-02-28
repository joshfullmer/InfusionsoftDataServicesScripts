from constants import FIELDS, CF_FORM_ID


def get_table(infusionsoft, tablename, query={}, fields=[]):
    lookup_fields = []
    if fields == []:
        lookup_fields += FIELDS[tablename][:]
    else:
        lookup_fields = fields
    table = []
    page = 0
    while True:
        table_page = infusionsoft.DataService('query',
                                              tablename,
                                              1000,
                                              page,
                                              query,
                                              lookup_fields)
        table += table_page
        if len(table_page) < 1000:
            break
        page += 1
    print("{} table returned {} records".format(tablename, len(table)))
    return table


def create_custom_field(infusionsoft, fieldname, tablename='Contact',
                        fieldtype='Text', values=None):
    query = {'Label': fieldname, 'FormId': CF_FORM_ID[tablename]}
    existing_fields = infusionsoft.DataService('query',
                                               'DataFormField',
                                               1000,
                                               0,
                                               query,
                                               FIELDS['DataFormField'])
    existing_field = []
    for f in existing_fields:
        if f['FormId'] == CF_FORM_ID[tablename]:
            existing_field += [f]

    field = {}
    if not existing_field:
        tab_id = infusionsoft.DataService('query',
                                          'DataFormTab',
                                          1000,
                                          0,
                                          {'FormId': CF_FORM_ID[tablename]},
                                          FIELDS['DataFormTab'])[0]['Id']
        header_id = infusionsoft.DataService('query',
                                             'DataFormGroup',
                                             1000,
                                             0,
                                             {'TabId': tab_id},
                                             FIELDS['DataFormGroup'])[0]['Id']
        field['Id'] = infusionsoft.DataService('addCustomField',
                                               tablename,
                                               fieldname,
                                               fieldtype,
                                               header_id)
        field['Name'] = "_" + infusionsoft.DataService('query',
                                                       'DataFormField',
                                                       1000,
                                                       0,
                                                       query,
                                                       ['Name'])[0]['Name']
        if values:
            infusionsoft.DataService('updateCustomField',
                                     field['Id'],
                                     values)
        print("Created field {}".format(field['Name']))
    else:
        field['Id'] = existing_field[0]['Id']
        field['Name'] = "_" + existing_field[0]['Name']
        print("Field {} already exists.".format(field['Name']))
    return field


def delete_table(infusionsoft, tablename):
    print("Deleting \"{}\" table".format(tablename))
    for record in get_table(infusionsoft, tablename):
        infusionsoft.DataService('delete', tablename, record['Id'])
    print("\"{}\" table deleted".format(tablename))
