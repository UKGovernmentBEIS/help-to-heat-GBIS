## Initial Setup
1. From the project root, run `cp envs/web.template envs/web`
2. Populate the OS API key into the OS_API_KEY variable. The key can be found in keeper

## Using Docker

1. [Install Docker](https://docs.docker.com/get-docker/) on your machine
2. `docker-compose up --build --force-recreate web`
3. It's now available at: http://localhost:8012/

Migrations are run automatically at startup, and suppliers are added automatically at startup


## Running tests

    make test


## Checking code

    make check-python-code
