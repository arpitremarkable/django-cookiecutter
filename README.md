# django-cookiecutter
Cookiecutter for django (only example projects)

# Setup
```
pip3 install cookiecutter scaraplate virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

git clone git@github.com:arpitremarkable/django-cookiecutter.git /tmp/django-cookiecutter

PROJECT_NAME=<project_name>

# New project
scaraplate rollup /tmp/django-cookiecutter $PROJECT_NAME
# Existing project
scaraplate rollup /tmp/django-cookiecutter $PROJECT_NAME --no-input

rm -rf /tmp/django-cookiecutter

cd $PROJECT_NAME
mkvirtualenv $PROJECT_NAME -p python3.8
```
# Start
```
workon $PROJECT_NAME
pip install -r requirements.txt -r requirements-dev.txt
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```
Then visit and login at Admin page - http://localhost:8000/PROJECT_NAME/

# Create new app
```
mkdir domain/travel
./manage.py startapp travel domain/travel
```

Add entry to `INSTALLED_APPS`
```
INSTALLED_APPS = [
    ...
    'domain.travel',
}
```

Add following to `domain/travel/apps.py`
```
from django.apps import AppConfig


class TravelConfig(AppConfig):
    label = 'travel_domain'
    name = 'domain.travel'
```
