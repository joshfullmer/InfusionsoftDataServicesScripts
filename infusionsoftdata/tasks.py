import time

from .celery import app


@app.task
def counter():
    i = 0
    for _ in range(10000):
        i += 1
        time.sleep(5)
    return i
