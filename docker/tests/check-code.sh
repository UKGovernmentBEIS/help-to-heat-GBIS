#!/bin/bash

set -o errexit
set -o nounset

if [[ $1 = "--check" ]]; then
    black --check --diff .
    isort --check --diff .
else
    black .
    isort .
fi

flake8 .