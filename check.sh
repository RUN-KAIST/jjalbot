#!/bin/sh

# Lint
flake8

# Wait until PostgreSQL is ready
until echo "select 1;" | python manage.py dbshell > /dev/null 2>&1; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

python manage.py migrate --no-input
python manage.py createcachetable
python manage.py check --deploy --fail-level WARNING --settings=jjalbot.settings.production
python manage.py test
