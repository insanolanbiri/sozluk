#!/bin/sh

set -e

exec .venv/bin/uwsgi -w sozluk.app:app --http 0.0.0.0:8080 --master -p $((${THREADS:-$(nproc)}))