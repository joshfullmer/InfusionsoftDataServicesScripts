from base64 import b64encode
import datetime as dt
import peewee as pw
import requests


from database.database import db


class Instance(pw.Model):
    appname = pw.CharField(unique=True)
    apikey = pw.CharField(null=True)
    access_token = pw.CharField(null=True)
    access_token_expiry = pw.DateTimeField(null=True)
    refresh_token = pw.CharField(null=True)

    class Meta:
        database = db

    @classmethod
    def get_apikey(cls, appname):
        instance = cls.get_or_none(cls.appname == appname)
        apikey = instance.apikey if instance else None
        return apikey

    @classmethod
    def create_or_update(cls, appname, apikey=None, access_token=None,
                         refresh_token=None):
        instance = cls.get_or_none(cls.appname == appname)
        if access_token:
            now = dt.datetime.now()
            access_token_expiry = now + dt.timedelta(days=1)
        else:
            access_token_expiry = None
        if instance:
            if apikey:
                instance.apikey = apikey
            if access_token:
                instance.access_token = access_token
            if refresh_token:
                instance.refresh_token = refresh_token
            if access_token:
                instance.access_token_expiry = access_token_expiry
            instance.save()
        else:
            instance = Instance.create(
                appname=appname,
                apikey=apikey,
                access_token=access_token,
                refresh_token=refresh_token,
                access_token_expiry=access_token_expiry,
            )
        return instance

    @classmethod
    def update_token(cls, appname):
        print("Updating API access token")
        instance = Instance.get_or_none(cls.appname == appname)
        if not instance:
            raise Exception('App does not exist')
        b64_cred = b64encode(b'nndwt7ass8w95kqfgh2utw9h:fWew3CY7zp')
        authorization = 'Basic ' + b64_cred.decode('utf-8')
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': instance.refresh_token,
        }
        headers = {
            'Authorization': authorization
        }
        response = requests.post(
            'https://api.infusionsoft.com/token',
            params,
            headers=headers,
        )
        r_json = response.json()
        instance = Instance.create_or_update(
            appname,
            access_token=r_json.get('access_token'),
            refresh_token=r_json.get('refresh_token'),
        )
        return instance


class Service(pw.Model):
    name = pw.CharField()  # Acronym for service
    appname = pw.CharField()
    status = pw.CharField(default='In Progress')  # In Progress or Complete

    # last row number or record ID added
    lastrecord = pw.IntegerField(null=True)
    lastupdated = pw.DateTimeField(default=dt.datetime.now())

    class Meta:
        database = db
