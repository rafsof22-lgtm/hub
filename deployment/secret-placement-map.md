# Deployment Secret Placement Map

Last updated: 2026-07-16

## Safety Rule

Secrets must not be committed to this repository and must not be copied into issues, comments, docs, or chat.

Public SSH keys and fingerprints are safe to record for verification. Private key blocks, passwords, reset tokens, and one-time credentials are never safe to record.

## GitHub Actions Secrets And Variables

| item | belongs in | secret? | notes |
|---|---|---:|---|
| `DIGITALOCEAN_SSH_KEY` | GitHub Actions Secret | yes | must be a full private OpenSSH key block or base64-encoded private key block; latest rerun job `87568284263` failed because this value did not parse as either |
| `DIGITALOCEAN_HOST` | GitHub Actions Variable preferred | no | expected `134.199.144.115` |
| `DIGITALOCEAN_USER` | GitHub Actions Variable preferred | no | expected `root` unless changed |
| `DIGITALOCEAN_PORT` | GitHub Actions Variable preferred | no | expected `22` unless changed |
| `APP_DIR` | GitHub Actions Variable preferred | no | expected `/opt/xrp-hbar-apex` |
| `BASE_URL` | GitHub Actions Variable or Secret | usually no | must include `http://` or `https://`; must target live app |
| `DIGITALOCEAN_ACCESS_TOKEN` | GitHub Actions Secret | yes | only needed for diagnostics workflow |
| `DIGITALOCEAN_DROPLET_ID` | GitHub Actions Variable preferred | no | expected `584697763` if diagnostics workflow is used |

## Current SSH Key Proof

Latest exercised Actions proof available to this agent:

- Run `29469547563`, latest job attempt `87568284263`, failed at `Prepare SSH key`.
- Exact error: `DIGITALOCEAN_SSH_KEY must contain a full private key block, or a base64-encoded private key block`.
- `Deploy to DigitalOcean droplet over SSH` and public endpoint checks were skipped.

Previous attempt evidence still matters as history:

- Prior job `87562750570` passed private-key parsing and derived public key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.
- DigitalOcean account key list contains that public key as key id `57820900`, name `github-actions-deploy-2026-07-16-active`, fingerprint `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`.
- That prior job then failed with `Permission denied (publickey)`, meaning account-level key presence alone did not prove existing-droplet authorization.

Current first blocker is now secret content/format, before SSH auth can be retested.

## Required Secret Fix

Replace GitHub Actions Secret `DIGITALOCEAN_SSH_KEY` with exactly one of:

1. A full private OpenSSH key block matching a public key authorized on the droplet:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

2. Or a base64-encoded version of the complete private key block.

Do not include:

- `DIGITALOCEAN_SSH_KEY=`
- quotes
- markdown fences
- `COPY_START`
- `COPY_END`
- comments or wrapper text
- the public key instead of the private key

## Host-Side Authorization Fix After Secret Parses

Once `Prepare SSH key` passes again, the next likely blocker is SSH auth on the existing droplet.

If the workflow derives this public key again:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy
```

make sure it is present for the configured user at:

```text
/root/.ssh/authorized_keys
```

A read-only Gmail search found a recent DigitalOcean reset email for this exact droplet. Use the original email or DigitalOcean console directly as an owner-controlled recovery path if no already-working SSH session is available. Do not copy the password/reset value into GitHub, docs, or chat.

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

- `DIGITALOCEAN_SSH_KEY`: workflow step `Prepare SSH key` passes and prints a public fingerprint/key.
- SSH auth: workflow step `Deploy to DigitalOcean droplet over SSH` reaches remote commands and prints `[remote] synced_commit=...`.
- `.env.production`: `deploy.sh` does not fail with missing value or placeholder messages.
- Postgres/Redis: `/ready` returns success locally and publicly.
- `BASE_URL`: post-deploy endpoint checks pass against all three public routes.
