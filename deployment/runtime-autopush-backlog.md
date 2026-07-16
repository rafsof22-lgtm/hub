# Runtime Autopush Backlog

Last updated: 2026-07-16

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `WORKFLOW_TRIGGER_PROVEN`, `SSH_KEY_FORMAT_PROVEN`, `HOST_KEY_PLACEMENT_PROVEN_BY_OWNER`, `SSH_AUTH_PROVEN`, `REMOTE_REPO_SYNC_PROVEN`, `HOST_BOOTSTRAP_PROVEN`, `PUBLIC_ENDPOINTS_PROVEN`, `CORE_RUNTIME_DEPLOYMENT_PROVEN`, `VTI_SMOKE_ROUTE_PROVEN`, `FRAMEWORK_LIVE_LAYERS_PARTIAL`.

## Current Deployment Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`
- Droplet IP: `134.199.144.115`
- SSH user: `root`
- SSH port: `22`
- App dir: `/opt/xrp-hbar-apex`
- Runtime scaffold: `deployment/runtime-scaffold-pack`
- Proof BASE_URL: `http://134.199.144.115`

## Current Proof Gates

| gate | status | evidence |
|---|---|---|
| workflow file truth | proven | workflow pins deploy target values and runs VTI smoke checks |
| workflow trigger truth | proven | latest push run `29486503772` / `DigitalOcean Auto Deploy #99` executed commit `34a6749865895a7cbe6f36c18affe3e0fd0dee59` |
| scaffold file truth | proven | required deploy-file validation passed |
| SSH key format truth | proven | `Prepare SSH key` passed and derived the expected public key |
| host-side key placement truth | proven by owner console output | deploy public key appears in `/root/.ssh/authorized_keys`; permissions and `sshd -T` output are compatible |
| SSH target mismatch risk | repo-side fixed | workflow hardcodes `root@134.199.144.115:22` for proof deployment |
| SSH auth truth | proven | run `29486503772`, job `87582140004`, connected as `root` |
| remote repo sync truth | proven | `[remote] synced_commit=34a6749865895a7cbe6f36c18affe3e0fd0dee59` |
| host bootstrap truth | proven | Docker Compose pulled/built/started runtime services |
| stale container conflict | fixed and proven | stale `runtime-scaffold-pack-*` cleanup added before compose recreate; latest run passed |
| `.env.production` truth | operationally proven for current scaffold | deploy script and services completed; secret values remain host-only |
| local service health truth | inferred through deploy completion | deploy script completed its local health wait before public checks |
| public endpoint truth | proven | `/health`, `/ready`, `/deployment/status` returned `200` from `http://134.199.144.115` |
| VTI smoke route truth | proven | `/vti/status` returned `200`; `POST /vti/smoke` returned `200` with copied-link, transcript, and OCR-text captured |
| VTI full media/caption/OCR worker truth | not yet proven | no automatic media download, caption fetch, OCR worker, or claim verification worker yet |
| email/newsletter live-access truth | partially proven | Gmail bounded pass produced sanitized durable registry/digest output and deployment-review label action |
| email/newsletter recurring ingestion truth | not yet proven | no recurring production ingest worker/schedule is proven |

## Repo-Side Backlog

1. Keep `deployment/runtime-proof-status-2026-07-16.md` as the active proof ledger for successful core deploy and VTI smoke proof.
2. Keep issue #1 open until the remaining live framework layer is either full VTI media/caption/OCR worker proof or split into a separate tracker issue.
3. Continue using first-failing-gate reporting for any future deploy run.
4. Avoid storing host secrets in repo; `.env.production` stays host-only.
5. Markdown-only proof/docs changes are ignored by the deploy workflow to avoid unnecessary runtime redeploy loops.

## Remaining Runtime / Framework Backlog

1. Build and prove a real VTI worker beyond smoke: official transcript/caption fetch when possible, uploaded transcript/OCR-file intake, source-record persistence, and evidence-result output.
2. Build and prove email/newsletter recurring production ingestion beyond the bounded Gmail pass.
3. If a real domain replaces the IP proof URL later, rerun public endpoint checks against that domain.

## Latest Proven Deploy

- Run: `29486503772` / `DigitalOcean Auto Deploy #99`
- Job: `87582140004`
- Commit deployed: `34a6749865895a7cbe6f36c18affe3e0fd0dee59`
- Result: success
- Public proof:
  - `http://134.199.144.115/health` -> `200`
  - `http://134.199.144.115/ready` -> `200`
  - `http://134.199.144.115/deployment/status` -> `200`
  - `http://134.199.144.115/vti/status` -> `200`
  - `POST http://134.199.144.115/vti/smoke` -> `200`, proof label `VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN`
