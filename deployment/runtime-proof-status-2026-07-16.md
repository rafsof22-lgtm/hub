# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `SSH_AUTH_PROVEN`, `REMOTE_DEPLOY_REACHED`, `PUBLIC_ENDPOINT_ROUTING_FIXED_PENDING_RERUN`, `END_TO_END_NOT_VERIFIED`.

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
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- Earlier push-triggered workflow runs proved workflow trigger behavior.
- Earlier run `29463550411` proved the prior first failing step was `Prepare SSH key` with invalid private-key format.
- Later runs proved `Prepare SSH key` passes and derives public key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.
- After that public key was authorized on the droplet, the deploy advanced past the earlier SSH-auth failure.
- User-provided latest log shows remote deploy completed far enough for the workflow to enter `Post-deploy live endpoint checks`.
- User-provided latest log shows public endpoint checks failed because `http://134.199.144.115/...` was redirected by Caddy to `https://134.199.144.115/...`, then curl failed TLS with `tlsv1 alert internal error`.
- Direct diagnostic probes in the latest user-provided log returned `HTTP/1.1 308 Permanent Redirect` from `Server: Caddy` to `https://134.199.144.115/...` for `/health`, `/ready`, and `/deployment/status`.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | file exists and was inspected |
| workflow trigger truth | proven | push-triggered runs appeared |
| SSH key format truth | proven | `Prepare SSH key` passes |
| SSH auth truth | proven after droplet authorization | workflow advanced beyond SSH into deploy/public checks per latest user-provided log |
| remote repo sync truth | reached | deploy step advanced far enough to reach post-deploy endpoint checks |
| host bootstrap truth | reached | deploy step advanced far enough to reach post-deploy endpoint checks |
| `.env.production` truth | reached | deploy did not stop at missing/placeholder env before post-deploy checks |
| local service health truth | reached | deploy did not stop at local `/health`, `/ready`, or `/deployment/status` before post-deploy checks |
| public endpoint truth | fixed pending rerun | Caddy HTTP-to-HTTPS redirect on bare IP caused TLS failure; repo fix pushed |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Repo-Side Changes Made In This Cleanup Pass

- Improved `Post-deploy live endpoint checks` in the deploy workflow with HTTP status, body preview, scheme validation, redirect reporting, and direct droplet HTTP probes.
- Pinned workflow target values to the intended deployment target: `root@134.199.144.115:22`, app dir `/opt/xrp-hbar-apex`, and `BASE_URL=http://134.199.144.115`.
- Added remote synced commit output to the SSH deploy step for future remote repo sync proof.
- Added deploy-key fingerprint and public-key output to the workflow so SSH auth failures can be matched without exposing private key material.
- Added `auto_https off` to the runtime Caddyfile so IP-based HTTP health checks are not redirected to invalid bare-IP HTTPS.
- Added canonical repo docs:
  - `deployment/runtime-autopush-backlog.md`
  - `deployment/github-auto-push-gap-analysis.md`
  - `deployment/github-auto-deploy-setup.md`
  - `deployment/secret-placement-map.md`
- Updated issue #1 to track current proof gates instead of stale missing-scaffold language.

## Current First Failing Proof Gate

`public endpoint truth` was the current first failing proof gate in the latest user-provided run.

Current exact blocker: Caddy redirected bare-IP HTTP checks to `https://134.199.144.115/...`; curl then failed TLS on the IP target. Repo fixes have been pushed to disable Caddy automatic HTTPS for this IP-based deployment and to avoid masking redirects with `curl --location`.

## Exact Next Step

Run `DigitalOcean Auto Deploy` again on `main` after commits `f40e469c21c384a48ce9eb4c95e59667314a562c` and `956671dd131ccd6a7118175d47c3c2cbd2da1163`. The next run should redeploy the updated Caddyfile and then recheck public `/health`, `/ready`, and `/deployment/status` over HTTP.

## Strict Success Standard

Auto-deploy is not fully proven until a fresh `main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
