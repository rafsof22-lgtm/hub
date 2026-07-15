#!/usr/bin/env bash
set -Eeuo pipefail

APP_DIR="/opt/xrp-hbar-apex"
REPO_URL="https://github.com/rafsof22-lgtm/hub.git"
BRANCH="main"
PUBLIC_IP="134.199.144.115"
DOMAIN="${DOMAIN:-134-199-144-115.sslip.io}"
BASE_URL="https://${DOMAIN}"
CODEX_PUBKEY='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIKzJU+XUrk9rlOYCGcI8NNiUjmvx7+qpbRiWsMNEq2M1 xrp-hbar-apex-codex-2026-07-15'
GH_DEPLOY_KEY="/root/.ssh/github_actions_xrp_hbar"

printf '\n== 1. Prepare SSH access ==\n'
mkdir -p /root/.ssh
chmod 700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
if ! grep -Fq "$CODEX_PUBKEY" /root/.ssh/authorized_keys; then
  printf '%s\n' "$CODEX_PUBKEY" >> /root/.ssh/authorized_keys
fi

if [ ! -f "$GH_DEPLOY_KEY" ]; then
  ssh-keygen -t ed25519 -N '' -C 'github-actions-xrp-hbar-apex' -f "$GH_DEPLOY_KEY"
fi
cat "$GH_DEPLOY_KEY.pub" >> /root/.ssh/authorized_keys
sort -u /root/.ssh/authorized_keys -o /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

printf '\n== 2. Install system packages ==\n'
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg lsb-release git ufw openssl

printf '\n== 3. Firewall ==\n'
ufw allow OpenSSH || true
ufw allow 80/tcp || true
ufw allow 443/tcp || true
ufw --force enable
ufw status

printf '\n== 4. Install Docker + Compose plugin ==\n'
install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  chmod a+r /etc/apt/keyrings/docker.gpg
fi
. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker
docker --version
docker compose version

printf '\n== 5. Clone or update repo ==\n'
mkdir -p "$APP_DIR"
if [ ! -d "$APP_DIR/.git" ]; then
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"
git fetch origin "$BRANCH"
git checkout "$BRANCH"
git reset --hard "origin/$BRANCH"

printf '\n== 6. Create production env ==\n'
cd "$APP_DIR/deployment/runtime-scaffold-pack"
JOB_SIGNING_SECRET="$(openssl rand -hex 32)"
POSTGRES_PASSWORD="$(openssl rand -hex 32)"
cat > .env.production <<EOF
APP_ENV=production
DOMAIN=${DOMAIN}
BASE_URL=${BASE_URL}
OPENAI_API_KEY=
JOB_SIGNING_SECRET=${JOB_SIGNING_SECRET}
PORT=8080
POSTGRES_URL=postgres://postgres:${POSTGRES_PASSWORD}@db:5432/xrp_hbar_apex
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_URL=redis://redis:6379/0
XRP_HBAR_APEX_ENV=production
XRP_HBAR_APEX_BASE_URL=${BASE_URL}
GOOGLE_SERVICE_ACCOUNT_JSON=
GOOGLE_SHEET_ID=
N8N_WEBHOOK_BASE_URL=
N8N_WEBHOOK_SECRET=
EOF
chmod 600 .env.production

printf '\n== 7. Deploy stack ==\n'
chmod +x deploy.sh
./deploy.sh

printf '\n== 8. Verify containers ==\n'
docker compose --env-file .env.production -f docker-compose.prod.yml ps

printf '\n== 9. Verify local endpoints ==\n'
for path in /health /ready /deployment/status; do
  for i in $(seq 1 30); do
    if curl -fsS "http://127.0.0.1${path}" >/tmp/xrp_hbar_check 2>/tmp/xrp_hbar_err; then
      printf 'PASS %s\n' "$path"
      cat /tmp/xrp_hbar_check
      printf '\n'
      break
    fi
    if [ "$i" = 30 ]; then
      printf 'FAIL %s\n' "$path"
      cat /tmp/xrp_hbar_err || true
      exit 1
    fi
    sleep 5
  done
done

printf '\n== 10. Public endpoint quick check ==\n'
for path in /health /ready /deployment/status; do
  curl -k -i "${BASE_URL}${path}" || true
  printf '\n'
done

printf '\n== 11. Add these GitHub Actions secrets in GitHub UI ==\n'
printf 'DIGITALOCEAN_HOST=%s\n' "$PUBLIC_IP"
printf 'DIGITALOCEAN_USER=root\n'
printf 'DIGITALOCEAN_PORT=22\n'
printf 'APP_DIR=%s\n' "$APP_DIR"
printf 'BASE_URL=%s\n' "$BASE_URL"
printf '\nDIGITALOCEAN_SSH_KEY: copy only the OpenSSH private key printed between COPY_START and COPY_END. Do not paste it into chat.\n'
printf 'COPY_START\n'
cat "$GH_DEPLOY_KEY"
printf 'COPY_END\n'

printf '\n== DONE ==\n'
printf 'Manual deploy complete if all local endpoint checks passed. Auto-deploy completes after GitHub Actions secrets are added and a new push/workflow run passes.\n'
