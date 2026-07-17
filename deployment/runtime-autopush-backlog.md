# Runtime Autopush Backlog

Last updated: 2026-07-17

Proof labels: `REPO_SIDE_TRUTH_ALIGNED`, `WORKFLOW_TARGET_VALUES_PINNED`, `WORKFLOW_TRIGGER_PROVEN`, `SSH_KEY_FORMAT_PROVEN`, `HOST_KEY_PLACEMENT_PROVEN_BY_OWNER`, `SSH_AUTH_PROVEN`, `REMOTE_REPO_SYNC_PROVEN`, `HOST_BOOTSTRAP_PROVEN`, `PUBLIC_ENDPOINTS_PROVEN`, `CORE_RUNTIME_DEPLOYMENT_PROVEN`, `VTI_SMOKE_ROUTE_PROVEN`, `FRAMEWORK_LIVE_LAYERS_PARTIAL`, `HYBRID_LLM_ROUTER_ARCHITECTURE_DOCUMENTED`, `HYBRID_LLM_ROUTER_FUTURE_ONLY`.

## Current Deployment Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`
- Main droplet IP: `134.199.144.115`
- Repair droplet IP: `170.64.230.87` (keep untouched unless explicitly approved)
- SSH user: `root`
- SSH port: `22`
- App dir: `/opt/xrp-hbar-apex`
- Runtime scaffold: `deployment/runtime-scaffold-pack`
- Proof BASE_URL: `http://134.199.144.115`

## Current Proof Gates

| gate | status | evidence |
|---|---|---|
| workflow file truth | proven | workflow pins deploy target values and runs VTI/email smoke checks |
| scaffold file truth | proven | required deploy-file validation is part of workflow |
| SSH key format truth | previously proven | `Prepare SSH key` passed in prior runs and derived the expected public key |
| host-side key placement truth | previously proven by owner console output | deploy public key appeared in `/root/.ssh/authorized_keys`; permissions and `sshd -T` output were compatible |
| SSH auth truth | previously proven | prior successful deploy runs connected as `root` to `134.199.144.115` |
| remote repo sync truth | previously proven | prior run logs showed `[remote] synced_commit=...` |
| host bootstrap truth | previously proven | Docker Compose pulled/built/started runtime services |
| `.env.production` truth | operationally proven for scaffold, not value-exposed | deploy script and services completed in prior runs; secret values remain host-only |
| public scaffold endpoint truth | previously proven | `/health`, `/ready`, and `/deployment/status` returned `200` from `http://134.199.144.115` in prior proof |
| user-supplied current baseline | partial | as of 2026-07-17 user context: DigitalOcean Auto Deploy #119 reached main host and passed scaffold route checks, but full production remained blocked by Gmail runtime credentials |
| Gmail runtime credential truth | current blocker | needs host/runtime values for `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, and `GMAIL_OAUTH_REFRESH_TOKEN`; values must not be stored in repo or chat |
| VTI full media/caption/OCR worker truth | not yet proven | smoke/manual intake is not automatic media download, caption fetch, OCR worker, or claim verification worker |
| email/newsletter recurring ingestion truth | not yet proven | no recurring production ingest worker/schedule is proven |
| hybrid LLM router architecture | documented, future-only | see `deployment/hybrid-llm-router-architecture.md`; no live router routes or provider calls are proven |

## Repo-Side Backlog

1. Keep `deployment/runtime-proof-status-2026-07-16.md` as historical proof for successful core deploy and VTI smoke proof, but do not treat it as a full-production claim.
2. Keep issue #1 open until the remaining live framework layer is either full VTI media/caption/OCR worker proof, Gmail runtime proof, or split into separate tracker issues.
3. Continue using first-failing-gate reporting for any future deploy run.
4. Avoid storing host secrets in repo; `.env.production` stays host-only.
5. Markdown-only proof/docs changes are ignored by the deploy workflow to avoid unnecessary runtime redeploy loops.
6. Keep `deployment/hybrid-llm-router-architecture.md` as the single source for hybrid router architecture until a live router module exists.

## Remaining Runtime / Framework Backlog

1. Prove Gmail runtime readiness with host-only credential values:
   - `GMAIL_OAUTH_CLIENT_ID`
   - `GMAIL_OAUTH_CLIENT_SECRET`
   - `GMAIL_OAUTH_REFRESH_TOKEN`
2. Run bounded Gmail fetch proof after token-refresh readiness passes.
3. Build and prove a real VTI worker beyond smoke: official transcript/caption fetch when possible, uploaded transcript/OCR-file intake, source-record persistence, and evidence-result output.
4. Build and prove email/newsletter recurring production ingestion beyond the bounded Gmail pass.
5. If a real domain replaces the IP proof URL later, rerun public endpoint checks against that domain.

## Hybrid LLM Router Backlog

These tasks are future-only and must not break the current VTI/email deployment path.

1. Add a router interface for task type, safety tier, context size, estimated token cost, and preferred worker.
2. Add dry-run routing before any provider calls.
3. Add provider adapters for OpenRouter, LiteLLM, DeepSeek, Kimi, Qwen, local Llama, OCR/vision, and embeddings.
4. Add routing policy defaults for GPT-5 planning/final decisions, DeepSeek coding, Kimi research/long context, Qwen classification, local Llama repetitive jobs, and OCR/vision extraction.
5. Add cost guards for per-task and monthly limits, including the under-AUD-100/month planning target.
6. Add health checks for enabled providers that verify access without exposing secret values.
7. Add fallback/fail-closed behavior and audit metadata without storing sensitive prompts or credentials.
8. Add live router status and smoke endpoints only after the current deployment proof gates remain stable.

## Router Secret / Env Placement Backlog

Secret values must not be committed. Track names only until implementation.

| name | placement | status |
|---|---|---|
| `OPENROUTER_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs it | future-only |
| `DEEPSEEK_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs it | future-only |
| `KIMI_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs it | future-only |
| `QWEN_API_KEY` | host runtime secret store or GitHub Actions Secret if CI needs it | future-only |
| `LITELLM_MASTER_KEY` | host runtime secret store | future-only |
| `LOCAL_LLM_BASE_URL` | host runtime variable | future-only |
| `OCR_VISION_ENDPOINT` | host runtime variable or secret depending on provider | future-only |
| `EMBEDDING_MODEL` | host runtime variable | future-only |

## Latest Proven Deploy

Historical proof retained from prior runs:

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

User-supplied current baseline for this update: DigitalOcean Auto Deploy #119 reached the main host and passed scaffold route checks, but full production remained blocked by Gmail runtime credentials. Reverify the exact run log before promoting this to a repo-side proof label.
