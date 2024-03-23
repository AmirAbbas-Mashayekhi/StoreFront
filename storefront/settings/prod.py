import os
from .common import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "storefront-prod",
        "HOST": "AmirAbbasMashayekhi.mysql.pythonanywhere-services.com",
        "USER": "AmirAbbasMashaye",
        "PASSWORD": "KgbT1384cout;",
    }
}
