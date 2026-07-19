#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://127.0.0.1}"
BASE_URL="${BASE_URL%/}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-.env.production}"

response_file="$(mktemp)"
trap 'rm -f "$response_file"' EXIT

curl --fail --silent --show-error \
  --header 'Content-Type: application/json' \
  --request POST \
  --data '{"job_type":"noop","payload":{"proof":"production-worker-smoke"}}' \
  --output "$response_file" \
  "$BASE_URL/worker/jobs"

job_id="$(python3 - "$response_file" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["job_id"])
PY
)"

echo "[worker-proof] enqueued job=$job_id"

for attempt in $(seq 1 30); do
  curl --fail --silent --show-error --output "$response_file" "$BASE_URL/worker/jobs/$job_id"
  status="$(python3 - "$response_file" <<'PY'
import json
import sys
with open(sys.argv[1], encoding="utf-8") as handle:
    print(json.load(handle)["job"]["status"])
PY
)"
  echo "[worker-proof] job=$job_id status=$status attempt=$attempt"
  if [ "$status" = "completed" ]; then
    cat "$response_file"
    echo
    echo "[worker-proof] completed"
    exit 0
  fi
  if [ "$status" = "dead_letter" ]; then
    cat "$response_file"
    echo
    break
  fi
  sleep 2
done

echo "[worker-proof] job did not complete: $job_id"
if command -v docker >/dev/null 2>&1; then
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" logs --tail=180 worker api redis db || true
fi
exit 1
