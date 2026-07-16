# GitHub Auto Deploy Gap Analysis

Last updated: 2026-07-16

## Direct Answer

The repo-side deployment scaffold is present, the `DigitalOcean Auto Deploy` workflow is restored on `main`, and the core GitHub-to-DigitalOcean deployment path has now been proven end to end for the current scaffold.

Fresh successful run: `29485379774` / `DigitalOcean Auto Deploy #89`

Successful job: `87578507636`

Deployed commit: `d3aaf301334450cf1a216961c76c620c5aba6d7a`

## Proven

- `main` is the deployment branch.
- `.github/workflows/digitalocean-auto-deploy.yml` exists and pins the proof target values.
- `deployment/runtime-scaffold-pack/deploy.sh` exists and completed.
- `deployment/runtime-scaffold-pack/docker-compose.prod.yml` exists.
- `deployment/runtime-scaffold-pack/Caddyfile` exists.
- `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/` contains Dockerfile, requirements, and Flask app.
- The app exposes `/health`, `/ready`, and `/deployment/status`.
- Required deploy-file validation passed.
- `Prepare SSH key` passed.
- GitHub Actions SSH connected to `root@134.199.144.115:22`.
- Remote repo sync reset the droplet to `d3aaf301334450cf1a216961c76c620c5aba6d7a`.
- Docker Compose pulled/built/started Postgres, Redis, API, worker, and Caddy.
- Public endpoint checks passed:
  - `http://134.199.144.115/health` -> `200`
  - `http://134.199.144.115/ready` -> `200`
  - `http://134.199.144.115/deployment/status` -> `200`

## Fixed Repo-Side

- Restored the missing `DigitalOcean Auto Deploy` workflow on current `main`.
- Normalized and validated common SSH private-key paste formats.
- Pinned non-secret proof target values to avoid stale GitHub variable drift.
- Added explicit target, connected user, host, and synced commit proof lines.
- Preserved local health gates and public endpoint body previews.
- Updated runtime proof ledger and backlog to reflect the successful deploy.
- Removed the obsolete Docker Compose `version` field that produced a warning during deploy.

## Superseded Blocker

Earlier run `29469547563` failed at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`, but that run checked out old commit `b46e969be6110e3326cf0b4236dd83cc3c93f445`. That blocker is superseded by successful fresh current-main run `29485379774`.

## Current First Remaining Proof Gate

There is no remaining core GitHub-to-DigitalOcean deploy blocker proven by the latest run. The first remaining framework-specific gates are:

1. VTI runtime smoke proof.
2. Email/newsletter live-ingestion proof.
3. Optional real-domain public endpoint proof if a domain replaces the IP-based proof URL.

## Not Yet Proven

- VTI copied-link/transcript/OCR end-to-end route.
- Gmail/newsletter live-ingestion route with durable registry/digest output.
- Domain-based endpoint proof beyond the IP proof URL.

## Current Best Next Test

Run one small VTI or Gmail/newsletter smoke test and record its output in the appropriate framework ledger. Keep issue #1 open until those live framework layers are either proven or split into their own tracker issue.
