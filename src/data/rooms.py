import datetime
import mongoengine as moen

from data.bookings import Booking


class Room(moen.Document):

    registered_date = moen.DateTimeField(default=datetime.datetime.now)
    name = moen.StringField(required=True)
    price = moen.FloatField(required=True)
    square_meters = moen.FloatField(required=True)
    height = moen.FloatField(required=True)

    bookings = moen.EmbeddedDocumentListField(Booking)

    meta = {
        'db_alias': 'core',
        'collection': 'rooms'
    }
