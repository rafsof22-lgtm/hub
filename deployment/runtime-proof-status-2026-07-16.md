# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `WORKFLOW_RESTORED`, `SSH_KEY_FORMAT_BLOCKED`, `END_TO_END_NOT_VERIFIED`.

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
- `DigitalOcean Auto Deploy` was restored on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` and re-fetched successfully.
- The deployment scaffold files exist in the repo.
- The Flask app exposes `/health`, `/ready`, and `/deployment/status`.
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.
- DigitalOcean API confirmed droplet `584697763` is active in `syd1` with public IPv4 `134.199.144.115`.
- DigitalOcean account key list contains public key id `57820900`, name `github-actions-deploy-2026-07-16-active`, fingerprint `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`.
- A read-only Gmail search on 2026-07-16 found an owner-controlled DigitalOcean reset email for this exact droplet. No password, token, or reset value is recorded in repo/docs/chat.
- Earlier push-triggered workflow runs proved workflow trigger behavior.
- Earlier run `29469547563`, job `87562750570`, passed `Prepare SSH key` and then failed at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`.
- New rerun requested on 2026-07-16 was accepted by GitHub Actions.
- New latest attempt job `87568284263` failed earlier at `Prepare SSH key`.

## Latest Exercised Run

- Run: `29469547563`
- Latest job attempt: `87568284263`
- Checked-out commit in that rerun: `b46e969be6110e3326cf0b4236dd83cc3c93f445`
- First failing step: `Prepare SSH key`
- Exact error: `DIGITALOCEAN_SSH_KEY must contain a full private key block, or a base64-encoded private key block`
- `Deploy to DigitalOcean droplet over SSH`: skipped
- `Post-deploy live endpoint checks`: skipped

This latest rerun supersedes the previous SSH-auth blocker for current proof-gate ordering. The current first blocker is now secret content/format, before SSH auth can be tested again.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | restored and re-fetched on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` |
| workflow trigger/rerun truth | proven | connected GitHub tool accepted rerun request for run `29469547563` |
| scaffold file truth | proven in latest rerun | validation passed before SSH key preparation |
| SSH key format truth | blocked now | latest job `87568284263` failed at `Prepare SSH key` |
| DigitalOcean account-key truth | previously proven | account key id `57820900` exists, but latest run did not derive/compare a public key because secret parsing failed |
| existing-droplet key authorization truth | not reached now | previous attempt failed with `Permission denied (publickey)`, but latest attempt did not reach SSH |
| owner recovery route truth | partial | Gmail search found reset email for this droplet; credential value remains owner-only and unrecorded |
| SSH auth truth | not reached now | requires `Prepare SSH key` to pass again |
| remote repo sync truth | not reached | requires workflow reaching remote shell and printing `[remote] synced_commit=...` |
| host bootstrap truth | not reached | requires remote Docker/compose execution evidence |
| `.env.production` truth | not reached | must be verified on droplet, never committed |
| local service health truth | not reached | deploy script checks local `/health`, `/ready`, `/deployment/status` on host |
| public endpoint truth | not reached | public checks only run after SSH deploy completes |
| VTI runtime truth | not started | only after generic deploy proof |
| email/newsletter live-ingestion truth | not started | only after generic deploy or separate Gmail proof |

## Repo-Side Changes Confirmed

- Restored `.github/workflows/digitalocean-auto-deploy.yml` on `main` in commit `4a5ed6a83de467ae944137ac43d331cc495a8364` after the current branch returned 404 for that path.
- Workflow includes required file validation, SSH private-key cleanup/fingerprinting, remote synced-commit output, deploy script execution, and public endpoint checks.
- `deployment/digitalocean-key-and-secret-runbook.md` records the owner-controlled reset-email recovery clue without storing the credential value.
- This proof-status update records latest rerun job `87568284263` and current first failing gate.

## Current First Failing Proof Gate

`SSH key format truth` is the current first failing proof gate from the newest exercised run available to this agent.

Exact blocker: GitHub Actions secret `DIGITALOCEAN_SSH_KEY` currently does not resolve inside the workflow to either a full private key block or a base64-encoded private key block.

## Exact Next Step

In GitHub repo settings, replace Actions Secret `DIGITALOCEAN_SSH_KEY` with exactly one of:

1. The full private OpenSSH key block whose public key is authorized on the droplet, including:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

2. Or a base64-encoded version of that complete private key block.

Do not include `DIGITALOCEAN_SSH_KEY=`, quotes, markdown fences, `COPY_START`, `COPY_END`, comments, or any wrapper text.

After the secret is corrected, rerun `DigitalOcean Auto Deploy`. The next expected gate is `Deploy to DigitalOcean droplet over SSH`; if that passes, continue to remote repo sync, `.env.production`, Docker/Compose, local health, and public endpoint checks.

## Strict Success Standard

Auto-deploy is not fully proven until a fresh `main` workflow run succeeds, the host pulls the target commit, `deploy.sh` completes without manual intervention, and public `/health`, `/ready`, and `/deployment/status` all pass.
