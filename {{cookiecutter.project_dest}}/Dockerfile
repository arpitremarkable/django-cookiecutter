FROM python:3.9-alpine

WORKDIR /usr/local/src/


RUN apk update

# For psycopg2-binary
RUN apk add postgresql-dev gcc python3-dev musl-dev

COPY ./requirements.txt ./requirements.txt
COPY ./requirements-dev.txt ./requirements-dev.txt
COPY ./constraints.txt ./constraints.txt
RUN pip install -r requirements.txt -r requirements-dev.txt

# For uwsgi
RUN apk add python3-dev build-base linux-headers pcre-dev
RUN pip install uwsgi

# postgresql-client
RUN apk add postgresql-client

ENV PORT=8080
EXPOSE 8080

COPY ./ ./
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD sh -c "uwsgi --http 0.0.0.0:8080 --module {{cookiecutter.project_name}}.wsgi --master --processes 4 --threads 2 --static-map /static=./static_root"
