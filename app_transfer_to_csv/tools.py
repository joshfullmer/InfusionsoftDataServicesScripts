import datetime
from xmlrpc.client import DateTime


def convert_dict_dates_to_string(dictionary):
    for key in dictionary:
        if isinstance(dictionary[key], DateTime):
            dictionary[key] = datetime.datetime.strptime(str(dictionary[key]),
                                                         '%Y%m%dT%H:%M:%S')
        if isinstance(dictionary[key], str):
            dictionary[key] = dictionary[key].encode('utf-8').encode("ASCII")
    return dictionary
