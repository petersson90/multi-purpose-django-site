from .dev import *  # noqa: F401,F403

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

MEDIA_ROOT = BASE_DIR / 'media_test'  # noqa: F405

# Keep test output quiet through the logging config rather than logging.disable():
# the latter switches off *all* logging process-wide and breaks assertLogs().
_quiet = {'handlers': ['null'], 'level': 'CRITICAL', 'propagate': False}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'null': {'class': 'logging.NullHandler'}},
    'root': {'handlers': ['null'], 'level': 'CRITICAL'},
    'loggers': {'django': _quiet, 'apps': _quiet},
}
