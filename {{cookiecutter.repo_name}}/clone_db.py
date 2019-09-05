#!/usr/bin/env python3

import os
import subprocess


temp_file_name = "temp.dump"

new_user_name = input("user name of sink database: ")

db_name = input("source database: ") or ""

host_name = input("host of source database: ") or "{{cookiecutter.project_name}}.chygm3sdbezd.ap-southeast-1.rds.amazonaws.com"

user_name = input("user name of source database: ") or "{{cookiecutter.project_name}}_app"

password = input("Enter the password: ") or "Lk455pPEegq72eC"

# create environment variable for password required to access the server database for creating dump.
os.environ['PGPASSWORD'] = password


def create_restore(database, source_user, sink_user, source_host):
    # create dump of source database
    subprocess.Popen(
        ['pg_dump', '-Fc', '-f', temp_file_name, database, '-h', source_host, '-U', source_user],
        stdout=subprocess.PIPE
    ).communicate()

    # create sink database
    subprocess.Popen(
        ['psql', '-U', new_user_name, '-d', 'postgres', '-c', f'create database {database};'],
        stdout=subprocess.PIPE
    ).communicate()

    # restore dump into sink database
    subprocess.Popen(
        ['pg_restore', '--no-owner', '--no-acl', '--no-privileges', '-d', database, '-U', sink_user, temp_file_name],
        stdout=subprocess.PIPE
    ).communicate()

    # delete temp file, containing db dump
    subprocess.Popen(['rm', temp_file_name]).communicate()


if db_name == "":
    create_restore("{{cookiecutter.project_name}}_default", user_name, new_user_name, host_name)
    create_restore("{{cookiecutter.project_name}}_analytics", user_name, new_user_name, host_name)
    create_restore("{{cookiecutter.project_name}}_pii", user_name, new_user_name, host_name)
else:
    create_restore(db_name, user_name, new_user_name, host_name)
