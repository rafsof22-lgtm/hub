# Runtime Autopush Backlog

Last updated: 2026-07-16

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `WORKFLOW_TRIGGER_PROVEN_HISTORICALLY`, `SSH_KEY_FORMAT_PROVEN`, `HOST_KEY_PLACEMENT_PROVEN_BY_OWNER`, `FRESH_CURRENT_MAIN_DEPLOY_NEEDED`, `END_TO_END_NOT_VERIFIED`.

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
| workflow trigger truth | proven historically / fresh proof pending | push-triggered workflow runs have appeared historically; connector cannot list fresh push-triggered runs for latest commits |
| scaffold file truth | proven historically | workflow validates deploy script, compose file, Caddyfile, Dockerfile, requirements, and app |
| SSH key format truth | proven historically | old-run reruns passed `Prepare SSH key` and derived the expected public key |
| DigitalOcean account-key truth | proven | account key id `57820900` matches workflow-derived public key |
| host-side key placement truth | proven by owner console output | deploy public key appears in `/root/.ssh/authorized_keys`; permissions and `sshd -T` output look correct |
| SSH target mismatch risk | repo-side fixed | workflow now hardcodes `root@134.199.144.115:22` instead of reading possibly stale GitHub variables/secrets |
| fresh current-main SSH auth truth | not yet visible to connector | requires a fresh `DigitalOcean Auto Deploy` run from current `main`, not old run `29469547563` |
| remote repo sync truth | not reached | requires workflow reaching remote shell and printing `[remote] synced_commit=...` |
| host bootstrap truth | not reached | requires remote Docker/compose execution evidence |
| `.env.production` truth | not reached | must be verified on droplet, never committed |
| local service health truth | not reached | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not reached | public checks must pass against `BASE_URL` after SSH deploy completes |
| VTI runtime truth | not yet proven | only after generic deploy proof |
| email/newsletter live-ingestion truth | not yet proven | only after generic deploy proof or separate Gmail workflow proof |

## Repo-Side Backlog

1. Inspect the fresh current-`main` workflow run when visible.
2. Keep `deployment/runtime-proof-status-2026-07-16.md` as the active proof ledger for this run.
3. Keep issue #1 aligned with the current first failing proof gate.
4. After SSH auth is proven on the pinned workflow, advance the proof gate to remote repo sync, host bootstrap, `.env.production`, local health, or public endpoint routing as evidence allows.
5. Do not mark host, env, health, VTI, or email proof complete without run evidence.

## External Or Runtime Backlog

1. Start or inspect a fresh `DigitalOcean Auto Deploy` run from current `main` so it uses the pinned workflow values.
2. If SSH still fails on the current workflow, inspect `/var/log/auth.log` or `journalctl -u ssh` on the droplet while a deploy attempt runs to identify whether the offered key is rejected, the user is wrong, or SSHD is applying a different auth rule.
3. Verify `.env.production` exists on the droplet and contains no placeholders after SSH auth is fixed.
4. Verify Docker/compose can build and start the runtime stack.
5. Verify public HTTP routes target the intended app.

## Fresh Trigger Note

This backlog update is intentionally committed after the workflow target pin so GitHub receives a fresh `main` push event using the current workflow file.
