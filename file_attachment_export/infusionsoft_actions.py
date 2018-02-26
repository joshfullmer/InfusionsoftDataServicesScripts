import constants


def get_table(infusionsoft, tablename, query={}, fields=[]):
    if fields == []:
        fields += constants.FIELDS[tablename]
    table = []
    page = 0
    while True:
        table_page = infusionsoft.DataService('query',
                                              tablename,
                                              1000,
                                              page,
                                              query,
                                              fields)
        table += table_page
        if len(table_page) < 1000:
            break
        page += 1
    print("{} table returned {} records".format(tablename, len(table)))
    return table
