# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_BLOCKED`, `END_TO_END_NOT_VERIFIED`.

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
- Run `29469334854` reached `Deploy to DigitalOcean droplet over SSH`, proving `Prepare SSH key` no longer fails on private-key format.
- Run `29469474129` printed deploy key fingerprint `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I (ED25519)` and failed with `Permission denied (publickey)`.
- Run `29469547563` printed deploy public key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy` and failed with `Permission denied (publickey)`.
- DigitalOcean account-level SSH keys visible through the connected API do not match fingerprint `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I`.

## Current User-Reported State

The user reports local-machine SSH auth to the droplet was proven manually. This ledger treats that as separate from GitHub Actions SSH auth. GitHub Actions SSH auth is currently blocked by the public-key rejection shown in runs `29469474129` and `29469547563`.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | file exists and was inspected |
| workflow trigger truth | proven | push-triggered runs appeared |
| SSH key format truth | proven | `Prepare SSH key` passed in runs `29469334854`, `29469474129`, and `29469547563` |
| SSH auth truth | blocked | `Permission denied (publickey)` in run `29469547563`; deploy key fingerprint is `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I` |
| remote repo sync truth | not reached | SSH auth fails before remote commands execute |
| host bootstrap truth | not reached | requires SSH deploy step to reach remote shell |
| `.env.production` truth | not reached | host-only file, never committed |
| local service health truth | not reached | deploy script checks local endpoints after Docker Compose starts |
| public endpoint truth | not reached in latest runs | post-deploy checks are skipped while SSH auth fails |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Repo-Side Changes Made In This Cleanup Pass

- Improved `Post-deploy live endpoint checks` in the deploy workflow with HTTP status, body preview, scheme validation, trailing-slash normalization, and direct droplet HTTP probes when `BASE_URL` checks fail.
- Added remote synced commit output to the SSH deploy step for future remote repo sync proof.
- Added deploy-key fingerprint and public-key output to the workflow so SSH auth failures can be matched without exposing private key material.
- Added canonical repo docs:
  - `deployment/runtime-autopush-backlog.md`
  - `deployment/github-auto-push-gap-analysis.md`
  - `deployment/github-auto-deploy-setup.md`
  - `deployment/secret-placement-map.md`
- Updated issue #1 to track the current proof gates instead of stale missing-scaffold language.
- Preserved historical failure evidence while separating it from current proof gates.

## Current First Failing Proof Gate

`SSH auth truth` is the current first failing proof gate.

Current exact blocker: GitHub Actions can parse the `DIGITALOCEAN_SSH_KEY` private key and derive a public key, but the droplet rejects that key for the configured SSH user. The current Actions key fingerprint is `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I` and public key is `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.

## Exact Next Step

Authorize the public key above for the configured droplet user, expected `root`, by adding it to `/root/.ssh/authorized_keys` on `134.199.144.115`, or replace GitHub Actions secret `DIGITALOCEAN_SSH_KEY` with the private key that matches a public key already authorized for that droplet user. Then rerun the latest failed workflow.

## Strict Success Standard

Auto-deploy is not proven until a fresh `main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
