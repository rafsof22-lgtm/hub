#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/xrp-hbar-apex}"
REPO_URL="${REPO_URL:-https://github.com/rafsof22-lgtm/hub.git}"
BRANCH="${BRANCH:-main}"
RUNTIME_DIR="$APP_DIR/deployment/runtime-scaffold-pack"

log() { printf '[host-self-heal] %s\n' "$*"; }

require_root() {
  if [ "${EUID:-$(id -u)}" -ne 0 ]; then
    log "run as root or with sudo"
    exit 1
  fi
}

install_basics() {
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y ca-certificates curl git ufw lsof psmisc
  if ! command -v docker >/dev/null 2>&1; then
    apt-get install -y docker.io docker-compose-v2 || apt-get install -y docker.io docker-compose-plugin
    systemctl enable --now docker
  fi
  if ! docker compose version >/dev/null 2>&1 && ! command -v docker-compose >/dev/null 2>&1; then
    apt-get install -y docker-compose-v2 || apt-get install -y docker-compose-plugin || apt-get install -y docker-compose
  fi
}

sync_repo() {
  if [ ! -d "$APP_DIR/.git" ]; then
    mkdir -p "$APP_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
  fi
  cd "$APP_DIR"
  git fetch origin "$BRANCH"
  git checkout "$BRANCH"
  git reset --hard "origin/$BRANCH"
}

ensure_env() {
  cd "$RUNTIME_DIR"
  if [ ! -f .env.production ]; then
    cp .env.production.example .env.production
    chmod 600 .env.production
    log "created .env.production from example"
  fi

  missing=0
  for name in DOMAIN BASE_URL JOB_SIGNING_SECRET POSTGRES_PASSWORD; do
    value="$(grep -E "^${name}=" .env.production | tail -n 1 | cut -d= -f2- || true)"
    if [ -z "$value" ]; then
      log "missing required value in .env.production: $name"
      missing=1
    fi
  done

  if grep -Eq 'YOUR-|change-me|change_me|example\.com' .env.production; then
    log ".env.production still contains core placeholder values"
    missing=1
  fi

  if [ "$missing" -ne 0 ]; then
    log "edit $RUNTIME_DIR/.env.production with real core runtime values, then rerun this script"
    exit 2
  fi

  gmail_pending=0
  for name in GMAIL_OAUTH_CLIENT_ID GMAIL_OAUTH_CLIENT_SECRET GMAIL_OAUTH_REFRESH_TOKEN; do
    value="$(grep -E "^${name}=" .env.production | tail -n 1 | cut -d= -f2- || true)"
    case "$value" in
      ""|your-client-id.apps.googleusercontent.com|your-client-secret|your-refresh-token)
        gmail_pending=1
        ;;
    esac
  done
  if [ "$gmail_pending" -ne 0 ]; then
    log "Gmail runtime credentials are still pending; route repair can continue, but Gmail proof will remain blocked"
  fi
}

free_public_ports() {
  for service in caddy nginx apache2 envoy; do
    if systemctl list-unit-files "${service}.service" >/dev/null 2>&1; then
      systemctl stop "$service" 2>/dev/null || true
      systemctl disable "$service" 2>/dev/null || true
    fi
  done
  fuser -k 80/tcp 443/tcp >/dev/null 2>&1 || true
}

run_deploy() {
  cd "$RUNTIME_DIR"
  chmod +x deploy.sh worker-proof.sh
  ./deploy.sh
}

local_required_check() {
  path="$1"
  log "local check /$path"
  curl --fail --silent --show-error "http://127.0.0.1/$path" | head -c 1600
  printf '\n'
}

local_diagnostic_check() {
  path="$1"
  log "local diagnostic /$path"
  body_file="$(mktemp)"
  status="$(curl --silent --show-error --output "$body_file" --write-out '%{http_code}' "http://127.0.0.1/$path" || true)"
  printf 'status=%s ' "$status"
  head -c 1600 "$body_file" | tr '\n' ' '
  printf '\n'
  rm -f "$body_file"
  case "$status" in
    2*) log "diagnostic /$path passed" ;;
    *) log "diagnostic /$path did not pass; public proof gates will enforce the final Gmail status" ;;
  esac
}

verify_local() {
  for path in health ready deployment/status vti/status email/newsletter/status evidence-pack/status source-discovery/status migrations/status worker/status outbound/status; do
    local_required_check "$path"
  done
  local_diagnostic_check email/newsletter/gmail/status
}

verify_worker_execution() {
  cd "$RUNTIME_DIR"
  BASE_URL="http://127.0.0.1" ./worker-proof.sh
}

print_public_checks() {
  base_url="$(grep -E '^BASE_URL=' "$RUNTIME_DIR/.env.production" | tail -n 1 | cut -d= -f2- | sed 's:/*$::')"
  log "public checks to run from outside host:"
  for path in health ready deployment/status vti/status email/newsletter/status email/newsletter/gmail/status evidence-pack/status source-discovery/status migrations/status worker/status outbound/status; do
    printf 'curl -i %s/%s\n' "$base_url" "$path"
  done
}

main() {
  require_root
  install_basics
  sync_repo
  ensure_env
  free_public_ports
  run_deploy
  verify_local
  verify_worker_execution
  print_public_checks
  log "complete"
}

main "$@"
