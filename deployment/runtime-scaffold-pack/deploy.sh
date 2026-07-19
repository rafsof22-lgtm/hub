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
for service in caddy nginx apache2 envoy; do
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files "${service}.service" >/dev/null 2>&1; then
    systemctl stop "$service" 2>/dev/null || true
    systemctl disable "$service" 2>/dev/null || true
  fi
done

$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml down --remove-orphans >/dev/null 2>&1 || true

for port in 80 443; do
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  elif command -v lsof >/dev/null 2>&1; then
    lsof -ti tcp:"${port}" | xargs -r kill -TERM 2>/dev/null || true
  elif command -v ss >/dev/null 2>&1; then
    pids="$(ss -ltnp 2>/dev/null | awk -v port=":${port}" '$4 ~ port {print $0}' | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' | sort -u)"
    if [ -n "$pids" ]; then
      echo "$pids" | xargs -r kill -TERM 2>/dev/null || true
    fi
  fi
done

sleep 2
if command -v ss >/dev/null 2>&1; then
  occupied="$(ss -ltnp 2>/dev/null | grep -E ':(80|443)\b' || true)"
  if [ -n "$occupied" ]; then
    echo "[deploy] ports still occupied after graceful stop; forcing cleanup"
    echo "$occupied"
    echo "$occupied" | sed -n 's/.*pid=\([0-9][0-9]*\).*/\1/p' | sort -u | xargs -r kill -KILL 2>/dev/null || true
  fi
fi

echo "[deploy] removing legacy xrp_hbar_apex containers if present"
for container in xrp_hbar_apex_caddy xrp_hbar_apex_app xrp_hbar_apex_postgres xrp_hbar_apex_redis; do
  if docker ps -a --format '{{.Names}}' | grep -Fxq "$container"; then
    docker rm -f "$container" >/dev/null 2>&1 || true
  fi
done

echo "[deploy] removing stale runtime-scaffold-pack containers if present"
stale_runtime_containers="$(docker ps -a --format '{{.Names}}' | grep '^runtime-scaffold-pack-' || true)"
if [ -n "$stale_runtime_containers" ]; then
  echo "$stale_runtime_containers" | while IFS= read -r container; do
    if [ -n "$container" ]; then
      echo "[deploy] removing stale container: $container"
      docker rm -f "$container" >/dev/null 2>&1 || true
    fi
  done
fi
if docker network inspect runtime-scaffold-pack_default >/dev/null 2>&1; then
  docker network rm runtime-scaffold-pack_default >/dev/null 2>&1 || true
fi

echo "[deploy] pulling latest images"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml pull || true

echo "[deploy] starting services and applying migrations"
if ! $COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml up -d --remove-orphans --build --force-recreate; then
  echo "[deploy] compose up failed; retrying once after explicit stale container cleanup"
  retry_runtime_containers="$(docker ps -a --format '{{.Names}}' | grep '^runtime-scaffold-pack-' || true)"
  if [ -n "$retry_runtime_containers" ]; then
    echo "$retry_runtime_containers" | while IFS= read -r container; do
      if [ -n "$container" ]; then
        echo "[deploy] retry cleanup container: $container"
        docker rm -f "$container" >/dev/null 2>&1 || true
      fi
    done
  fi
  if docker network inspect runtime-scaffold-pack_default >/dev/null 2>&1; then
    docker network rm runtime-scaffold-pack_default >/dev/null 2>&1 || true
  fi
  $COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml up -d --remove-orphans --build --force-recreate
fi

echo "[deploy] current status"
$COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml ps -a

echo "[deploy] waiting for local proof endpoints"
for path in health ready deployment/status migrations/status worker/status outbound/status; do
  success=0
  for attempt in $(seq 1 45); do
    if curl --fail --silent --show-error "http://127.0.0.1/${path}" >/dev/null 2>&1; then
      success=1
      break
    fi
    sleep 2
  done

  if [ "$success" -ne 1 ]; then
    echo "[deploy] local endpoint failed: /${path}"
    $COMPOSE_CMD --env-file .env.production -f docker-compose.prod.yml logs --tail=160
    exit 1
  fi
done

echo "[deploy] migration ledger"
curl --fail --silent --show-error http://127.0.0.1/migrations/status
echo

echo "[deploy] worker heartbeat"
curl --fail --silent --show-error http://127.0.0.1/worker/status
echo

echo "[deploy] active public listeners"
if command -v ss >/dev/null 2>&1; then
  ss -ltnp | grep -E ':(80|443)\b' || true
fi

echo "[deploy] complete"
echo "Next: verify all public proof gates on the live base URL."
