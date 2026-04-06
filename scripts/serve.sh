#!/usr/bin/env bash
# Run granian ASGI server with deployed settings.
# Set LOCAL_DEPLOY=1 to relax HTTPS/secure-cookie requirements for local testing.
set -euo pipefail

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.deployed}"
export LOCAL_DEPLOY="${LOCAL_DEPLOY:-1}"

exec uv run granian config.asgi:application \
    --interface asgi \
    --host "${GRANIAN_HOST:-0.0.0.0}" \
    --port "${GRANIAN_PORT:-8000}" \
    --workers "${GRANIAN_WORKERS:-4}" \
    --static-path-route /static \
    --static-path-mount staticfiles \
    --access-log
