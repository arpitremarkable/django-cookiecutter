# django-cookiecutter
Cookiecutter for django (only aegon projects)

# Setup
```
pip3 install cookiecutter scaraplate virtualenvwrapper
git clone git@github.com:futureadybroker/django-cookiecutter.git /tmp/django-cookiecutter

PROJECT_NAME=<project_name>
scaraplate rollup /tmp/django-cookiecutter $PROJECT_NAME
rm -rf /tmp/django-cookiecutter

cd $PROJECT_NAME
mkvirtualenv $PROJECT_NAME -p python3.7
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
mkdir insurance/travel
./manage.py startapp travel insurance/travel
```

Add entry to `INSTALLED_APPS`
```
INSTALLED_APPS = [
    ...
    'insurance.travel',
}
```

Add following to `insurance/travel/apps.py`
```
from django.apps import AppConfig


class TravelConfig(AppConfig):
    label = 'travel_insurance'
    name = 'insurance.travel'
```
