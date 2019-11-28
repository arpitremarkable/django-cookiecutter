from .settings import *


DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS += [
    'django_extensions',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '{{cookiecutter.project_name}}.sqlite3',
    },
}
