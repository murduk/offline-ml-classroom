#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; fi
docker info >/dev/null
docker compose config --quiet
for image in offline-ml-hub:1.0 offline-ml-student:1.0; do
  if ! docker image inspect "$image" >/dev/null 2>&1; then
    printf 'Missing image: %s. Run scripts/build-online.sh while online, or docker load your image archive.\n' "$image" >&2
    exit 1
  fi
done
docker compose up -d --no-build --pull never hub
printf '\nHub starting. Check: docker compose ps\n'
printf 'On the host: http://localhost:<CLASSROOM_PORT, default 8000>/hub/login\n'
printf 'Students: http://<HOST-LAN-IP>:<CLASSROOM_PORT, default 8000>/hub/login\n'
printf 'First run: create the ADMIN_USER account at /hub/signup before students connect.\n'
