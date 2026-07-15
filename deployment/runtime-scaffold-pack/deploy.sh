#!/usr/bin/env sh
set -eu

echo "[deploy] starting VPS deploy"

if [ ! -f .env.production ]; then
  echo "[deploy] missing .env.production"
  echo "Copy .env.production.example to .env.production and fill in real values first."
  exit 1
fi

if grep -Eq 'YOUR-|change-me|change_me|example\.com' .env.production; then
  echo "[deploy] .env.production still contains placeholder values"
  echo "Fill DOMAIN, BASE_URL, JOB_SIGNING_SECRET, and POSTGRES_PASSWORD before production deploy."
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  echo "[deploy] docker is not installed"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "[deploy] docker compose is not installed"
  exit 1
fi

echo "[deploy] pulling latest images"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml pull || true

echo "[deploy] starting services"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml up -d --remove-orphans --build

echo "[deploy] current status"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml ps

echo "[deploy] complete"
echo "Next: verify /health, /ready, and /deployment/status on your live domain."
