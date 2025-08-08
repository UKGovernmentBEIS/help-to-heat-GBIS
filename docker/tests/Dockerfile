FROM public.ecr.aws/docker/library/python:3.11.13-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ=UTC

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update -y && apt install -y postgresql-client curl

RUN curl -o /bin/wait-for-db https://github.com/palfrey/wait-for-db/releases/download/v1.2.0/wait-for-db-linux-x86
RUN chmod +x /bin/wait-for-db

COPY ./docker/tests/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./docker/tests/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/tests/check-code.sh /check-code.sh
RUN chmod +x /check-code.sh

COPY ./envs/web.template ./envs/web

COPY poetry.lock pyproject.toml /app/

WORKDIR /app/

RUN pip install poetry && \
  poetry config virtualenvs.create false && \
  poetry install --with dev

COPY ./ /app/

RUN \
    DJANGO_SETTINGS_MODULE=help_to_heat.settings_base \
    DJANGO_SECRET_KEY="temp" \
    python manage.py collectstatic --no-input

ENTRYPOINT ["sh","/entrypoint.sh"]
CMD ["sh","/start.sh"]
