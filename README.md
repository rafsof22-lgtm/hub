# XRP/HBAR Apex Runtime Hub

Deployment scaffold for the XRP/HBAR Apex Intelligence OS runtime.

## Current scope

- GitHub Actions workflow for DigitalOcean SSH deploy
- Docker Compose production stack with Flask API, worker placeholder, Postgres, Redis, and Caddy
- Health endpoints: `/health`, `/ready`, `/deployment/status`

## Production status

Scaffold files are committed to `main`, but production is not verified live yet.

Do not claim the runtime is live until:

- GitHub Actions secrets are configured.
- The DigitalOcean droplet has a real `deployment/runtime-scaffold-pack/.env.production` file.
- The workflow runs from `main` and completes.
- Droplet containers are healthy.
- Public endpoint checks pass for `/health`, `/ready`, and `/deployment/status`.
- A second harmless push proves auto-deploy updates the droplet without manual SSH deployment.

Latest verification trigger commit: 2026-07-15T10:35Z.

Secret/key setup runbook: `deployment/digitalocean-key-and-secret-runbook.md`

Tracked blocker: https://github.com/rafsof22-lgtm/hub/issues/1
