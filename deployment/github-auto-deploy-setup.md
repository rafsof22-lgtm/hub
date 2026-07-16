# GitHub Auto Deploy Setup

Last updated: 2026-07-16

## Purpose

This is the current repo-side setup guide for DigitalOcean auto-deploy. The deployment scaffold, workflow, SSH path, remote sync, host bootstrap, and IP-based public runtime endpoints are proven for the current scaffold.

## Current Proven Deployment

- Workflow run: `29485379774` / `DigitalOcean Auto Deploy #89`
- Job: `87578507636`
- Commit deployed: `d3aaf301334450cf1a216961c76c620c5aba6d7a`
- Target: `root@134.199.144.115:22`
- App dir: `/opt/xrp-hbar-apex`
- Proof URL: `http://134.199.144.115`
- Public endpoints:
  - `/health` -> `200`
  - `/ready` -> `200`
  - `/deployment/status` -> `200`

## Required GitHub Actions Values

The workflow currently pins the non-secret proof values in repo code to avoid stale variable drift.

| name | current proof value | proof method |
|---|---|---|
| `DIGITALOCEAN_HOST` | `134.199.144.115` | deploy step reached the expected host |
| `DIGITALOCEAN_USER` | `root` | SSH deploy connected as root |
| `DIGITALOCEAN_PORT` | `22` | SSH deploy connected |
| `APP_DIR` | `/opt/xrp-hbar-apex` | remote git reset ran there |
| `BASE_URL` | `http://134.199.144.115` | post-deploy endpoint checks passed |
| `DIGITALOCEAN_SSH_KEY` | Actions secret only | private key parsed and matched the droplet-authorized public key |

Do not commit secrets. Do not paste secrets into issues, docs, logs, or chat.

## Required Droplet State

These are proven operationally for the current scaffold because the deploy run completed:

- Git installed.
- Docker installed.
- Docker Compose plugin available.
- App directory exists and can be reset at `/opt/xrp-hbar-apex`.
- `deployment/runtime-scaffold-pack/.env.production` exists on the droplet with values sufficient for the current scaffold.
- Ports 80 and 443 are available for Docker Caddy.

## Required `.env.production` Values On Host

Keep these host-only. Do not commit them.

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`
- `POSTGRES_URL`
- `REDIS_URL`
- `XRP_HBAR_APEX_BASE_URL`
- Optional until route needs it: `OPENAI_API_KEY`, Google, n8n, and other future integrations.

## Verification Order

1. Workflow file validates deploy files. Proven.
2. SSH key is parsed and accepted by `ssh-keygen`. Proven.
3. GitHub Actions connects to the droplet over SSH. Proven.
4. Remote repo sync resets to `origin/main`. Proven.
5. `deploy.sh` runs on the droplet. Proven.
6. Docker Compose services start. Proven.
7. Local host `/health`, `/ready`, and `/deployment/status` pass. Inferred through deploy completion.
8. Public `BASE_URL` `/health`, `/ready`, and `/deployment/status` pass. Proven.
9. VTI smoke proof runs. Pending.
10. Email/newsletter intake proof runs. Pending.

## Current Rule

A workflow run is not deployment proof by itself. Only mark a gate proven when the run logs show that gate passed. For the current scaffold, the core deploy path is proven by run `29485379774`; VTI and email/newsletter live layers still need separate smoke proof.
