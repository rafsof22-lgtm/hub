#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/opt/xrp-hbar-apex"
RUNTIME_DIR="$APP_DIR/deployment/runtime-scaffold-pack"
SERVICE_PATH="/etc/systemd/system/xrp-hbar-auto-deploy.service"
TIMER_PATH="/etc/systemd/system/xrp-hbar-auto-deploy.timer"
RUNNER_PATH="/usr/local/bin/xrp-hbar-auto-deploy"

cat > "$RUNNER_PATH" <<'EOF'
#!/usr/bin/env bash
set -Eeuo pipefail
APP_DIR="/opt/xrp-hbar-apex"
RUNTIME_DIR="$APP_DIR/deployment/runtime-scaffold-pack"
LOG_FILE="/var/log/xrp-hbar-auto-deploy.log"
{
  echo "== $(date -Is) auto-deploy start =="
  cd "$APP_DIR"
  BEFORE="$(git rev-parse HEAD 2>/dev/null || true)"
  git fetch origin main
  git reset --hard origin/main
  AFTER="$(git rev-parse HEAD)"
  cd "$RUNTIME_DIR"
  chmod +x deploy.sh
  ./deploy.sh
  for path in /health /ready /deployment/status; do
    curl -fsS "http://127.0.0.1${path}" >/dev/null
  done
  echo "deployed $BEFORE -> $AFTER"
  echo "== $(date -Is) auto-deploy ok =="
} >> "$LOG_FILE" 2>&1
EOF
chmod +x "$RUNNER_PATH"

cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=XRP/HBAR Apex auto-pull deploy
Wants=network-online.target docker.service
After=network-online.target docker.service

[Service]
Type=oneshot
ExecStart=$RUNNER_PATH
EOF

cat > "$TIMER_PATH" <<'EOF'
[Unit]
Description=Run XRP/HBAR Apex auto-pull deploy every 2 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
AccuracySec=30s
Persistent=true
Unit=xrp-hbar-auto-deploy.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now xrp-hbar-auto-deploy.timer
systemctl start xrp-hbar-auto-deploy.service
systemctl status xrp-hbar-auto-deploy.timer --no-pager
systemctl status xrp-hbar-auto-deploy.service --no-pager || true

echo "== recent auto-deploy log =="
tail -80 /var/log/xrp-hbar-auto-deploy.log || true

echo "== endpoint proof =="
for path in /health /ready /deployment/status; do
  echo "--- http://127.0.0.1${path}"
  curl -fsS "http://127.0.0.1${path}"
  echo
  echo "--- http://134.199.144.115${path}"
  curl -fsS "http://134.199.144.115${path}"
  echo
done
