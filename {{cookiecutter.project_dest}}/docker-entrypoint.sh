#!/bin/sh

./manage.py migrate --noinput
./manage.py collectstatic --noinput

exec "$@"
