#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate --noinput

python manage.py add_suppliers

echo
echo '----------------------------------------------------------------------'
echo
pytest ./tests


echo
echo '----------------------------------------------------------------------'
echo
echo 'Test Basic Auth'
BASIC_AUTH="mr-flibble:flim-flam-flooble" pytest ./tests/test_basic_auth.py
