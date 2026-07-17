# XRP/HBAR Apex Runtime Hub

Deployment scaffold for the XRP/HBAR Apex Intelligence OS runtime.

## Current scope

- GitHub Actions workflow for DigitalOcean SSH deploy
- Docker Compose production stack with Flask API, worker placeholder, Postgres, Redis, and Caddy
- Health endpoints: `/health`, `/ready`, `/deployment/status`
- VTI/email scaffold proof routes and runtime proof-gate docs
- Hybrid LLM router architecture backlog: `deployment/hybrid-llm-router-architecture.md`

## Production status

The existing GitHub Actions + DigitalOcean path targets `main` and the main droplet at `134.199.144.115`. Prior proof indicates the DigitalOcean Auto Deploy workflow reached the main host and passed scaffold route checks, but full production remains unclaimed while Gmail runtime credentials and remaining framework proof gates are unresolved.

Do not claim the full Jarvis/XRP-HBAR runtime is production complete until:

- GitHub Actions deploys the intended commit from `main` to `134.199.144.115`.
- The DigitalOcean droplet has a real `deployment/runtime-scaffold-pack/.env.production` file.
- Droplet containers are healthy.
- Public endpoint checks pass for `/health`, `/ready`, `/deployment/status`, `/vti/status`, `/email/newsletter/status`, and `/evidence-pack/status`.
- Gmail runtime status proves token-refresh readiness using host-only credentials:
  - `GMAIL_OAUTH_CLIENT_ID`
  - `GMAIL_OAUTH_CLIENT_SECRET`
  - `GMAIL_OAUTH_REFRESH_TOKEN`
- A bounded Gmail fetch succeeds without exposing credential values.
- The first remaining VTI/email proof gates in `deployment/runtime-autopush-backlog.md` are updated with run-level evidence.

## Gmail OAuth invalid-grant recovery

If `/email/newsletter/gmail/status` reports `error_type: invalid_grant` after all three Gmail env names are configured, the remaining blocker is credential validity, not missing env names.

Manual action required: replace `GMAIL_OAUTH_REFRESH_TOKEN` first in GitHub Actions secrets. If the refresh token was generated against a different OAuth client, replace all three secrets together: `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, and `GMAIL_OAUTH_REFRESH_TOKEN`.

Required OAuth scope: `https://www.googleapis.com/auth/gmail.readonly`.

Never paste OAuth client secrets or refresh tokens into chat, issues, commits, logs, or docs. Store them only in the approved GitHub Actions secret path or runtime secret store.

## Hybrid router status

The hybrid LLM router is architecture/backlog only. It does not replace ChatGPT Agent Builder's core model, does not configure provider secrets, and is not required for the current VTI/email deployment path.

Future router secret/env names are tracked by name only in:

- `deployment/hybrid-llm-router-architecture.md`
- `deployment/secret-placement-map.md`
- `deployment/runtime-scaffold-pack/.env.production.example`

Secret/key setup runbook: `deployment/digitalocean-key-and-secret-runbook.md`

Tracked blocker: https://github.com/rafsof22-lgtm/hub/issues/1
