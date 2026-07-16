# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_PROVEN`, `REMOTE_REPO_SYNC_PROVEN`, `HOST_BOOTSTRAP_PROVEN`, `PUBLIC_ENDPOINTS_PROVEN`, `CORE_RUNTIME_DEPLOYMENT_PROVEN`, `FRAMEWORK_LIVE_LAYERS_NOT_YET_PROVEN`.

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
- Connected GitHub app reports repo access and can update repo files/issues.
- Deployment scaffold files exist in the repo.
- The Flask app exposes `/health`, `/ready`, and `/deployment/status`.
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- DigitalOcean account key list contains public key id `57820900`, name `github-actions-deploy-2026-07-16-active`, fingerprint `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`.
- User-provided droplet console output proved the deploy public key was present in `/root/.ssh/authorized_keys`, with `PermitRootLogin yes`, `PubkeyAuthentication yes`, and `AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys2`.
- Workflow target values were pinned in commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04`:
  - `DIGITALOCEAN_HOST=134.199.144.115`
  - `DIGITALOCEAN_USER=root`
  - `DIGITALOCEAN_PORT=22`
  - `APP_DIR=/opt/xrp-hbar-apex`
  - `BASE_URL=http://134.199.144.115`
- Fresh workflow run `29485379774` / `DigitalOcean Auto Deploy #89` for commit `d3aaf301334450cf1a216961c76c620c5aba6d7a` completed successfully.
- Job `87578507636` passed all deploy steps:
  - `Validate required deploy files exist`
  - `Prepare SSH key`
  - `Deploy to DigitalOcean droplet over SSH`
  - `Post-deploy live endpoint checks`
- Run logs proved SSH connected to the expected host as `root`:
  - `deploy_target=root@134.199.144.115:22 app_dir=/opt/xrp-hbar-apex`
  - `[remote] connected_user=root`
  - `[remote] host=Digital-ocean-XRP-Hbar-Apex`
- Remote repo sync was proven by run log line `synced_commit=d3aaf301334450cf1a216961c76c620c5aba6d7a`.
- Host bootstrap was proven: Docker Compose pulled/built images, started Postgres, Redis, API, worker, and Caddy containers.
- Container state was proven healthy enough for deploy completion: Postgres and Redis became healthy; API, worker, and Caddy started.
- Public endpoint proof passed from GitHub Actions against `http://134.199.144.115`:
  - `/health` returned `200` with `{"env":"production","service":"xrp-hbar-apex","status":"ok","version":"0.1.0"}`.
  - `/ready` returned `200` with `{"postgres":"ok","redis":"ok","status":"ready"}`.
  - `/deployment/status` returned `200` with `{"env":"production","service":"xrp-hbar-apex","stack":["app","postgres","redis","caddy"],"status":"running","version":"0.1.0"}`.

## Superseded Historical Blocker

Old reruns of run `29469547563` checked out old commit `b46e969be6110e3326cf0b4236dd83cc3c93f445` and failed at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`. That evidence is now superseded by fresh successful run `29485379774` on current `main` commit `d3aaf301334450cf1a216961c76c620c5aba6d7a`.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | workflow exists and pins target values |
| workflow trigger truth | proven | fresh push run `29485379774` executed current `main` |
| scaffold file truth | proven | validation step passed |
| SSH key format truth | proven | `Prepare SSH key` passed and derived the expected public key |
| DigitalOcean account-key truth | proven | account key id `57820900` matches workflow-derived public key |
| host-side key placement truth | proven by owner console output | key present in `/root/.ssh/authorized_keys`; SSHD configured to read it |
| SSH auth truth | proven | job `87578507636` connected to `root@134.199.144.115:22` |
| remote repo sync truth | proven | `synced_commit=d3aaf301334450cf1a216961c76c620c5aba6d7a` |
| host bootstrap truth | proven | Docker Compose pull/build/start completed |
| `.env.production` truth | operationally proven for current scaffold | deploy script and services passed; secret values remain host-only and are not recorded here |
| local service health truth | inferred through deploy completion | deploy script reached completion after waiting for local health endpoints |
| public endpoint truth | proven | `/health`, `/ready`, `/deployment/status` returned `200` |
| VTI runtime truth | not yet proven | no external VTI smoke test completed yet |
| email/newsletter live-ingestion truth | not yet proven | no Gmail/newsletter ingestion proof completed yet |

## Current First Remaining Proof Gate

Core GitHub-to-DigitalOcean deployment is proven. The first remaining framework-specific proof gate is VTI runtime smoke proof or email/newsletter live-ingestion proof, depending on which layer is intended to be live next.

## Exact Next Step

Run one small framework-layer smoke test after the core runtime: either a VTI copied-link/transcript path, or a Gmail/newsletter scan that writes durable output to `newsletter-source-registry.md` and `email-intelligence-digest-log.md`.

## Strict Success Standard

Do not mark VTI or email/newsletter live-ingestion complete until each has its own end-to-end proof. Core deployment, SSH, remote sync, host bootstrap, and public runtime endpoints are now proven for run `29485379774`.
