#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for image in offline-ml-hub:1.0 offline-ml-student:1.0; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    printf 'Missing image: %s. Build online or load your saved image archive.\n' "$image" >&2
    exit 1
  fi
done
docker run --rm --pull never --network none --entrypoint sh offline-ml-hub:1.0 \
  -c 'python -m pip check && jupyterhub --show-config -f /etc/jupyterhub/jupyterhub_config.py >/dev/null && configurable-http-proxy --version'
docker run --rm --pull never --network none --entrypoint python offline-ml-student:1.0 \
  /opt/classroom/check_environment.py
