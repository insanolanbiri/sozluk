FROM python:3.13-slim AS builder
WORKDIR /app

RUN pip install poetry --no-cache-dir

RUN mkdir sozluk
RUN touch sozluk/__init__.py
RUN touch README.md
COPY pyproject.toml .

ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-cache --no-ansi --no-interaction --without=dev

FROM python:3.13-slim
LABEL maintainer="Eren Akgün <iobthedev@outlook.com>"
WORKDIR /app

RUN apt update; apt install -y uwsgi-core; apt remove -y uwsgi-core; apt clean

COPY --from=builder /app/.venv .venv
COPY . .
VOLUME [ "/data" ]

ARG VCS_TAG
ENV VCS_TAG=${VCS_TAG}

ENV DATABASE_URL='sqlite:////data/sozluk.sqlite'
ENV THREADS=''

EXPOSE 8080
ENTRYPOINT [ "./entrypoint.sh" ]