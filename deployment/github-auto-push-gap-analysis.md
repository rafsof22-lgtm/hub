# GitHub Auto Deploy Gap Analysis

Last updated: 2026-07-16

## Direct Answer

The repo-side deployment scaffold is present and the `DigitalOcean Auto Deploy` workflow has been restored on `main`. The remaining exercised blocker is not a missing-repo-file gap; it is SSH authorization from GitHub Actions to the DigitalOcean droplet.

## Proven

- `main` is the deployment branch.
- `.github/workflows/digitalocean-auto-deploy.yml` exists again after restore commit `4a5ed6a83de467ae944137ac43d331cc495a8364` and was re-fetched successfully.
- `deployment/runtime-scaffold-pack/deploy.sh` exists.
- `deployment/runtime-scaffold-pack/docker-compose.prod.yml` exists.
- `deployment/runtime-scaffold-pack/Caddyfile` exists.
- `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/` contains Dockerfile, requirements, and Flask app.
- The app exposes `/health`, `/ready`, and `/deployment/status`.
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.
- The latest exercised run `29469547563`, job `87562750570`, passed deploy-file validation and `Prepare SSH key`.

## Fixed Repo-Side

- Restored the missing `DigitalOcean Auto Deploy` workflow on current `main`.
- The workflow validates required deploy files before SSH.
- The workflow normalizes common SSH private-key paste formats.
- The workflow can read deploy settings from GitHub Actions variables or secrets with safe defaults.
- The Caddyfile includes both `:80` fallback and configured domain routing through `DOMAIN`.
- The deploy script includes local health gates after compose startup.
- Public endpoint checks emit HTTP status/body previews and direct-droplet diagnostic probes on failure.
- Runtime docs and issue tracking have been realigned to the latest exercised proof gate.

## Current First Failing Proof Gate

`SSH auth truth` is the current first failing proof gate from the newest exercised run available to this agent.

Evidence:

- Run `29469547563`
- Job `87562750570`
- First failing step: `Deploy to DigitalOcean droplet over SSH`
- Error: `Permission denied (publickey)`
- Derived public key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`
- Derived fingerprint: `SHA256:EW6NvPhLbV8CxvvfGme6iSLTzyAii4AiSCQN2Cb+z6I (ED25519)`

## Still Blocked Until Fresh Run Evidence

- Whether restored workflow commit `4a5ed6a83de467ae944137ac43d331cc495a8364` creates a run visible in GitHub Actions.
- Whether `DIGITALOCEAN_SSH_KEY` is currently valid in GitHub Actions for the droplet user.
- Whether GitHub Actions can SSH into `root@134.199.144.115`.
- Whether `/opt/xrp-hbar-apex` can be reset to `origin/main`.
- Whether `.env.production` exists on the droplet and has real values.
- Whether Docker and Compose are installed and healthy on the host.
- Whether local health endpoints pass from inside the host.
- Whether `BASE_URL` points to the live intended target.
- Whether public `/health`, `/ready`, and `/deployment/status` pass.

## Not Yet In Scope As Proven

- VTI runtime proof.
- Email/newsletter live-ingestion proof.
- Any claim that the deployed host matches the latest commit.

## Current Best Next Test

Exercise the restored `DigitalOcean Auto Deploy` workflow on `main`. If it still derives the same public key and fails with `Permission denied (publickey)`, the next blocker is external to repo code: authorize that public key for the configured droplet user or replace the GitHub Actions secret with a private key whose public key is already authorized on the droplet.