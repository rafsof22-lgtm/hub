# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `END_TO_END_NOT_VERIFIED`, `SECRET_OWNER_ACTION_REQUIRED`.

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
- Commit `91f13ff52ac2f1ef4d99d7117a6fb16a1da61013` triggered `DigitalOcean Auto Deploy` run `29463550411`.
- Run `29463550411` failed in job `87511834686`, step `Prepare SSH key`.
- First failing log line: `DIGITALOCEAN_SSH_KEY must contain a full private key block, or a base64-encoded private key block`.

## Current Blocker

`PLACEHOLDER_SECRET` / `INVALID_SECRET_FORMAT` on `DIGITALOCEAN_SSH_KEY`.

The workflow is enabled and triggering, but the `DIGITALOCEAN_SSH_KEY` secret value is not a valid private SSH key block and is not a valid base64-encoded private key block. The deploy never reaches the droplet, so Docker, `.env.production`, Caddy, local health, public health, VTI smoke proof, and email/newsletter proof remain downstream and unverified.

A separate visible public route issue remains: the public IP currently returns `HTTP 403 Domain forbidden` from `envoy`, not from the intended Caddy/Flask stack. This may clear after a real deploy, but it cannot be proven until the SSH key secret is fixed and the deploy reaches the host.

## Required Secret And Variable Placement

Do not paste secret values into chat or commit them.

| item | location | status |
|---|---|---|
| `DIGITALOCEAN_HOST=134.199.144.115` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `DIGITALOCEAN_USER=root` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `DIGITALOCEAN_PORT=22` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `APP_DIR=/opt/xrp-hbar-apex` | GitHub Actions variable or secret | needs GitHub UI/API verification |
| `BASE_URL=<real live URL>` | GitHub Actions variable or secret | needs real domain value |
| `DIGITALOCEAN_SSH_KEY=<private key>` | GitHub Actions secret only | invalid current value; secret owner action required |
| `.env.production` | droplet only, never committed | secret owner action required |

## Exact Fix For The Current Blocker

Replace the GitHub Actions secret named `DIGITALOCEAN_SSH_KEY` with the full private key matching a public key authorized on the droplet.

Accepted formats:

- full OpenSSH private key block beginning with `-----BEGIN OPENSSH PRIVATE KEY-----` and ending with `-----END OPENSSH PRIVATE KEY-----`
- full PEM private key block beginning with `-----BEGIN ... PRIVATE KEY-----` and ending with `-----END ... PRIVATE KEY-----`
- base64-encoded version of one of those full private key blocks

Do not use:

- the public key
- the DigitalOcean SSH key name
- the DigitalOcean SSH key ID
- the fingerprint
- a placeholder
- a partial/private-key body without BEGIN and END lines

## Next Exact Actions

1. In GitHub, replace `Settings -> Secrets and variables -> Actions -> Secrets -> DIGITALOCEAN_SSH_KEY` with the valid private key value.
2. Confirm these variables/secrets exist: `DIGITALOCEAN_HOST`, `DIGITALOCEAN_USER`, `DIGITALOCEAN_PORT`, `APP_DIR`, and `BASE_URL`.
3. Re-run workflow run `29463550411`, or push a fresh `main` commit after the secret is fixed.
4. If `Prepare SSH key` passes, inspect the next failing step, likely SSH connectivity, missing `.env.production`, Docker/bootstrap, or public route.
5. From an SSH-capable environment, connect to `root@134.199.144.115` and verify Docker, repo checkout, `.env.production`, containers, and local health endpoints.
6. Fix the public route/domain so `/health`, `/ready`, and `/deployment/status` return success from the intended app.
7. Only after generic deploy proof passes, run VTI and email/newsletter smoke proof.

## Verification Standard

Auto-deploy is not proven until a fresh `main` commit produces a successful workflow run, the host pulls that commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
