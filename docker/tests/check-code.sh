#!/bin/bash

set -o errexit

if [[ $1 = "--format" ]]; then
    black .
    isort .
else
    black --check --diff .
    isort --check --diff .
fi

flake8 .