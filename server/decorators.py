from .message import Message
from django.conf import settings


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if settings.DEBUG:
                print(str(e))
            return Message.error(str(e))

    return wrapper
