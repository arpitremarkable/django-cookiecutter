import os
import shutil


print('CWD', os.getcwd())  # prints /absolute/path/to/{{cookiecutter.project_dest}}

def remove(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)

app_payment = '{{cookiecutter.app_payment}}' == 'y'
app_data_store = '{{cookiecutter.app_data_store}}' == 'y'

if not app_payment:
    remove('payment')

if not app_data_store:
    remove('data_store')
