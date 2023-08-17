#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate --noinput

echo "Migrations completed"

python manage.py add_suppliers

echo "Suppliers check completed"

echo "Starting app"

python manage.py collectstatic --no-input

watchmedo auto-restart --directory=./  --pattern=""*.py"" --recursive -- gunicorn --bind="0.0.0.0:$PORT" --workers=12 help_to_heat.wsgi:application
