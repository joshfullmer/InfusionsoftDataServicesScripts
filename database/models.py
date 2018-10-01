import datetime as dt
import peewee as pw


from database.database import db


class Instance(pw.Model):
    appname = pw.CharField(unique=True)
    apikey = pw.CharField()

    class Meta:
        database = db

    @classmethod
    def get_apikey(cls, appname):
        instance = cls.get_or_none(cls.appname == appname)
        apikey = instance.apikey if instance else None
        return apikey

    @classmethod
    def create_or_update(cls, appname, apikey):
        instance = cls.get_or_none(cls.appname == appname)
        if instance:
            Instance.update(apikey=apikey).execute()
        else:
            instance = Instance.create(appname=appname, apikey=apikey)
        return instance


class Service(pw.Model):
    name = pw.CharField()
    appname = pw.CharField()
    status = pw.CharField()
    stage = pw.CharField(null=True)
    last_updated = pw.DateTimeField(default=dt.datetime.now())

    class Meta:
        database = db
