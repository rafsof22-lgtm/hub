# Deployment Secret Placement Map

Last updated: 2026-07-16

## Safety Rule

Secrets must not be committed to this repository and must not be copied into issues, comments, docs, or chat.

Public SSH keys and fingerprints are safe to record for verification. Private key blocks are never safe to record.

## GitHub Actions Secrets And Variables

| item | belongs in | secret? | notes |
|---|---|---:|---|
| `DIGITALOCEAN_SSH_KEY` | GitHub Actions Secret | yes | full private key block or base64-encoded private key block only; current Actions key parses but is not accepted by the droplet |
| `DIGITALOCEAN_HOST` | GitHub Actions Variable preferred | no | expected `134.199.144.115` |
| `DIGITALOCEAN_USER` | GitHub Actions Variable preferred | no | expected `root` unless changed |
| `DIGITALOCEAN_PORT` | GitHub Actions Variable preferred | no | expected `22` unless changed |
| `APP_DIR` | GitHub Actions Variable preferred | no | expected `/opt/xrp-hbar-apex` |
| `BASE_URL` | GitHub Actions Variable or Secret | usually no | must include `http://` or `https://`; must target live app |
| `DIGITALOCEAN_ACCESS_TOKEN` | GitHub Actions Secret | yes | only needed for diagnostics workflow |
| `DIGITALOCEAN_DROPLET_ID` | GitHub Actions Variable preferred | no | expected `584697763` if diagnostics workflow is used |

## Current SSH Auth Proof

Latest Actions proof:

- Run `29469547563` passed private-key parsing and printed deploy fingerprint `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I (ED25519)`.
- The derived public key was `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.
- The deploy step failed with `Permission denied (publickey)`.

This means the secret is syntactically valid, but the matching public key is not accepted for the configured droplet SSH user. The fix is to authorize that public key on the droplet for the configured user, expected `root`, or replace the secret with a private key whose public key is already authorized on the droplet.

## Droplet-Only `.env.production`

These values belong on the host at:

`/opt/xrp-hbar-apex/deployment/runtime-scaffold-pack/.env.production`

| item | secret? | required for |
|---|---:|---|
| `DOMAIN` | no | Caddy domain routing |
| `BASE_URL` | no | service self-reference and proof context |
| `JOB_SIGNING_SECRET` | yes | future job/webhook signing |
| `POSTGRES_PASSWORD` | yes | Postgres container |
| `POSTGRES_URL` | yes | application database connection |
| `REDIS_URL` | no/low | Redis connection |
| `XRP_HBAR_APEX_BASE_URL` | no | module base URL |
| `OPENAI_API_KEY` | yes | future model-backed routes, not current basic health |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | yes | future Google workflows |
| `N8N_WEBHOOK_SECRET` | yes | future n8n webhooks |

## Verification Without Exposing Secrets

- `DIGITALOCEAN_SSH_KEY`: workflow step `Prepare SSH key` passes.
- SSH auth: workflow step `Deploy to DigitalOcean droplet over SSH` reaches remote commands and prints `[remote] synced_commit=...`.
- `.env.production`: `deploy.sh` does not fail with missing value or placeholder messages.
- Postgres/Redis: `/ready` returns success locally and publicly.
- `BASE_URL`: post-deploy endpoint checks pass against all three public routes.
