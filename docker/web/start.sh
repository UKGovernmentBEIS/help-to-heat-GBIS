#!/bin/sh

set -o errexit
set -o nounset

# Migrate the database if it's out of date. Ideally we wouldn't do this on app startup for our deployed
# environments, because we're risking multiple containers attempting to run the migrations concurrently and
# getting into a mess. However, we very rarely add migrations at this point, so in practice it's easier to
# risk it and keep an eye on the deployment: we should be doing rolling deployments anyway which makes it
# very unlikely we run into concurrency issues. If that changes though we should look at moving migrations
# to a deployment pipeline step, and only doing the following locally (PC-1152).
python manage.py migrate --noinput

echo "Migrations completed"

python manage.py add_suppliers

echo "Suppliers check completed"

echo "Starting app"

python manage.py collectstatic --no-input

if [ "$DEBUG" = "True" ]
then
  watchmedo auto-restart --directory=./  --pattern=""*.py"" --recursive -- \
      waitress-serve --port=$PORT --threads=128 --asyncore-use-poll \
      --connection-limit=2000 --backlog=2000 \
      help_to_heat.wsgi:application
else
  watchmedo auto-restart --directory=./  --pattern=""*.py"" --recursive -- \
      gunicorn --bind="0.0.0.0:$PORT" \
      --workers=24 --worker-class="eventlet" \
      help_to_heat.wsgi:application
fi
