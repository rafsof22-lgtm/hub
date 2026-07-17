# Deployment Secret Placement Map

Last updated: 2026-07-17

## Safety Rule

Secrets must not be committed to this repository and must not be copied into issues, comments, docs, or chat.

Public SSH keys and fingerprints are safe to record for verification. Private key blocks, passwords, reset tokens, OAuth client secrets, refresh tokens, API keys, bearer tokens, and one-time credentials are never safe to record.

## GitHub Actions Secrets And Variables

| item | belongs in | secret? | notes |
|---|---|---:|---|
| `DIGITALOCEAN_SSH_KEY` | GitHub Actions Secret | yes | full private OpenSSH key block or base64-encoded private key block; latest rerun job `87571675414` parses this value successfully and derives the expected public key |
| `DIGITALOCEAN_HOST` | GitHub Actions Variable preferred | no | expected `134.199.144.115` |
| `DIGITALOCEAN_USER` | GitHub Actions Variable preferred | no | expected `root` unless changed |
| `DIGITALOCEAN_PORT` | GitHub Actions Variable preferred | no | expected `22` unless changed |
| `APP_DIR` | GitHub Actions Variable preferred | no | expected `/opt/xrp-hbar-apex` |
| `BASE_URL` | GitHub Actions Variable or Secret | usually no | expected `http://134.199.144.115` for current proof testing unless a real domain is intentionally used |
| `DIGITALOCEAN_ACCESS_TOKEN` | GitHub Actions Secret | yes | only needed for diagnostics workflow |
| `DIGITALOCEAN_DROPLET_ID` | GitHub Actions Variable preferred | no | expected `584697763` if diagnostics workflow is used |

## Current SSH Key Proof

Latest exercised Actions proof available to this agent:

- Run `29469547563`, latest job attempt `87571675414`, passed `Prepare SSH key`.
- Derived fingerprint: `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I (ED25519)`.
- Derived public key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.
- The deploy step failed with `Permission denied (publickey)` before remote commands ran.

DigitalOcean account key inventory contains the same public key as key id `57820900`, name `github-actions-deploy-2026-07-16-active`, fingerprint `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`.

Historical blocker note: that SSH authorization failure is superseded by later successful deploy proof. Recheck the latest Actions run before treating SSH as the current blocker.

## Host-Side Authorization Fix

Make sure this public key is present for the configured user if SSH authorization regresses:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy
```

Expected host-side location:

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
| `OPENAI_API_KEY` | yes | model-backed routes; optional for current basic health |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | yes | future Google workflows |
| `N8N_WEBHOOK_SECRET` | yes | future n8n webhooks |
| `GMAIL_OAUTH_CLIENT_ID` | low/yes | Gmail runtime token refresh; keep host-only with the paired secret/refresh token |
| `GMAIL_OAUTH_CLIENT_SECRET` | yes | Gmail runtime token refresh |
| `GMAIL_OAUTH_REFRESH_TOKEN` | yes | Gmail runtime token refresh |

## Future Hybrid LLM Router Values

These are future-only until a router module and provider health checks exist. Do not add real values to repo docs, issues, comments, logs, or chat.

| item | belongs in | secret? | required now? | verification without exposing value |
|---|---|---:|---:|---|
| `OPENROUTER_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs provider checks | yes | no | narrow provider health/auth check returns success without printing key |
| `DEEPSEEK_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs provider checks | yes | no | narrow provider health/auth check returns success without printing key |
| `KIMI_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs provider checks | yes | no | narrow provider health/auth check returns success without printing key |
| `QWEN_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs provider checks | yes | no | narrow provider health/auth check returns success without printing key |
| `LITELLM_MASTER_KEY` | host runtime secret store | yes | no | LiteLLM health/auth check passes without logging key |
| `LLM_ROUTER_MODE` | host runtime variable | no | no | router status reports dry-run/live mode |
| `LLM_ROUTER_DEFAULT_MODEL` | host runtime variable | no | no | dry-run route selection reports expected default |
| `LLM_ROUTER_CODING_MODEL` | host runtime variable | no | no | dry-run coding task selects expected worker |
| `LLM_ROUTER_RESEARCH_MODEL` | host runtime variable | no | no | dry-run research task selects expected worker |
| `LLM_ROUTER_CLASSIFICATION_MODEL` | host runtime variable | no | no | dry-run classification task selects expected worker |
| `LOCAL_LLM_BASE_URL` | host runtime variable | no/low | no | local worker health endpoint responds |
| `OCR_VISION_ENDPOINT` | host runtime variable or secret depending on provider | depends | no | OCR/vision health check responds without secret leakage |
| `EMBEDDING_MODEL` | host runtime variable | no | no | embedding route dry-run selects expected model |

## Verification Without Exposing Secrets

- `DIGITALOCEAN_SSH_KEY`: workflow step `Prepare SSH key` passes and prints a public fingerprint/key.
- SSH auth: workflow step `Deploy to DigitalOcean droplet over SSH` reaches remote commands and prints `[remote] synced_commit=...`.
- `.env.production`: `deploy.sh` does not fail with missing value or placeholder messages.
- Postgres/Redis: `/ready` returns success locally and publicly.
- `BASE_URL`: post-deploy endpoint checks pass against required public routes.
- Gmail runtime credentials: `/email/newsletter/gmail/status` reports token-refresh-proven readiness; then a bounded read-only Gmail fetch succeeds.
- Hybrid router credentials: future router health endpoints prove configured providers without logging secret values.
