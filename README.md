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

Tracked blocker: https://github.com/rafsof22-lgtm/hub/issues/1
