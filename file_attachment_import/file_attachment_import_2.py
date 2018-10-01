from database.models import Instance


def fai():
    appname = input('Appname: ')
    apikey = Instance.get_apikey(appname)
    if apikey:
        resp = input('API key found. Use this one? (yN)')
        if resp.lower() == 'n':
            apikey = None
    if not apikey:
        apikey = input('API key: ')
    Instance.create_or_update(appname, apikey)


if __name__ == '__main__':
    fai()
