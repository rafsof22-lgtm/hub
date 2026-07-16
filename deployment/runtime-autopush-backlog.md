# Runtime Autopush Backlog

Last updated: 2026-07-16

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `WORKFLOW_TRIGGER_PROVEN`, `SSH_KEY_FORMAT_PROVEN`, `HOST_KEY_PLACEMENT_PROVEN_BY_OWNER`, `SSH_AUTH_PROVEN`, `REMOTE_REPO_SYNC_PROVEN`, `HOST_BOOTSTRAP_PROVEN`, `PUBLIC_ENDPOINTS_PROVEN`, `CORE_RUNTIME_DEPLOYMENT_PROVEN`, `FRAMEWORK_LIVE_LAYERS_PENDING`.

## Current Deployment Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`
- Droplet IP: `134.199.144.115`
- SSH user: `root`
- SSH port: `22`
- App dir: `/opt/xrp-hbar-apex`
- Runtime scaffold: `deployment/runtime-scaffold-pack`
- Proof BASE_URL: `http://134.199.144.115`

## Current Proof Gates

| gate | status | evidence |
|---|---|---|
| workflow file truth | proven | workflow pins deploy target values in commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04` |
| workflow trigger truth | proven | fresh push run `29485379774` / `DigitalOcean Auto Deploy #89` executed commit `d3aaf301334450cf1a216961c76c620c5aba6d7a` |
| scaffold file truth | proven | required deploy-file validation passed |
| SSH key format truth | proven | `Prepare SSH key` passed and derived the expected public key |
| DigitalOcean account-key truth | proven | account key id `57820900` matches workflow-derived public key |
| host-side key placement truth | proven by owner console output | deploy public key appears in `/root/.ssh/authorized_keys`; permissions and `sshd -T` output are compatible |
| SSH target mismatch risk | repo-side fixed | workflow hardcodes `root@134.199.144.115:22` for proof deployment |
| SSH auth truth | proven | run `29485379774`, job `87578507636`, connected as `root` |
| remote repo sync truth | proven | `[remote] synced_commit=d3aaf301334450cf1a216961c76c620c5aba6d7a` |
| host bootstrap truth | proven | Docker Compose pulled/built/started runtime services |
| `.env.production` truth | operationally proven for current scaffold | deploy script and services completed; secret values remain host-only |
| local service health truth | inferred through deploy completion | deploy script completed its local health wait before public checks |
| public endpoint truth | proven | `/health`, `/ready`, `/deployment/status` returned `200` from `http://134.199.144.115` |
| VTI runtime truth | not yet proven | needs separate copied-link/transcript smoke test |
| email/newsletter live-ingestion truth | not yet proven | needs Gmail/newsletter scan proof and durable registry/digest output |

## Repo-Side Backlog

1. Keep `deployment/runtime-proof-status-2026-07-16.md` as the active proof ledger for the successful core deploy.
2. Keep issue #1 open until framework-specific VTI/email live proof is either completed or explicitly split into separate tracker issues.
3. Continue using first-failing-gate reporting for any future deploy run.
4. Avoid storing host secrets in repo; `.env.production` stays host-only.

## Remaining Runtime / Framework Backlog

1. Inspect any deploy run triggered by documentation or Compose cleanup commits.
2. Run one VTI smoke test before calling VTI externally proven.
3. Run one Gmail/newsletter pass before calling email/newsletter live ingestion proven.
4. If a real domain replaces the IP proof URL later, rerun public endpoint checks against that domain.

## Latest Proven Core Deploy

- Run: `29485379774`
- Job: `87578507636`
- Commit deployed: `d3aaf301334450cf1a216961c76c620c5aba6d7a`
- Result: success
- Public proof:
  - `http://134.199.144.115/health` -> `200`
  - `http://134.199.144.115/ready` -> `200`
  - `http://134.199.144.115/deployment/status` -> `200`
