# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `END_TO_END_NOT_VERIFIED`, `BLOCKED_BY_MISSING_ACCESS`.

## Scope

Target repo: `rafsof22-lgtm/hub`

Target droplet: `Digital-ocean-XRP-Hbar-Apex`

Target public IP: `134.199.144.115`

Expected app dir: `/opt/xrp-hbar-apex`

Expected deploy path: `deployment/runtime-scaffold-pack`

## Proven From Current Run

- GitHub repo exists and default branch is `main`.
- Connected GitHub app reports admin/maintain/push access to the repo.
- `.github/workflows/digitalocean-auto-deploy.yml` exists on `main`.
- Workflow validates expected deploy files before SSH deploy.
- Workflow expects `DIGITALOCEAN_SSH_KEY` as an Actions secret.
- Workflow expects `DIGITALOCEAN_HOST`, `DIGITALOCEAN_USER`, `DIGITALOCEAN_PORT`, `APP_DIR`, and `BASE_URL` as Actions variables or secrets.
- DigitalOcean API confirms droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- DigitalOcean API confirms SSH keys exist on the account, including `xrp-hbar-github-actions-2026-07-15-fresh`.
- Public probes against `http://134.199.144.115/health`, `/ready`, and `/deployment/status` currently return `HTTP 403 Domain forbidden` from `envoy`.
- Direct SSH from the current Codex container to `root@134.199.144.115:22` failed with `Network is unreachable`.
- Direct `git clone` from the current Codex container failed due network policy: `CONNECT tunnel failed, response 403`.

## Current Blocker

`ROUTE_HEALTH_FAILURE` plus `BLOCKED_BY_MISSING_ACCESS`.

The public IP does not yet prove the Docker/Caddy/Flask stack is serving the health endpoints. The response header shows `server: envoy`, so the visible public route is not currently proving the intended Caddy reverse proxy and Flask app.

The current runtime cannot SSH into the droplet, cannot inspect `/opt/xrp-hbar-apex`, cannot create `.env.production` on the host, and cannot verify Docker containers from inside the host.

## Required Secret And Variable Placement

Do not paste secret values into chat or commit them.

| item | location | status |
|---|---|---|
| `DIGITALOCEAN_HOST=134.199.144.115` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `DIGITALOCEAN_USER=root` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `DIGITALOCEAN_PORT=22` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `APP_DIR=/opt/xrp-hbar-apex` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `BASE_URL=<real live URL>` | GitHub Actions variable or secret | needs real domain value |
| `DIGITALOCEAN_SSH_KEY=<private key>` | GitHub Actions secret only | secret owner action required |
| `.env.production` | droplet only, never committed | secret owner action required |

## Next Exact Actions

1. Confirm GitHub Actions is enabled for `rafsof22-lgtm/hub` and the `DigitalOcean Auto Deploy` workflow appears after this commit.
2. Confirm all required GitHub Actions variables/secrets are present, especially `DIGITALOCEAN_SSH_KEY` as a secret.
3. From an SSH-capable environment, connect to `root@134.199.144.115` and verify Docker, repo checkout, `.env.production`, containers, and local health endpoints.
4. Fix the public route/domain so `/health`, `/ready`, and `/deployment/status` return success from the intended app.
5. Only after generic deploy proof passes, run VTI and email/newsletter smoke proof.

## Verification Standard

Auto-deploy is not proven until a fresh `main` commit produces a successful workflow run, the host pulls that commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
