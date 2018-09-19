from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'infusionsoftdata.settings')

app = Celery('infusionsoftdata')

app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
