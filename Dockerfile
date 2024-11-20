FROM python:3.13-slim AS builder
WORKDIR /src
RUN pip install poetry poetry-plugin-bundle --no-cache-dir
COPY . .
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-cache --no-ansi --no-interaction --without=dev

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /src/.venv .
COPY . .
VOLUME [ "/data" ]

ARG VCS_TAG
ENV VCS_TAG=${VCS_TAG}

ENV DATABASE_PATH='/data/database.pickle'
EXPOSE 8080
CMD ["./bin/python3", "sozluk/__init__.py"]