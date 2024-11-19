FROM python:3.13-slim AS builder
WORKDIR /src
RUN pip install poetry poetry-plugin-bundle --no-cache-dir
COPY . .
RUN poetry bundle venv --no-cache --no-interaction --without=dev /venv

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /venv .
COPY . .
VOLUME [ "/data" ]

ARG VCS_TAG
ENV VCS_TAG=${VCS_TAG}

ENV DATABASE_PATH='/data/database.pickle'
EXPOSE 8080
CMD ["./bin/python3", "sozluk/__init__.py"]
