from .base import *  # noqa: F401,F403
from .base import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', 'django-insecure-lsv-^8++5rbzl1!x5og)qm7pg+$mz=^nrnpb^rnr^bnhu6kj7)')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
