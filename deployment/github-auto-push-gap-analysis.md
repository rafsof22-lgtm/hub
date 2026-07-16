# GitHub Auto Deploy Gap Analysis

Last updated: 2026-07-16

## Direct Answer

The repo-side deployment scaffold and workflow are present. The remaining proof gaps are not missing-repo-file gaps; they are runtime proof gates that must be advanced by a fresh GitHub Actions deploy run.

## Proven

- `main` is the deployment branch.
- `.github/workflows/digitalocean-auto-deploy.yml` exists.
- `deployment/runtime-scaffold-pack/deploy.sh` exists.
- `deployment/runtime-scaffold-pack/docker-compose.prod.yml` exists.
- `deployment/runtime-scaffold-pack/Caddyfile` exists.
- `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/` contains Dockerfile, requirements, and Flask app.
- The app exposes `/health`, `/ready`, and `/deployment/status`.
- The deploy script validates `.env.production`, rejects placeholders, starts Docker Compose, and checks local health endpoints.

## Fixed Repo-Side

- The workflow now validates required deploy files before SSH.
- The workflow normalizes common SSH private-key paste formats.
- The workflow can read deploy settings from GitHub Actions variables or secrets.
- The Caddyfile includes both `:80` fallback and `{$DOMAIN}` routing.
- The deploy script includes local health gates after compose startup.
- Public endpoint checks now emit HTTP status/body previews and direct-droplet diagnostic probes on failure.

## Still Blocked Until Fresh Run Evidence

- Whether `DIGITALOCEAN_SSH_KEY` is currently valid in GitHub Actions.
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

Trigger a fresh `main` deploy run and inspect the first failing step. The current workflow should classify failures better than earlier runs.
