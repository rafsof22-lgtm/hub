# Runtime Proof Status

Updated: 2026-07-17T10:41:00Z

## Scope

Repo: `rafsof22-lgtm/hub`
Branch: `main`
Target: `http://134.199.144.115`
Workflow: `DigitalOcean Auto Deploy`

## Current Repo State

Latest checked main commit before this note: `a1501b03b41c5014d364a2f1a01d74baec43b3de`.

Inspected repo-side deployment files:

- `.github/workflows/digitalocean-auto-deploy.yml`
- `deployment/runtime-scaffold-pack/host-self-heal.sh`
- `deployment/runtime-scaffold-pack/deploy.sh`
- `deployment/runtime-scaffold-pack/docker-compose.prod.yml`
- `deployment/runtime-scaffold-pack/Caddyfile`
- `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/app.py`
- `deployment/runtime-scaffold-pack/README.md`

No secret values were read, printed, stored, inferred, or copied.

## Current Evidence

GitHub connector evidence:

- Latest visible main commit: `a1501b03b41c5014d364a2f1a01d74baec43b3de`.
- Combined commit status returned no statuses.
- Commit-associated workflow-run query returned no workflow runs.

DigitalOcean connector evidence:

- Droplet `Digital-ocean-XRP-Hbar-Apex` is active.
- Public IPv4 target is `134.199.144.115`.
- Size is `s-2vcpu-2gb`, Sydney `syd1`, about USD 18/month.
- Older repair droplet `Digital-ocean-XRP-Hbar-Apex-repair` is also active at `170.64.230.87`.

Public route probe from the current container returned HTTP `403` with `server: envoy` and body category `Domain forbidden` for all checked routes, including `/health`, `/ready`, `/deployment/status`, newsletter scaffold routes, VTI scaffold routes, evidence-pack, ops checkpoint, and Gmail status.

Because every direct IP/port probe from this environment returned the same Envoy domain block, the current route evidence is classified as `PUBLIC_ROUTE_PROOF_UNKNOWN_FROM_CURRENT_EGRESS`, not app-route proof failure. The next authoritative live proof should come from a GitHub Actions runner or direct host shell proof after deploy.

## Proof Policy

Gmail OAuth remains a separate manual blocker only. Do not treat `invalid_grant` as blocking these non-Gmail gates:

- `CORE_DEPLOY_PROOF`
- `PUBLIC_ROUTE_PROOF`
- `VTI_PROOF`
- `NEWSLETTER_MANUAL_PROOF`
- `SYNC_CLAIM_EVIDENCE_OPS_PROOFS`

Only claim `GMAIL_OAUTH_PROOF=PASS` when `/email/newsletter/gmail/status` proves token refresh success.

## Current Blocker Classification

Remaining non-Gmail blocker:

- `PUBLIC_ROUTE_PROOF_UNKNOWN_FROM_CURRENT_EGRESS`: current workspace public probing is blocked by an Envoy `Domain forbidden` response before the Flask/Caddy proof routes can be observed.

Known manual Gmail blocker:

- `GMAIL_OAUTH_REFRESH_TOKEN`
- If generated against a different OAuth client, also replace `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` together.

## Next Fastest Action

Trigger `DigitalOcean Auto Deploy` with a minimal non-doc `.deploy-trigger` update. Then inspect the latest run/job/log evidence if visible. If Actions remains invisible, use direct host console or SSH with the already configured deploy key path to run `deployment/runtime-scaffold-pack/host-self-heal.sh` and verify local/public non-Gmail routes from the host side.
