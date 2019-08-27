import os
import logging.config

import dj_database_url
from django.utils.crypto import get_random_string
from environs import Env

#
#  Pull all configuration from the environment
#
env = Env()
try:
    env.read_env()
except FileNotFoundError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#
# Application loading
#
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'debug_toolbar',
    'umami',
    'redirect',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'bootstrap4',
    'concurrency',
    'markdownx',
    'guildmaster',
]

#
# Execution
#
WSGI_APPLICATION = 'umami.wsgi.application'
SECRET_KEY = env('SECRET_KEY', get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'))
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', [])
SITE_ID = 1
TIME_ZONE = 'UTC'
USE_TZ = True

#
# Development
#
DEBUG = env.bool('DEBUG', False)
LOCALDEV = env.bool('LOCALDEV', False)

#
# Security
#
INTERNAL_IPS = env.list('INTERNAL_IPS', [])
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not LOCALDEV:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True

#
# Routing
#
ROOT_URLCONF = 'umami.urls'
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'redirect.middleware.RedirectServiceMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REDIRECT_HOST = env('REDIRECT_HOST', None)
REDIRECT_SECURE = env.bool('REDIRECT_SECURE', True)

#
# Services
#
DATABASES = {'default': dj_database_url.config(default='sqlite:///test.db', conn_max_age=600)}
EMAIL_HOST = env('EMAIL_HOST', 'localhost')
EMAIL_PORT = env.int('EMAIL_PORT', 25)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', True)
EMAIL_TIMEOUT = env.int('EMAIL_TIMEOUT', None)
SERVER_EMAIL = env('SERVER_EMAIL', 'root@localhost')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', 'webmaster@localhost')

#
# Authentication and authorization
#
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'

ACCOUNT_EMAIL_REQUIRED = env.bool('ACCOUNT_EMAIL_REQUIRED', True)
ACCOUNT_EMAIL_VERIFICATION = env('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = env.bool('ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION', True)
SOCIALACCOUNT_EMAIL_REQUIRED = env.bool('SOCIALACCOUNT_EMAIL_REQUIRED', True)
SOCIALACCOUNT_EMAIL_VERIFICATION = env('SOCIALACCOUNT_EMAIL_VERIFICATION', 'mandatory')
SOCIALACCOUNT_QUERY_EMAIL = env.bool('SOCIALACCOUNT_QUERY_EMAIL', True)
SOCIALACCOUNT_STORE_TOKENS = env.bool('SOCIALACCOUNT_STORE_TOKENS', False)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

#
# Internationalization
#
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True

#
# Static content
#
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

#
# Templates
#
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': True,
        },
    }
]

#
# Logging
#
LOGGING = None
logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {'console': {'format': '%(asctime)s %(name)s [%(levelname)s] %(message)s'}},
        'handlers': {
            'console': {'class': 'logging.StreamHandler', 'formatter': 'console'},
            'null': {'class': 'logging.NullHandler'},
        },
        'loggers': {'django': {'handlers': ['console'], 'level': env('DJANGO_LOG_LEVEL', 'INFO').upper()}},
        'root': {'handlers': ['console'], 'level': env('DJANGO_LOG_LEVEL', 'INFO').upper()},
    }
)
