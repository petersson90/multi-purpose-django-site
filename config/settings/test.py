from .dev import *  # noqa: F401,F403

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

MEDIA_ROOT = BASE_DIR / 'media_test'  # noqa: F405
