# django-cookiecutter
Cookiecutter for django (only aegon projects)

# Setup
```
pip3 install cookiecutter scaraplate virtualenvwrapper
git clone git@github.com:futureadybroker/django-cookiecutter.git /tmp/django-cookiecutter

mkdir <project_name>
scaraplate rollup /tmp/django-cookiecutter <project_name>

cd <project_name>
mkvirtualenv <project_name> -p python3.7
```
# Start
```
workon <project_name>
pip install -r requirements.txt -r requirements-dev.txt
./manage.py migrate
./manage.py createsuperuser
./manage.py runserver
```
Then visit and login at Admin page - http://localhost:8000/project_name/

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
