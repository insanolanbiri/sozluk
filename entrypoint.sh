#!/bin/sh

set -e

exec .venv/bin/gunicorn sozluk.app:app -b 0.0.0.0:8080 -w $((${THREADS:-$(nproc)}))