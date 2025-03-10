include envs/web.template

.PHONY: reset-db
reset-db:
	docker compose up --detach ${POSTGRES_HOST}
	docker compose run ${POSTGRES_HOST} dropdb -U ${POSTGRES_USER} -h ${POSTGRES_HOST} ${POSTGRES_DB}
	docker compose run ${POSTGRES_HOST} createdb -U ${POSTGRES_USER} -h ${POSTGRES_HOST} ${POSTGRES_DB}
	docker compose kill

.PHONY: add-suppliers
add-suppliers:
	docker compose build web
	docker compose run web python manage.py add_suppliers

# -------------------------------------- Code Style  -------------------------------------

.PHONY: format-python-code
format-python-code:
	docker compose -f tests/docker-compose.yml build format-code-help-to-heat && docker compose -f tests/docker-compose.yml run --no-deps --rm format-code-help-to-heat

.PHONY: check-python-code
check-python-code:
	docker compose -f tests/docker-compose.yml build check-code-help-to-heat && docker compose -f tests/docker-compose.yml run --no-deps --rm check-code-help-to-heat

.PHONY: check-migrations
check-migrations:
	docker compose build web
	docker compose run web python manage.py migrate
	docker compose run web python manage.py makemigrations --check

.PHONY: test
test:
	docker compose -f tests/docker-compose.yml down
	docker compose -f tests/docker-compose.yml build tests-help-to-heat help-to-heat-test-db && docker compose -f tests/docker-compose.yml run --rm tests-help-to-heat
	docker compose -f tests/docker-compose.yml down

.PHONY: psql
psql:
	docker compose run ${POSTGRES_HOST} psql -U ${POSTGRES_USER} -h ${POSTGRES_HOST} ${POSTGRES_DB}

.PHONY: extract-translations
extract-translations:
	docker compose build web
	docker compose run web python manage.py makemessages --locale cy --ignore venv

.PHONY: compile-translations
compile-translations:
	docker compose build web
	docker compose run web python manage.py compilemessages --ignore venv
