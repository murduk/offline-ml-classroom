#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
archive="${1:-classroom-images.tar}"
docker image inspect offline-ml-hub:1.0 offline-ml-student:1.0 >/dev/null
docker save -o "$archive" offline-ml-hub:1.0 offline-ml-student:1.0
printf 'Saved images to %s. Also transfer the project folder and your .env.\n' "$archive"
printf 'Images do not include existing student work or accounts; those live in volumes.\n'
