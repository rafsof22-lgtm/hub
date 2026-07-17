# Runtime Scaffold Pack

This folder contains the production deployment scaffold for the XRP/HBAR Apex Intelligence OS runtime path.

## Current Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Runtime scaffold root: `deployment/runtime-scaffold-pack/`
- Service root: `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/`
- DigitalOcean production target: `http://134.199.144.115`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`

## Current Honest Status

As of the 2026-07-17 remediation pass, repo-side deployment scaffolding and GitHub Actions deployment logic are present on `main`.

Current proven evidence from DigitalOcean Auto Deploy #130 supplied to this pass:

- Core production proof previously passed for `/health`, `/ready`, `/deployment/status`, email/newsletter scaffold routes, VTI routes, evidence-pack route, ops checkpoint route, and scaffold POST proof routes.
- Gmail proof failed only at `/email/newsletter/gmail/status` with HTTP 503.
- Gmail env names were configured and hidden.
- Gmail token refresh attempted and failed with `invalid_grant`, HTTP 400, with required scope present.

Current live public recheck during this pass returned `403 Domain forbidden` for:

- `/health`
- `/ready`
- `/deployment/status`
- `/email/newsletter/status`
- `/email/newsletter/gmail/status`
- `/email/newsletter/gmail/proof/latest`

Interpretation:

- Core route proof and Gmail OAuth proof are separate gates.
- A current public-route regression or stale proxy layer must be cleared before live public proof can be called passing again.
- Gmail OAuth remains blocked until the refresh token is replaced and token refresh succeeds.

## Required Secrets And Values

Use GitHub Actions secrets for deploy-time connection values. Do not commit secrets and never paste secret values into chat.

Required deploy secret:

- `DIGITALOCEAN_SSH_KEY`: full private SSH key block for the droplet deploy user

Required Gmail OAuth secrets:

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`

If the replacement refresh token is generated against the same OAuth client, replace only:

- `GMAIL_OAUTH_REFRESH_TOKEN`

If the replacement refresh token is generated against a different OAuth client, replace all three together:

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`

Required Gmail scope:

- `https://www.googleapis.com/auth/gmail.readonly`

Host-side `.env.production` must contain real runtime values, including:

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`

## Proof Gates

The workflow separates proof into three labels:

- `CORE_DEPLOY_PROOF`: fatal if core health/readiness/deployment/scaffold routes fail.
- `PUBLIC_ROUTE_PROOF`: fatal if public non-Gmail proof routes fail.
- `GMAIL_OAUTH_PROOF`: explicit pass or blocked state. Gmail OAuth `invalid_grant` is reported as `GMAIL_OAUTH_INVALID_GRANT_REFRESH_TOKEN_REPLACE_REQUIRED` without exposing secret values.

Do not call Gmail automation proven until all are true:

- `/email/newsletter/gmail/status` returns token-refresh-proven status.
- `GMAIL_OAUTH_PROOF=PASS` appears in workflow logs.
- `/email/newsletter/gmail/fetch` succeeds.
- `/email/newsletter/gmail/proof/latest` returns a persisted proof.

## Safe Recovery Order

1. Let a fresh non-doc `main` commit trigger DigitalOcean Auto Deploy.
2. Confirm the workflow deploy step can SSH, sync `main`, and run `host-self-heal.sh`.
3. Verify `PUBLIC_ROUTE_PROOF=PASS` for non-Gmail public routes.
4. If Gmail remains `invalid_grant`, replace the GitHub secret values listed above without exposing them.
5. Rerun the workflow and verify `GMAIL_OAUTH_PROOF=PASS` plus the Gmail fetch proof route.

## Guardrails

- Do not remove Gmail proof or pretend Gmail passed while token refresh fails.
- Do not treat configured secret names as proof that OAuth credentials are valid.
- Do not expose or log secret values.
- Do not create, destroy, rebuild, resize, power-cycle, or reset droplets from this scaffold without explicit approval.
