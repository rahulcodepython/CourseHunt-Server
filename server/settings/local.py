from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv(
            "DB_NAME",
        ),
        "USER": os.getenv(
            "DB_USER",
        ),
        "PASSWORD": os.getenv(
            "DB_PASSWORD",
        ),
        "HOST": "localhost",
        "PORT": "5432",
    },
    # 'mongodb': {
    #         'ENGINE': 'djongo',
    #         'NAME': 'courseHunt',
    #         'ENFORCE_SCHEMA': False,
    #         'CLIENT': {
    #             'host': 'localhost',
    #             'port': 27017,
    #             'username': 'rahul',
    #             'password': 'admin',
    #         }
    #     }
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = []
CORS_ALLOW_ALL_ORIGINS = True
