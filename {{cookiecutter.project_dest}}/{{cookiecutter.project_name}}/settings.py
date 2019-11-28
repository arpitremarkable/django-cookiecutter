"""
Django settings for {{cookiecutter.project_name}} project.

Generated by 'django-admin startproject' using Django 2.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import collections
import os
import subprocess


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_MODULES_PATH = subprocess.check_output(["npm", "bin"]).strip()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i0g1h*(hz^oni&yi+&fr9(euk9d7p#zx$%5=87@xed=4dgde&c'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ("DJANGO_DEBUG" in os.environ) and (os.environ["DJANGO_DEBUG"] == '1')

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    {%- if cookiecutter.feature_i18n == 'y' %}
    'modeltranslation',  # need to be before django.contrib.admin
    {%- endif %}
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    {%- if cookiecutter.app_data_store == 'y' %}
    'data_store',
    {%- endif %}
    'django.contrib.postgres',
    {%- if cookiecutter.feature_i18n == 'y' %}
    'rosetta',
    {%- endif %}
    # 'analytics',  # optional,
    'common',
    {%- if cookiecutter.app_payment == 'y' %}
    'payment',
    {%- endif %}

]


MIDDLEWARE = [
    # 'analytics.middleware.VisitorTrackingMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    '{{cookiecutter.project_name}}.middleware.request.GlobalRequestMiddleware',
]

ROOT_URLCONF = '{{cookiecutter.project_name}}.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

{%- if cookiecutter.feature_i18n == 'y' %}
# i18n code start
LANGUAGE_CODE = 'en'
MODELTRANSLATION_DEFAULT_LANGUAGE = MODELTRANSLATION_PREPOPULATE_LANGUAGE = 'en'

# Translators: Name of language in it's local form
LANGUAGES = (
    ('{{cookiecutter.country_language_code}}', ('{{cookiecutter.country_language_name}}')),
    ('en', ('English')),
)

MODELTRANSLATION_LANGUAGES = ('en', 'th')

ROSETTA_SHOW_AT_ADMIN_PANEL = True
# i18n code end
{% endif %}

WSGI_APPLICATION = '{{cookiecutter.project_name}}.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {}

# DB_APP_ROUTER = {
#     'analytics': (
#         'analytics',
#     ),
#     'pii': (
#         'payment',
#     ),
# }

ALLOW_DATABASE_UNION = False

LOGGING = {}

DATABASE_ROUTERS = ['{{cookiecutter.project_name}}.database_routers.Router']

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = 'admin:login'

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/


TIME_ZONE = 'UTC'

{%- if cookiecutter.feature_i18n == 'y' %}
USE_I18N = True

USE_L10N = True
{% endif %}

FORMAT_MODULE_PATH = [
    '{{cookiecutter.project_name}}.formats',
]

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')
CSRF_USE_SESSIONS = False
CSRF_COOKIE_DOMAIN = None
SESSION_COOKIE_AGE = 60 * 60 * 24 * 365  # Seconds in a year

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

DATE_FORMAT = "j M Y"

TRACK_PAGEVIEWS = True  # Track WebEvents
