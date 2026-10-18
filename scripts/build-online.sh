#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; fi
docker info >/dev/null
docker compose --profile build config --quiet
docker compose --profile build build --pull hub student-image
bash scripts/check-offline.sh
printf '\nImages built and offline notebook checks passed.\n'
