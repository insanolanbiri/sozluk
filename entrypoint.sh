#!/bin/sh

set -e

exec .venv/bin/gunicorn -k gevent sozluk.app:app -b 0.0.0.0:8080 -w $((${THREADS:-$(nproc)}))