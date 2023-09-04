#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate --noinput

echo "Migrations completed"

python manage.py add_suppliers

echo "Suppliers check completed"

echo "Starting app"

python manage.py collectstatic --no-input

watchmedo auto-restart --directory=./  --pattern=""*.py"" --recursive -- waitress-serve --port=$PORT --threads=128 --asyncore-use-poll --connection-limit=2000 --backlog=2000 help_to_heat.wsgi:application
