FROM public.ecr.aws/docker/library/python:3.11.9-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ=UTC
ENV CONN_MAX_AGE=300

ARG BASE_URL

ENV BASE_URL=${BASE_URL}

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN curl -o /bin/wait-for-db https://github.com/palfrey/wait-for-db/releases/download/v1.2.0/wait-for-db-linux-x86
RUN chmod +x /bin/wait-for-db

RUN apt-get update
RUN apt-get install -y gettext \
# this ensures psql is available on the container
# we may use this in support when connecting to EC2 container & we need to query the database
    postgresql-client

COPY ./docker/web/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/web/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./envs/web.template ./envs/web

COPY poetry.lock pyproject.toml /app/

WORKDIR /app/

RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --with deployment

COPY ./ /app/

RUN groupadd -r appuser && useradd -r -g appuser appuser && chown -R appuser:appuser /app
USER appuser

RUN \
    DJANGO_SETTINGS_MODULE=help_to_heat.settings_base \
    DJANGO_SECRET_KEY="temp" \
    python manage.py collectstatic --no-input

EXPOSE 8012 5678

ENTRYPOINT ["sh","/entrypoint.sh"]
CMD ["sh","/start.sh"]
