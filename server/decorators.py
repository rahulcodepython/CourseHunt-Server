from rest_framework import response


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return response.Response(str(e))

    return wrapper
