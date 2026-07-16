#!/usr/bin/env sh
set -eu

echo "[deploy] starting VPS deploy"

if [ ! -f .env.production ]; then
  echo "[deploy] missing .env.production"
  echo "Copy .env.production.example to .env.production and fill in real values first."
  exit 1
fi

required_env="DOMAIN BASE_URL JOB_SIGNING_SECRET POSTGRES_PASSWORD"
for name in $required_env; do
  value="$(grep -E "^${name}=" .env.production | tail -n 1 | cut -d= -f2- || true)"
  if [ -z "$value" ]; then
    echo "[deploy] .env.production is missing required value: ${name}"
    exit 1
  fi
done

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

echo "[deploy] freeing host ports 80 and 443 for Docker Caddy"
for service in caddy nginx apache2; do
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "${service}.service" >/dev/null 2>&1; then
    systemctl stop "$service" 2>/dev/null || true
    systemctl disable "$service" 2>/dev/null || true
  fi
done

echo "[deploy] removing legacy xrp_hbar_apex containers if present"
for container in xrp_hbar_apex_caddy xrp_hbar_apex_app xrp_hbar_apex_postgres xrp_hbar_apex_redis; do
  if docker ps -a --format '{{.Names}}' | grep -Fxq "$container"; then
    docker rm -f "$container" >/dev/null 2>&1 || true
  fi
done

echo "[deploy] pulling latest images"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml pull || true

echo "[deploy] starting services"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml up -d --remove-orphans --build --force-recreate

echo "[deploy] current status"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml ps

echo "[deploy] waiting for local health endpoints"
for path in health ready deployment/status; do
  success=0
  for attempt in $(seq 1 30); do
    if curl --fail --silent --show-error "http://127.0.0.1/${path}" >/dev/null 2>&1; then
      success=1
      break
    fi
    sleep 2
  done

  if [ "$success" -ne 1 ]; then
    echo "[deploy] local endpoint failed: /${path}"
    $COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml logs --tail=120
    exit 1
  fi
done

echo "[deploy] active public listeners"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | grep -E ':(80|443)\b' || true
fi

echo "[deploy] complete"
echo "Next: verify /health, /ready, and /deployment/status on your live domain."
