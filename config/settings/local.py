from .base import *

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nasdaq',
        'USER': 'postgres',
        'HOST': '0.0.0.0',
        'PORT': 5432
    }
}

# DJANGO DEBUG TOOLBAR SETTINGS
# https://django-debug-toolbar.readthedocs.io/en/stable/configuration.html
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
