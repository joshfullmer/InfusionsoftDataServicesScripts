from infusionsoft import Infusionsoft

appname = 'ju127'
apikey = 'dd2a3e0a40616221cd69a0b46558aae6'

ifs = Infusionsoft(appname, apikey)

print(ifs.DataService('count', 'Contact', {}))
