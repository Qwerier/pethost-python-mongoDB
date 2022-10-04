import datetime
import mongoengine as moen


class Owner(moen.Document):
    registered_date = moen.DateTimeField(default=datetime.datetime.now)
    name = moen.StringField(required=True)
    email = moen.StringField(required=True)
    password = moen.StringField(required=True)

    pet_ids = moen.ListField()
    room_ids = moen.ListField()

    meta = {
        'db_alias': 'core',
        'collection': 'owners'
    }
