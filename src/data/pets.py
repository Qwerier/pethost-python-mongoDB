import datetime
import mongoengine as moen


class Pet(moen.Document):

    registered_date = moen.DateTimeField(default=datetime.datetime.now)
    species = moen.StringField(required=True)
    name = moen.StringField(required=True)
    height = moen.FloatField(required=True)
    need_desc = moen.StringField(required=True)

    meta = {
        "db_alias": 'core',
        'collection': 'pets'
    }
