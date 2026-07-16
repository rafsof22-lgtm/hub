# Runtime Proof Status - 2026-07-16

Proof labels: `STANDING_AUTONOMY_APPROVED`, `DEPLOYMENT_DRIFT_CHECKED`, `GITHUB_ACTIONS_TRIGGER_VERIFIED`, `REPO_DOCS_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `SSH_KEY_FORMAT_PROVEN`, `SSH_AUTH_PROVEN`, `REMOTE_REPO_SYNC_PROVEN`, `HOST_BOOTSTRAP_PROVEN`, `PUBLIC_ENDPOINTS_PROVEN`, `CORE_RUNTIME_DEPLOYMENT_PROVEN`, `VTI_REAL_COPIED_LINK_SMOKE_PROVEN`, `VTI_FULL_MEDIA_PIPELINE_NOT_YET_PROVEN`, `EMAIL_NEWSLETTER_RECURRING_INGESTION_NOT_YET_PROVEN`.

## Scope

Target repo: `rafsof22-lgtm/hub`

Target branch: `main`

Target workflow: `.github/workflows/digitalocean-auto-deploy.yml`

Target droplet: `Digital-ocean-XRP-Hbar-Apex`

Target public IP: `134.199.144.115`

Expected app dir: `/opt/xrp-hbar-apex`

Expected deploy path: `deployment/runtime-scaffold-pack`

Proof BASE_URL: `http://134.199.144.115`

## Current Proven State

- GitHub repo exists and default branch is `main`.
- Connected GitHub app reports repo access and can update repo files/issues.
- Deployment scaffold files exist in the repo.
- The Flask app now exposes `/health`, `/ready`, `/deployment/status`, `/vti/status`, and `/vti/smoke`.
- DigitalOcean droplet target remains `root@134.199.144.115:22`, app dir `/opt/xrp-hbar-apex`.
- User-provided droplet console output proved the deploy public key was present in `/root/.ssh/authorized_keys`, with `PermitRootLogin yes`, `PubkeyAuthentication yes`, and `AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys2`.
- Workflow target values remain pinned:
  - `DIGITALOCEAN_HOST=134.199.144.115`
  - `DIGITALOCEAN_USER=root`
  - `DIGITALOCEAN_PORT=22`
  - `APP_DIR=/opt/xrp-hbar-apex`
  - `BASE_URL=http://134.199.144.115`
- Latest full workflow proof: `29486999105` / `DigitalOcean Auto Deploy #100`.
- Latest successful job: `87583747175`.
- Latest deployed commit: `d8228b76db37cf92cc09dea3cc7fe57e03f095e8`.
- Job `87583747175` passed all deploy steps:
  - `Validate required deploy files exist`
  - `Prepare SSH key`
  - `Deploy to DigitalOcean droplet over SSH`
  - `Post-deploy live endpoint checks`
- Run logs proved SSH connected to the expected host as `root`:
  - `deploy_target=root@134.199.144.115:22 app_dir=/opt/xrp-hbar-apex`
  - `[remote] connected_user=root`
  - `[remote] host=Digital-ocean-XRP-Hbar-Apex`
- Remote repo sync was proven by run log line `synced_commit=d8228b76db37cf92cc09dea3cc7fe57e03f095e8`.
- Host bootstrap was proven: Docker Compose pulled/built images, removed stale containers, started Postgres, Redis, API, worker, and Caddy containers.
- Public endpoint proof passed from GitHub Actions against `http://134.199.144.115`:
  - `/health` returned `200` with `{"env":"production","service":"xrp-hbar-apex","status":"ok","version":"0.1.0"}`.
  - `/ready` returned `200` with `{"postgres":"ok","redis":"ok","status":"ready"}`.
  - `/deployment/status` returned `200` with `framework_layers.vti_smoke=available` and `email_newsletter_ingestion=partial_live_access_not_recurring_proven`.
  - `/vti/status` returned `200` with `proof_label=VTI_SMOKE_ROUTE_AVAILABLE` and capabilities for copied-link metadata, manual transcript, OCR text, and source-record hashing.
  - `POST /vti/smoke` returned `200` with `proof_label=VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN`, `copied_link_captured=true`, `manual_transcript_captured=true`, and `ocr_text_captured=true`.
- Real copied-link proof details:
  - `source_url=https://ripple.com/solutions/stablecoin/`
  - `domain=ripple.com`
  - `platform=official-web-copied-link`
  - `source_id=41454f275f5e68c2179c43c7`
  - `transcript_word_count=17`
  - `ocr_word_count=9`

## Superseded Historical Blockers

- Old reruns of run `29469547563` checked out old commit `b46e969be6110e3326cf0b4236dd83cc3c93f445` and failed at `Deploy to DigitalOcean droplet over SSH` with `Permission denied (publickey)`. That evidence is superseded by fresh successful runs.
- Run `29485900138` / `DigitalOcean Auto Deploy #95` failed on a stale Docker container-name conflict for `runtime-scaffold-pack-redis-1`. That blocker is superseded by commit `c283fd0d63c502824a5141131ea8ca85f76bd000` and successful run #97.
- VTI endpoint missing is superseded by commit `dd57d94a26071acdd1a5eca2839acc7b599b608c` plus successful workflow run #99.
- Synthetic-link-only VTI smoke proof is superseded by real copied-link proof in run #100.

## Current Proof Gates

| gate | status | notes |
|---|---|---|
| workflow file truth | proven | workflow exists, pins target values, and includes VTI smoke checks |
| workflow trigger truth | proven | push run `29486999105` executed current `main` |
| scaffold file truth | proven | validation step passed |
| SSH key format truth | proven | `Prepare SSH key` passed and derived expected public key |
| host-side key placement truth | proven by owner console output | key present in `/root/.ssh/authorized_keys`; SSHD configured to read it |
| SSH auth truth | proven | job `87583747175` connected to `root@134.199.144.115:22` |
| remote repo sync truth | proven | `synced_commit=d8228b76db37cf92cc09dea3cc7fe57e03f095e8` |
| host bootstrap truth | proven | Docker Compose pull/build/start completed |
| `.env.production` truth | operationally proven for current scaffold | deploy script and services passed; secret values remain host-only and are not recorded here |
| local service health truth | inferred through deploy completion | deploy script reached completion after waiting for local health endpoints |
| public endpoint truth | proven | `/health`, `/ready`, `/deployment/status` returned `200` |
| VTI real copied-link smoke truth | proven | `/vti/status` and real-link `POST /vti/smoke` returned `200` from the public proof URL |
| VTI full media/caption/OCR worker truth | not yet proven | smoke route accepts copied link, manual transcript, and OCR text; it does not fetch media, captions, or frames automatically yet |
| email/newsletter live-access truth | partially proven | Gmail search/read/classify/label plus sanitized repo logs completed earlier |
| email/newsletter recurring ingestion truth | not yet proven | no scheduled/production recurring ingest worker is proven |
| real-domain proof | not applicable yet | IP proof URL remains the active target |

## Current First Remaining Proof Gate

The first remaining unproven framework-runtime gate is persistent VTI evidence storage/result retrieval, followed by full VTI media/caption/OCR worker proof. Email/newsletter recurring production ingestion is also still unproven.

## Exact Next Step

Persist the VTI smoke source record/evidence payload and expose a retrieval/result endpoint, then add that endpoint to the deploy proof chain. Keep email/newsletter recurring ingestion as the separate next production-ingestion gate.

## Strict Success Standard

Core deployment, SSH, remote sync, host bootstrap, public runtime endpoints, and real copied-link/transcript/OCR VTI smoke are proven for run `29486999105`. Do not mark persistent VTI evidence storage, full media extraction, automatic OCR, claim verification, domain proof, or recurring email/newsletter ingestion complete until each has its own end-to-end proof.
