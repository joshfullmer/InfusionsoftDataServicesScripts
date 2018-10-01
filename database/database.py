import peewee as pw

from database import models


db = pw.SqliteDatabase('dataservices.db')


def initialize():
    db.connect()
    db.create_tables([models.Instance, models.Service])


def shutdown():
    db.close()


if __name__ == '__main__':
    initialize()
    shutdown()
