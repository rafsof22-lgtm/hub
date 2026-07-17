# Runtime Proof Status

Updated: 2026-07-17T10:43:00Z

## Scope

Repo: `rafsof22-lgtm/hub`
Branch: `main`
Target: `http://134.199.144.115`
Workflow: `DigitalOcean Auto Deploy`

## Current Repo State

Latest checked main commits in this pass:

- `a1501b03b41c5014d364a2f1a01d74baec43b3de` - prior trigger commit found at start of pass.
- `4e29771da9fc5a5a08280e29633a472c9d40a622` - added this runtime proof status ledger.
- `da4101cf11b43c47f75cb862ede05385161b2d94` - minimal non-doc deploy trigger for non-Gmail proof gates.

This final ledger update is markdown-only and should not trigger `DigitalOcean Auto Deploy` because the workflow ignores `**/*.md` push changes.

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

- Latest visible non-doc deploy trigger commit: `da4101cf11b43c47f75cb862ede05385161b2d94`.
- Combined commit status for the trigger commit returned no statuses.
- Commit-associated workflow-run query for the trigger commit returned no workflow runs.
- No latest Actions run ID was visible through the available commit/status/run connector paths in this pass.

DigitalOcean connector evidence:

- Droplet `Digital-ocean-XRP-Hbar-Apex` is active.
- Public IPv4 target is `134.199.144.115`.
- Size is `s-2vcpu-2gb`, Sydney `syd1`, about USD 18/month.
- Older repair droplet `Digital-ocean-XRP-Hbar-Apex-repair` is also active at `170.64.230.87`.
- No destructive DigitalOcean action was performed.

Public route probe from the current container, before and after the trigger commit, returned HTTP `403` with `server: envoy` and body category `Domain forbidden` for all checked routes:

- `/health`
- `/ready`
- `/deployment/status`
- `/email/newsletter/status`
- `/email/newsletter/sync/status`
- `/email/newsletter/claims/status`
- `/vti/status`
- `/vti/worker/status`
- `/evidence-pack/status`
- `/ops/dedupe-retry-backfill/status`
- `/email/newsletter/gmail/status`

The same Envoy block also appeared for alternate direct port probes from this environment. Current classification is therefore `PUBLIC_ROUTE_PROOF_UNKNOWN_FROM_CURRENT_EGRESS_OR_HOST_PROXY`, not a proven Flask route failure.

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

- `PUBLIC_ROUTE_PROOF_UNKNOWN_FROM_CURRENT_EGRESS_OR_HOST_PROXY`: current workspace public probing is blocked by an Envoy `Domain forbidden` response before the Flask/Caddy proof routes can be observed, and latest Actions run evidence was not visible through the available connector run/status paths.

Known manual Gmail blocker:

- `GMAIL_OAUTH_REFRESH_TOKEN`
- If generated against a different OAuth client, also replace `GMAIL_OAUTH_CLIENT_ID` and `GMAIL_OAUTH_CLIENT_SECRET` together.

## Next Fastest Action

Inspect the latest `DigitalOcean Auto Deploy` run in GitHub Actions UI or any available Actions connector that can list all branch runs, not only commit-associated runs. If Actions remains invisible, use direct host console or SSH with the existing deploy key path to run `deployment/runtime-scaffold-pack/host-self-heal.sh`, then verify local non-Gmail routes from the host and public non-Gmail routes from a network path that is not returning the Envoy domain block.
