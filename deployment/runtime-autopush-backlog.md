# Runtime Autopush Backlog

Last updated: 2026-07-16

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TRIGGER_PROVEN`, `HOST_PROOF_PARTIAL`, `END_TO_END_NOT_VERIFIED`.

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
| SSH key format truth | needs fresh run proof | earlier run failed on key format; user later reported it was cleared |
| SSH auth truth | needs fresh run proof | user reported local SSH auth worked; GitHub Actions proof still needed |
| remote repo sync truth | not yet proven in latest run | requires workflow reaching SSH deploy step |
| host bootstrap truth | not yet proven in latest run | requires remote Docker/compose execution evidence |
| `.env.production` truth | not yet proven | must be verified on droplet, never committed |
| local service health truth | not yet proven | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not yet proven | public checks must pass against `BASE_URL` |
| VTI runtime truth | not yet proven | only after generic deploy proof |
| email/newsletter live-ingestion truth | not yet proven | only after generic deploy proof or separate Gmail workflow proof |

## Repo-Side Backlog

1. Keep deploy workflow diagnostic output current.
2. Keep `deployment/runtime-proof-status-2026-07-16.md` as the active proof ledger for this run.
3. Keep issue #1 aligned with the current first failing proof gate.
4. Do not mark host, env, health, VTI, or email proof complete without run evidence.

## External Or Runtime Backlog

1. Verify the actual GitHub Actions values for `DIGITALOCEAN_HOST`, `DIGITALOCEAN_USER`, `DIGITALOCEAN_PORT`, `APP_DIR`, `BASE_URL`, and `DIGITALOCEAN_SSH_KEY` through workflow outcome.
2. Verify `.env.production` exists on the droplet and contains no placeholders.
3. Verify Docker/compose can build and start the runtime stack.
4. Verify public DNS/domain/proxy routing targets the intended app.
