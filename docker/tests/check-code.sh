#!/bin/sh

set -o errexit
set -o nounset

black .
isort .
flake8 .