# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `END_TO_END_NOT_VERIFIED`.

## Scope

Target repo: `rafsof22-lgtm/hub`

Target branch: `main`

Target workflow: `.github/workflows/digitalocean-auto-deploy.yml`

Target droplet: `Digital-ocean-XRP-Hbar-Apex`

Target public IP: `134.199.144.115`

Expected app dir: `/opt/xrp-hbar-apex`

Expected deploy path: `deployment/runtime-scaffold-pack`

## Current Proven State

- GitHub repo exists and default branch is `main`.
- Connected GitHub app reports admin/maintain/push access to the repo.
- `DigitalOcean Auto Deploy` exists on `main`.
- `DigitalOcean Diagnostics` exists on `main`.
- The deployment scaffold files exist in the repo.
- The Flask app exposes `/health`, `/ready`, and `/deployment/status`.
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.
- The Caddyfile contains both `:80` fallback and `{$DOMAIN}` routing.
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- Earlier push-triggered workflow runs proved workflow trigger behavior.
- Earlier run `29463550411` proved the prior first failing step was `Prepare SSH key` with invalid private-key format.

## Current User-Reported State Needing Fresh Workflow Proof

The user reports the SSH key format blocker has since been cleared and that local-machine SSH auth to the droplet has been proven manually. This ledger does not mark those gates as GitHub Actions proven until a fresh workflow run shows them passing.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | file exists and was inspected |
| workflow trigger truth | proven | push-triggered runs appeared previously |
| SSH key format truth | pending fresh run | prior run failed; user reports fixed |
| SSH auth truth | pending fresh run | user reports local SSH worked; Actions proof still needed |
| remote repo sync truth | pending fresh run | requires SSH deploy step to reach remote commands |
| host bootstrap truth | pending fresh run | requires Docker/Compose execution evidence |
| `.env.production` truth | pending fresh run | host-only file, never committed |
| local service health truth | pending fresh run | deploy script checks local endpoints |
| public endpoint truth | pending fresh run | post-deploy checks now provide better diagnostics |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Repo-Side Changes Made In This Cleanup Pass

- Improved `Post-deploy live endpoint checks` in the deploy workflow with HTTP status, body preview, scheme validation, trailing-slash normalization, and direct droplet HTTP probes when `BASE_URL` checks fail.
- Added canonical repo docs:
  - `deployment/runtime-autopush-backlog.md`
  - `deployment/github-auto-push-gap-analysis.md`
  - `deployment/github-auto-deploy-setup.md`
  - `deployment/secret-placement-map.md`
- Preserved historical failure evidence while separating it from current pending proof gates.

## Current First Failing Proof Gate

Pending fresh run. The next deploy run must establish whether the first failing proof gate is now:

1. SSH key format,
2. SSH auth,
3. remote repo sync,
4. host bootstrap / Docker,
5. `.env.production`,
6. local service health, or
7. public `BASE_URL` endpoint routing.

## Strict Success Standard

Auto-deploy is not proven until a fresh `main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
