# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_BLOCKED`, `END_TO_END_NOT_VERIFIED`.

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
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- DigitalOcean account key list contains public key id `57820900`, name `github-actions-deploy-2026-07-16-active`, fingerprint `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`.
- User-provided droplet console output proves the deploy public key is present in `/root/.ssh/authorized_keys`, permissions are `700` for `/root/.ssh` and `600` for `authorized_keys`, `PermitRootLogin yes`, `PubkeyAuthentication yes`, and `AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys2`.
- Historical reruns of run `29469547563` still checked out old commit `b46e969be6110e3326cf0b4236dd83cc3c93f445` and failed at SSH auth.
- Workflow target values were pinned in `.github/workflows/digitalocean-auto-deploy.yml` in commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04`:
  - `DIGITALOCEAN_HOST=134.199.144.115`
  - `DIGITALOCEAN_USER=root`
  - `DIGITALOCEAN_PORT=22`
  - `APP_DIR=/opt/xrp-hbar-apex`
  - `BASE_URL=http://134.199.144.115`
- The pinned workflow also prints `[remote] connected_user`, `[remote] host`, and `[remote] synced_commit` after successful SSH so the next proof gate is unambiguous.
- Connector limitation: commit-associated workflow-run lookup returned no visible run for commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04`; the available connector did not expose a general fresh `workflow_dispatch` action.

## Latest Exercised Run Before Target Pinning

- Run: `29469547563`
- Latest old-run job attempt: `87574584632`
- Checked-out commit in that rerun: `b46e969be6110e3326cf0b4236dd83cc3c93f445`
- First failing step: `Deploy to DigitalOcean droplet over SSH`
- Exact error: `Permission denied (publickey)`
- `Prepare SSH key`: passed
- `Post-deploy live endpoint checks`: skipped

This old-run rerun is no longer the right proof vehicle because it checks out an old commit and old workflow state. The next proof must run the current `main` workflow at or after commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04`.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | current workflow pins target values in commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04` |
| workflow trigger/rerun truth | partial | historical reruns work, but connector cannot prove a fresh run for the new commit |
| scaffold file truth | proven historically | validation passed in old-run reruns |
| SSH key format truth | proven historically | old-run reruns passed `Prepare SSH key` and derived expected public key |
| DigitalOcean account-key truth | proven | account key id `57820900` matches workflow-derived public key |
| host-side key placement truth | proven by user console output | key present in `/root/.ssh/authorized_keys`; SSHD configured to read it |
| SSH auth truth | needs fresh proof | must run current `main`, not old run `b46e...` |
| remote repo sync truth | not reached | requires fresh workflow reaching remote shell and printing `[remote] synced_commit=...` |
| host bootstrap truth | not reached | requires remote Docker/compose execution evidence |
| `.env.production` truth | not reached | must be verified on droplet, never committed |
| local service health truth | not reached | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not reached | public checks only run after SSH deploy completes |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Current First Failing Proof Gate

Fresh current-`main` deploy proof is not visible yet. The first gate to test is now `Deploy to DigitalOcean droplet over SSH` using workflow commit `c21c112aa83adcea3e21fcc7bd1040cbcd2aee04` or newer.

## Exact Next Step

In GitHub Actions, start a fresh `DigitalOcean Auto Deploy` run from current `main` using **Run workflow**, not re-run failed jobs from old run `29469547563`.

Expected first proof lines if SSH clears:

```text
deploy_target=root@134.199.144.115:22 app_dir=/opt/xrp-hbar-apex
[remote] connected_user=root
[remote] host=Digital-ocean-XRP-Hbar-Apex
[remote] synced_commit=<current main commit>
```

If SSH passes, continue to remote repo sync, `.env.production`, Docker/Compose, local health, and public endpoint checks.

## Strict Success Standard

Auto-deploy is not fully proven until a fresh current-`main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
