import mongoengine as moen


def global_init():
    moen.register_connection(alias='core', name='pet_host')
