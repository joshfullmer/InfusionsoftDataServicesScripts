import celery
import os
import time

app = celery.Celery('example')
app.conf.update(BROKER_URL=os.environ['REDIS_URL'],
                CELERY_RESULT_BACKEND=os.environ['REDIS_URL'])


@app.task
def counter():
    i = 0
    for _ in range(10000):
        time.sleep(5)
        i += 1
    return i
