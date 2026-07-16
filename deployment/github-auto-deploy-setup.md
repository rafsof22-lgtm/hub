# GitHub Auto Deploy Setup

Last updated: 2026-07-16

## Purpose

This is the current repo-side setup guide for DigitalOcean auto-deploy. It replaces stale notes that implied the deployment scaffold or workflow was missing.

## Required GitHub Actions Values

| name | type | expected value | proof method |
|---|---|---|---|
| `DIGITALOCEAN_HOST` | variable or secret | `134.199.144.115` | deploy step reaches the expected host |
| `DIGITALOCEAN_USER` | variable or secret | `root` unless host user changed | SSH deploy connects |
| `DIGITALOCEAN_PORT` | variable or secret | `22` unless SSH port changed | SSH deploy connects |
| `APP_DIR` | variable or secret | `/opt/xrp-hbar-apex` | remote git reset runs there |
| `BASE_URL` | variable or secret | correct live URL, including scheme | post-deploy endpoint checks pass |
| `DIGITALOCEAN_SSH_KEY` | secret only | full private key matching droplet-authorized public key | Prepare SSH key and SSH deploy pass |

Do not commit secrets. Do not paste secrets into issues, docs, logs, or chat.

## Required Droplet State

- Git installed.
- Docker installed.
- Docker Compose plugin or `docker-compose` installed.
- App directory can be created or updated at `/opt/xrp-hbar-apex`.
- `deployment/runtime-scaffold-pack/.env.production` exists on the droplet.
- `.env.production` contains real values and no placeholders.
- Ports 80 and 443 are open and available for Docker Caddy.

## Required `.env.production` Values On Host

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`
- `POSTGRES_URL`
- `REDIS_URL`
- `XRP_HBAR_APEX_BASE_URL`
- Optional until route needs it: `OPENAI_API_KEY`, Google, n8n, and other future integrations.

## Verification Order

1. Workflow file validates deploy files.
2. SSH key is parsed and accepted by `ssh-keygen`.
3. GitHub Actions connects to the droplet over SSH.
4. Remote repo sync resets to `origin/main`.
5. `deploy.sh` runs on the droplet.
6. Docker Compose services start.
7. Local host `/health`, `/ready`, and `/deployment/status` pass.
8. Public `BASE_URL` `/health`, `/ready`, and `/deployment/status` pass.
9. VTI smoke proof runs.
10. Email/newsletter intake proof runs.

## Current Rule

A workflow run is not deployment proof by itself. Only mark a gate proven when the run logs show that gate passed.
