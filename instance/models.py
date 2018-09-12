from django.db import models

import datetime


class Instance(models.Model):
    name = models.CharField(max_length=30)
    api_key = models.CharField(max_length=100, blank=True)
    access_token = models.CharField(max_length=50, blank=True)
    refresh_token = models.CharField(max_length=50, blank=True)
    expire_time = models.DateTimeField(blank=True)

    @classmethod
    def get_instance_or_error(instance_name):
        pass

    @classmethod
    def create_or_update_instance(cls, response):
        r_json = response.json()
        name = r_json.get('scope').split('.')[0][1:]
        access_token = r_json.get('access_token')
        refresh_token = r_json.get('refresh_token')
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_in = r_json.get('expires_in')
        expire_time = now + datetime.timedelta(seconds=expires_in)
        try:
            instance = Instance.objects.get(name=name)
        except Instance.DoesNotExist:
            instance = Instance(
                name=name,
                access_token=access_token,
                refresh_token=refresh_token,
                expire_time=expire_time)
        else:
            instance.access_token = access_token
            instance.refresh_token = refresh_token
            instance.expire_time = expire_time
        instance.save()
        return name
