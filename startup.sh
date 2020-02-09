#!/bin/sh

set -e

# Wait until PostgreSQL is ready
until echo "select 1;" | python manage.py dbshell > /dev/null 2>&1; do
  >&2 echo "Database is unavailable - sleeping"
  sleep 1
done

python manage.py migrate --no-input
python manage.py createcachetable
python manage.py collectstatic --no-input
celery multi start 3 -A jjalbot -l info -c4 --pidfile=/var/run/celery/%n.pid
gunicorn -w 3 -b unix:/tmp/gunicorn.sock jjalbot.wsgi -D
nginx -g 'daemon off;'
