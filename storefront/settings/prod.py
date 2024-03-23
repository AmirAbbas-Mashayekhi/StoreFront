import os
from .common import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "railway",
        "HOST": "monorail.proxy.rlwy.net",
        "USER": "root",
        "PASSWORD": "OYzPivwVAKdjNXAJGESjSNtrIljBIQsp",
    }
}
