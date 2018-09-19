web: gunicorn infusionsoftdata.wsgi --log-file -
worker: celery -A infusionsoftdata.tasks worker -B --loglevel=info