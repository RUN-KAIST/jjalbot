FROM python:3.6-alpine

# Create project directory
RUN mkdir /jjalbot
WORKDIR /jjalbot/

# Install NGINX
RUN apk add nginx

# Psycopg2 dependency
RUN apk add postgresql-dev

# Pillow dependencies
RUN apk add jpeg-dev zlib-dev

# Install Poetry
RUN apk add curl
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

# Install Python dependencies
COPY pyproject.toml /jjalbot/pyproject.toml
COPY poetry.lock /jjalbot/poetry.lock
RUN /root/.poetry/bin/poetry config virtualenvs.create false
RUN /root/.poetry/bin/poetry install --no-root --no-dev

# Django DB shell utility
RUN apk add postgresql-client

COPY nginx.conf /etc/nginx/nginx.conf

# Redirect logs
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

RUN mkdir -p /var/run/celery

COPY . /jjalbot

CMD sh startup.sh

EXPOSE 8000
