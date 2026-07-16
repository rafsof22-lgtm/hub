# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `WORKFLOW_RESTORED`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_BLOCKED`, `END_TO_END_NOT_VERIFIED`.

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
- `DigitalOcean Auto Deploy` was restored on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` and re-fetched successfully.
- The deployment scaffold files exist in the repo.
- The Flask app exposes `/health`, `/ready`, and `/deployment/status`.
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- Earlier push-triggered workflow runs proved workflow trigger behavior.
- Earlier run `29463550411` proved the prior first failing step was `Prepare SSH key` with invalid private-key format.
- Later runs proved `Prepare SSH key` passes and derives public key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`.
- Latest available rerun inspected in this pass: run `29469547563`, job `87562750570`.
- Latest available rerun still fails at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`.
- Latest available rerun does not reach remote repo sync, host bootstrap, `.env.production`, local health, public endpoint, VTI, or email-ingestion proof.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | restored and re-fetched on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` |
| workflow trigger truth | proven historically | prior push-triggered runs appeared; connected run list is limited and did not expose a new run for the restore commit |
| scaffold file truth | proven in latest exercised run | validation passed in run `29469547563`, job `87562750570` |
| SSH key format truth | proven | `Prepare SSH key` passed in latest exercised run |
| SSH auth truth | blocked | latest exercised run failed before remote shell with `Permission denied (publickey)` |
| remote repo sync truth | not reached | requires workflow reaching remote shell and printing `[remote] synced_commit=...` |
| host bootstrap truth | not reached | requires remote Docker/compose execution evidence |
| `.env.production` truth | not reached | must be verified on droplet, never committed |
| local service health truth | not reached | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not reached in latest exercised run | public checks only run after SSH deploy completes |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Repo-Side Changes Confirmed

- Restored `.github/workflows/digitalocean-auto-deploy.yml` on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` after the current branch returned 404 for that path.
- Workflow includes required file validation, SSH private-key cleanup/fingerprinting, remote synced-commit output, deploy script execution, and public endpoint checks.
- Deployment docs and issue #1 should treat SSH auth as the current exercised blocker until a newer run proves remote shell access.

## Current First Failing Proof Gate

`SSH auth truth` is the current first failing proof gate from the newest exercised run available to this agent.

Exact blocker: the workflow parses the private key and derives the public key, but SSH to the configured droplet user fails with `Permission denied (publickey)` before remote commands execute.

## Exact Next Step

Use GitHub Actions or a supported run-inspection path to exercise restored workflow commit `4a5ed6a83de467ae944137ac43d331cc495a8364`. If it still derives public key `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy` and fails with `Permission denied (publickey)`, authorize that public key for the configured droplet user or replace `DIGITALOCEAN_SSH_KEY` with the private key for an already-authorized droplet key.

## Strict Success Standard

Auto-deploy is not fully proven until a fresh `main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.