# Runtime Autopush Backlog

Last updated: 2026-07-16

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TRIGGER_PROVEN`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_BLOCKED`, `END_TO_END_NOT_VERIFIED`.

## Current Deployment Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`
- Droplet IP: `134.199.144.115`
- App dir: `/opt/xrp-hbar-apex`
- Runtime scaffold: `deployment/runtime-scaffold-pack`

## Current Proof Gates

| gate | status | evidence |
|---|---|---|
| workflow file truth | proven | workflow exists on `main` |
| workflow trigger truth | proven | push-triggered workflow runs have appeared |
| scaffold file truth | proven | workflow validates deploy script, compose file, Caddyfile, Dockerfile, requirements, and app |
| SSH key format truth | proven | `Prepare SSH key` passed in runs `29469334854`, `29469474129`, and `29469547563` |
| SSH auth truth | blocked | run `29469547563` failed with `Permission denied (publickey)` using fingerprint `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I` |
| remote repo sync truth | not reached | requires workflow reaching remote shell and printing `[remote] synced_commit=...` |
| host bootstrap truth | not reached | requires remote Docker/compose execution evidence |
| `.env.production` truth | not reached | must be verified on droplet, never committed |
| local service health truth | not reached | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not reached in latest runs | public checks must pass against `BASE_URL` after SSH deploy completes |
| VTI runtime truth | not yet proven | only after generic deploy proof |
| email/newsletter live-ingestion truth | not yet proven | only after generic deploy proof or separate Gmail workflow proof |

## Repo-Side Backlog

1. Keep deploy workflow diagnostic output current.
2. Keep `deployment/runtime-proof-status-2026-07-16.md` as the active proof ledger for this run.
3. Keep issue #1 aligned with the current first failing proof gate.
4. After SSH auth is fixed, inspect the next run and advance the proof gate to remote repo sync, host bootstrap, `.env.production`, local health, or public endpoint routing as evidence allows.
5. Do not mark host, env, health, VTI, or email proof complete without run evidence.

## External Or Runtime Backlog

1. Authorize the current Actions deploy public key on the droplet for the configured user, expected `root`, or replace `DIGITALOCEAN_SSH_KEY` with the private key that matches an already authorized droplet key.
2. Verify `.env.production` exists on the droplet and contains no placeholders after SSH auth is fixed.
3. Verify Docker/compose can build and start the runtime stack.
4. Verify public DNS/domain/proxy routing targets the intended app.
