from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401,F403
from .base import env, env_bool, env_list

if not SECRET_KEY:  # noqa: F405
    raise ImproperlyConfigured('Set the DJANGO_SECRET_KEY environment variable.')
if not ALLOWED_HOSTS:  # noqa: F405
    raise ImproperlyConfigured('Set DJANGO_ALLOWED_HOSTS (comma-separated).')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Serve static files from the app itself with WhiteNoise (run `collectstatic` on deploy).
# Uploaded media (avatars) is NOT served by WhiteNoise: serve MEDIA_ROOT from your web server.
MIDDLEWARE = [  # noqa: F405
    MIDDLEWARE[0],  # noqa: F405  (SecurityMiddleware must stay first)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    *MIDDLEWARE[1:],  # noqa: F405
]
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

CSRF_TRUSTED_ORIGINS = env_list('DJANGO_CSRF_TRUSTED_ORIGINS')

SECURE_SSL_REDIRECT = env_bool('DJANGO_SECURE_SSL_REDIRECT', True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(env('DJANGO_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_CONTENT_TYPE_NOSNIFF = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(env('EMAIL_PORT', '587'))
EMAIL_HOST_USER = env('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = env_bool('EMAIL_USE_TLS', True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
