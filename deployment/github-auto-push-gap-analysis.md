# GitHub Auto Deploy Gap Analysis

Last updated: 2026-07-16

## Direct Answer

The repo-side deployment scaffold is present, the `DigitalOcean Auto Deploy` workflow is restored on `main`, and the core GitHub-to-DigitalOcean deployment path has been proven end to end for the current scaffold. The smallest VTI copied-link/transcript/OCR smoke route is now also deployed and proven from the public proof URL.

Latest successful run: `29486503772` / `DigitalOcean Auto Deploy #99`

Successful job: `87582140004`

Deployed commit: `34a6749865895a7cbe6f36c18affe3e0fd0dee59`

## Proven

- `main` is the deployment branch.
- `.github/workflows/digitalocean-auto-deploy.yml` exists, pins the proof target values, and includes VTI smoke checks.
- Markdown-only proof/doc updates are ignored by the deploy workflow to reduce unnecessary redeploy loops.
- `deployment/runtime-scaffold-pack/deploy.sh` exists and completed.
- `deployment/runtime-scaffold-pack/docker-compose.prod.yml` exists.
- `deployment/runtime-scaffold-pack/Caddyfile` exists.
- `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/` contains Dockerfile, requirements, and Flask app.
- The app exposes `/health`, `/ready`, `/deployment/status`, `/vti/status`, and `/vti/smoke`.
- Required deploy-file validation passed.
- `Prepare SSH key` passed.
- GitHub Actions SSH connected to `root@134.199.144.115:22`.
- Remote repo sync reset the droplet to `34a6749865895a7cbe6f36c18affe3e0fd0dee59`.
- Docker Compose pulled/built/started Postgres, Redis, API, worker, and Caddy.
- Public endpoint checks passed:
  - `http://134.199.144.115/health` -> `200`
  - `http://134.199.144.115/ready` -> `200`
  - `http://134.199.144.115/deployment/status` -> `200`
  - `http://134.199.144.115/vti/status` -> `200`
  - `POST http://134.199.144.115/vti/smoke` -> `200`
- VTI smoke proof returned `proof_label=VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN`, with copied link, manual transcript, and OCR text captured.

## Fixed Repo-Side

- Restored the missing `DigitalOcean Auto Deploy` workflow on current `main`.
- Normalized and validated common SSH private-key paste formats.
- Pinned non-secret proof target values to avoid stale GitHub variable drift.
- Added explicit target, connected user, host, and synced commit proof lines.
- Preserved local health gates and public endpoint body previews.
- Removed the obsolete Docker Compose `version` field that produced a warning during deploy.
- Added stale `runtime-scaffold-pack-*` container cleanup before Docker Compose recreate.
- Added `/vti/status` and `POST /vti/smoke` to the runtime scaffold.
- Added public VTI smoke checks to the deploy workflow.
- Added `paths-ignore: ['**/*.md']` so ledger-only updates do not trigger unnecessary production redeploys.
- Updated runtime proof ledger, backlog, and issue tracking to current truth.

## Superseded Blockers

- Earlier run `29469547563` failed at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`, but that run checked out old commit `b46e969be6110e3326cf0b4236dd83cc3c93f445`. That blocker is superseded by successful fresh current-main runs.
- Run `29485900138` / `DigitalOcean Auto Deploy #95` failed on stale Docker container-name conflict for `runtime-scaffold-pack-redis-1`; that blocker is superseded by the stale-container cleanup and successful run #97.
- The previous VTI endpoint-missing blocker is superseded by commit `dd57d94a26071acdd1a5eca2839acc7b599b608c` and successful run #99.

## Current First Remaining Proof Gate

There is no remaining core GitHub-to-DigitalOcean deploy blocker. There is no remaining VTI smoke-route blocker.

The first remaining framework-specific gates are:

1. Full VTI media/caption/OCR worker proof beyond the smoke route.
2. Email/newsletter recurring production-ingestion proof beyond the bounded Gmail live pass.
3. Optional real-domain public endpoint proof if a domain replaces the IP-based proof URL.

## Not Yet Proven

- Automatic media download or platform caption fetch.
- Automatic frame/OCR worker.
- Claim extraction and verification worker.
- Persistent VTI evidence-store/result endpoint beyond the stateless smoke response.
- Gmail/newsletter recurring ingestion route with durable registry/digest output on a schedule.
- Domain-based endpoint proof beyond the IP proof URL.

## Current Best Next Test

Build the next narrow VTI worker layer: take a real copied link plus transcript/OCR input, persist a source record, return a durable evidence result, and then add that result endpoint to the deploy proof chain. Keep issue #1 open until that next live framework layer is proven or split into its own tracker issue.
