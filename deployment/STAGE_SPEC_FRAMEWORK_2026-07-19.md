# XRP/HBAR Apex Runtime Hub — Verified Stage Specification and Framework

**Stage date:** 2026-07-19  
**Repository:** `rafsof22-lgtm/hub`  
**Canonical branch:** `main`  
**Specification branch:** `stage-spec-2026-07-19`  
**Runtime target:** DigitalOcean droplet `134.199.144.115`  
**Runtime path:** `/opt/xrp-hbar-apex`  
**Governed status:** `DEPLOYED_UNVERIFIED`  

## 1. Executive stage statement

The repository contains a deployable XRP/HBAR Apex Runtime Hub scaffold with a Flask API, PostgreSQL, Redis, Caddy, a placeholder worker, persistence-backed evidence routes, Gmail read-only proof routes, VTI copied-link/transcript/OCR intake routes, checkpoint scaffolds, evidence-pack generation, deployment automation, and a Jarvis federation contract adapter.

Historical GitHub Actions evidence proves that an earlier main-branch commit deployed successfully to the target DigitalOcean droplet and passed core public endpoint checks. The current repository has advanced materially beyond that historical deployed commit. Independent checks performed on 2026-07-19 could not connect to the public IP on port 80, so the currently deployed runtime state cannot be promoted to `DONE_VERIFIED` from the present environment.

The correct stage is therefore:

- repository implementation: `IMPLEMENTED`
- historical production deployment: `PROVEN_FOR_EARLIER_COMMIT`
- current main-to-runtime parity: `UNVERIFIED`
- public runtime availability on 2026-07-19: `UNREACHABLE_FROM_CURRENT_EGRESS`
- Gmail OAuth proof: `BLOCKED_EXTERNAL_CREDENTIAL`
- full VTI media/caption/OCR automation: `SCAFFOLDED_NOT_IMPLEMENTED`
- recurring newsletter ingestion: `SCAFFOLDED_NOT_ENABLED`
- Jarvis federation contract: `IMPLEMENTED_NOT_INTEGRATED`

## 2. Non-negotiable truth model

Every capability must be assigned one of these statuses:

| Status | Meaning |
|---|---|
| `SPEC_ONLY` | Documented only; no executable implementation. |
| `BACKLOGGED` | Accepted work item with no completed implementation. |
| `SCAFFOLDED` | Route, interface, table, or placeholder exists but does not perform the full intended operation. |
| `IMPLEMENTED_NOT_INTEGRATED` | Executable implementation exists but is not connected to the canonical runtime path. |
| `INTEGRATED_STAGING` | Integrated and tested outside production. |
| `DEPLOYED_UNVERIFIED` | Deployment is believed to exist, but current runtime proof is absent or stale. |
| `DONE_VERIFIED` | Code, deployment, runtime health, and smallest real workflow have all passed current evidence gates. |
| `BLOCKED` | Progress requires a missing permission, credential, provider action, or unresolved fault. |
| `WAIVED` | Explicitly excluded by an authorised owner decision. |

A narrow proof must never be expanded into a broader completion claim.

## 3. System purpose

The hub is the runtime and evidence boundary for the XRP/HBAR Apex Intelligence OS. Its intended responsibilities are:

1. provide a stable API and operational health surface;
2. persist source and evidence records;
3. accept copied links, transcript text, OCR text, and newsletter evidence;
4. expose retrieval and proof routes;
5. support bounded Gmail read-only metadata intake;
6. create claim candidates without presenting them as verified facts;
7. maintain checkpoints for recurring jobs, retries, deduplication, and backfill;
8. export structured evidence-pack state;
9. federate governed capability and health state into a wider Jarvis system;
10. preserve security, approval, audit, rollback, and proof boundaries.

## 4. Current architecture

### 4.1 Runtime topology

| Service | Technology | Current role | Stage |
|---|---|---|---|
| Reverse proxy | Caddy 2 Alpine | Exposes ports 80/443 and proxies API traffic | Implemented; current live reachability unverified |
| API | Flask/Python | Health, evidence, Gmail, VTI, checkpoint and export routes | Implemented in repository |
| Database | PostgreSQL 16 | Persists proof records, checkpoints, claims and exports | Implemented; historical deployment proven |
| Cache/queue substrate | Redis 7 | Readiness dependency and future job coordination substrate | Implemented; no real queue worker proven |
| Worker | Python placeholder loop | Keeps worker service topology present | Scaffold only |
| Deployment automation | GitHub Actions + SSH | Resets target host to `main`, imports bounded runtime env, runs self-heal and proof gates | Implemented; historical success proven |
| Federation adapter | Python contract module | Emits governed Jarvis-compatible service state | Implemented, not bound to Flask runtime |

### 4.2 Deployment chain

`GITHUB MAIN -> DIGITALOCEAN AUTO DEPLOY WORKFLOW -> SSH -> /opt/xrp-hbar-apex -> HOST SELF-HEAL -> DOCKER COMPOSE -> CADDY/API/POSTGRES/REDIS/WORKER -> PUBLIC PROOF GATES`

The repair droplet `170.64.230.87` is excluded from normal execution and must remain untouched unless separately approved.

## 5. Implemented API surface

### 5.1 Core operational routes

| Method | Route | Purpose | Stage |
|---|---|---|---|
| GET | `/health` | Process-level service health | Implemented; historically proven |
| GET | `/ready` | PostgreSQL and Redis readiness | Implemented; historically proven |
| GET | `/deployment/status` | Runtime version, environment, stack and framework-layer summary | Implemented; historically proven for earlier version |

### 5.2 Gmail/newsletter routes

| Method | Route | Purpose | Stage |
|---|---|---|---|
| GET | `/email/newsletter/gmail/status` | Validates env presence and attempts OAuth token refresh | Implemented; blocked by credential validity/current runtime availability |
| POST | `/email/newsletter/gmail/fetch` | Bounded Gmail metadata-only fetch and proof persistence | Implemented; not currently end-to-end proven |
| GET | `/email/newsletter/gmail/proof/latest` | Retrieve latest Gmail proof | Implemented |
| GET | `/email/newsletter/gmail/proof/<proof_id>` | Retrieve Gmail proof by ID | Implemented |
| GET | `/email/newsletter/status` | Newsletter subsystem capability statement | Implemented |
| POST | `/email/newsletter/smoke` | Manual newsletter proof persistence | Implemented |
| GET | `/email/newsletter/proof/latest` | Latest manual newsletter proof | Implemented |
| GET | `/email/newsletter/proof/<proof_id>` | Manual newsletter proof by ID | Implemented |
| GET | `/email/newsletter/proof` | List persisted newsletter proofs | Implemented |
| GET | `/email/newsletter/sync/status` | Recurring sync scaffold status | Scaffolded |
| POST | `/email/newsletter/sync/checkpoint` | Persist a manual sync checkpoint | Scaffolded and persistence-backed |
| GET | `/email/newsletter/claims/status` | Claim extraction scaffold status | Scaffolded |
| POST | `/email/newsletter/claims/extract` | Naive sentence-split claim candidate persistence | Scaffolded; not fact verification |

### 5.3 VTI routes

| Method | Route | Purpose | Stage |
|---|---|---|---|
| GET | `/vti/status` | VTI intake and worker capability state | Implemented |
| POST | `/vti/smoke` | Persist copied URL plus supplied transcript/OCR evidence | Implemented and historically proven |
| GET | `/vti/evidence/<source_id>` | Retrieve one VTI evidence record | Implemented |
| GET | `/vti/evidence/latest` | Retrieve latest VTI evidence record | Implemented |
| GET | `/vti/evidence` | List VTI evidence records | Implemented |
| GET | `/vti/worker/status` | External media/caption/OCR worker status | Scaffolded |
| POST | `/vti/worker/checkpoint` | Persist worker-stage checkpoint | Scaffolded and persistence-backed |

### 5.4 Evidence and operations routes

| Method | Route | Purpose | Stage |
|---|---|---|---|
| GET | `/evidence-pack/status` | Evidence-pack export capability state | Implemented |
| GET | `/evidence-pack/latest` | Build and persist a latest-state JSON evidence pack | Scaffolded export; no downloadable file |
| GET | `/ops/dedupe-retry-backfill/status` | Operational checkpoint capability state | Scaffolded |
| POST | `/ops/dedupe-retry-backfill/checkpoint` | Persist dedupe/retry/backfill checkpoint | Scaffolded and persistence-backed |

## 6. Persistence model

The API creates and uses these PostgreSQL tables:

| Table | Purpose |
|---|---|
| `vti_smoke_evidence` | Copied-link, transcript and OCR evidence records |
| `email_newsletter_proof` | Manual newsletter evidence |
| `gmail_fetch_proof` | Sanitised Gmail metadata fetch proofs |
| `phase_checkpoint` | Sync, worker, dedupe, retry and backfill checkpoints |
| `claim_candidate` | Unverified claim candidates |
| `evidence_pack_export` | Generated evidence-pack JSON state |

### Data-governance rules

- secret values must never be persisted in these tables;
- Gmail message IDs, thread IDs, history IDs, domains, subjects and snippets are hashed or preview-limited;
- message bodies and attachments are not read by the bounded Gmail proof route;
- a claim candidate is not a verified claim;
- every record must carry a proof label, evidence object, limits object, and timestamps;
- future migrations require explicit backup and rollback gates.

## 7. Gmail OAuth boundary

### Required runtime secrets

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`

Required scope:

`https://www.googleapis.com/auth/gmail.readonly`

### Secret-placement policy

Secrets belong only in an approved GitHub Actions secret path, host runtime secret file, or managed vault. They must never be placed in chat, commits, issues, logs, documentation, `.env.example`, or application responses.

### Current blocker

The repository documents an `invalid_grant` recovery path. This means the env names may be populated while the refresh token or OAuth client pairing is invalid, revoked, expired, or generated for another client. The smallest valid fix is to replace the refresh token first; if it belongs to a different OAuth client, replace the client ID, client secret, and refresh token as one matched set.

### Completion gates

Gmail becomes `DONE_VERIFIED` only when all of the following pass in one current deployment:

1. `/email/newsletter/gmail/status` returns token-refresh success;
2. required scope is present or Google omits the scope field without error;
3. bounded metadata fetch succeeds for at most 10 messages;
4. no body, attachment, full address or credential value is exposed;
5. a `gmail_fetch_proof` record is persisted;
6. the persisted proof is retrievable through both ID and latest routes;
7. logs contain no secret values;
8. the proof is attached to the deployed commit SHA and workflow run.

## 8. VTI framework

### Implemented intake

The VTI smoke path currently supports:

- validated HTTP/HTTPS source URL;
- source domain and platform capture;
- optional title;
- supplied transcript text;
- supplied OCR text;
- SHA-256 evidence hashes;
- word counts;
- deterministic source ID;
- PostgreSQL persistence;
- evidence retrieval and listing.

### Not yet implemented

The following remain outside the completed stage:

- automatic external media download;
- official transcript/caption retrieval;
- platform-specific adapters;
- frame extraction;
- automatic OCR execution;
- diarisation;
- language detection and translation;
- claim-to-timestamp alignment;
- source authenticity checks;
- research verification;
- scheduled ingestion;
- retry worker and dead-letter queue;
- rights/terms-aware source handling.

### Next VTI implementation standard

A real VTI worker must:

1. accept a source job through a durable queue;
2. apply URL allow/deny and SSRF protections;
3. identify platform and lawful acquisition method;
4. fetch official captions first where available;
5. accept uploaded transcript/OCR files as a fallback;
6. avoid unauthorised bypass of authentication or access controls;
7. persist source provenance, acquisition method and timestamps;
8. execute OCR only on approved frames/files;
9. deduplicate by source fingerprint;
10. emit structured evidence with exact limitations;
11. retry transient failures with a capped budget;
12. send terminal failures to a dead-letter state;
13. expose job and evidence retrieval routes;
14. pass current end-to-end proof on a non-sensitive source.

## 9. Newsletter and claim-intelligence framework

### Current stage

Manual newsletter persistence, Gmail metadata proof code, sync checkpoints and naive claim candidate extraction are implemented or scaffolded. No recurring scheduler, production queue consumer, full-body extraction, semantic claim extraction, citation validation, or external fact verification is proven.

### Target flow

`SOURCE INTAKE -> SANITISATION -> DEDUPE -> PERSISTENCE -> CLAIM CANDIDATE EXTRACTION -> SOURCE LINKAGE -> VERIFICATION QUEUE -> EVIDENCE PACK -> HUMAN/AGENT DECISION`

### Verification rule

No extracted sentence may alter an XRP/HBAR likelihood, forecast, alert, score, or recommendation unless it has:

- a stable source reference;
- publication/receipt time;
- claim text hash;
- source-quality rating;
- corroboration or contradiction search;
- proof tier;
- explicit uncertainty;
- reviewer or governed automation decision.

## 10. Jarvis federation contract

The repository contains a self-contained contract adapter with:

- contract version `1.0.0`;
- service ID `xrp-hbar-hub-runtime`;
- governed status enum;
- required-route health checks;
- capability declarations;
- deployment metadata;
- blocker list;
- evidence references;
- validation tests;
- PR-only CI;
- secret-file absence checks.

### Current limitation

The adapter is not registered as a Flask route and does not probe the live runtime. It remains `IMPLEMENTED_NOT_INTEGRATED`.

### Integration target

Add a read-only route such as `/federation/contract` that:

1. binds the canonical adapter to the API;
2. reports the exact deployed commit SHA;
3. derives route status from current internal checks rather than static assumptions;
4. reports `partial` unless every required route passes;
5. excludes all secret names that could reveal secret structure unnecessarily;
6. remains read-only and unauthenticated only if its output is safe for public disclosure;
7. is included in staging and production proof gates.

## 11. Deployment and operations controls

### Existing controls

- main-branch deployment target is pinned;
- deployment concurrency does not cancel an active production run;
- deploy files are validated before SSH execution;
- SSH key material is normalised and validated;
- secrets are imported without committing `.env.production`;
- target repo is hard-reset to canonical `main`;
- host self-heal runs before public proof gates;
- core routes and subsystem routes are tested independently;
- first-failing-gate reporting is used;
- markdown-only changes do not trigger runtime deployment.

### Required hardening before production-complete status

- current public endpoint reachability restoration;
- HTTPS/domain proof rather than permanent raw-IP HTTP dependence;
- non-root deployment user or a documented root-risk acceptance;
- firewall and DigitalOcean network rule verification;
- database backup and restore proof;
- migration framework and rollback command;
- real worker implementation with bounded concurrency;
- structured logs and retention;
- uptime and error-rate monitoring;
- disk, memory, CPU and database capacity alerts;
- Redis persistence/eviction policy review;
- secret rotation procedure;
- incident-stop conditions;
- dependency vulnerability scanning;
- branch protection and required checks;
- staging environment separated from production;
- disaster-recovery runbook;
- cost guardrails.

## 12. Verification matrix

| Proof layer | Current result | Evidence quality |
|---|---|---|
| Repository exists and is accessible | Proven | Current connector evidence |
| Canonical branch is `main` | Proven | Current repository metadata |
| Deployment workflow exists | Proven | Current repository file |
| Core API code exists | Proven | Current repository file |
| Persistence routes exist | Proven | Current repository file |
| Federation adapter exists | Proven | Current commit evidence |
| Historical SSH deployment | Proven for earlier commit | Historical workflow ledger |
| Historical public core routes | Proven for earlier commit | Historical workflow ledger |
| Historical VTI copied-link smoke | Proven for earlier commit | Historical workflow ledger |
| Current public IP reachability | Not proven; connection refused/unavailable from current environment | Current independent check |
| Current main commit deployed | Not proven | Missing current successful run evidence |
| Current container health | Not proven | Requires host or workflow evidence |
| Gmail token refresh | Blocked/unproven | Requires valid matched OAuth secrets |
| Gmail bounded metadata proof | Unproven | Depends on token refresh and runtime |
| Recurring newsletter ingestion | Not implemented | Scaffold only |
| Full VTI worker | Not implemented | Scaffold only |
| Jarvis federation live integration | Not implemented | Adapter only |
| Full XRP/HBAR intelligence engine | Not implemented in this hub stage | Backlog/domain layer outside current proof |

## 13. Exact remaining task sequence

### Gate A — restore and prove runtime availability

1. inspect the latest GitHub Actions production run;
2. identify whether failure is SSH, host power/network, Caddy, Docker, firewall, application health or stale deployment;
3. rerun only failed jobs when safe;
4. verify host sync to the intended commit;
5. verify container status and logs;
6. pass `/health`, `/ready`, `/deployment/status`, `/vti/status`, `/email/newsletter/status`, and `/evidence-pack/status`;
7. record workflow run, job, commit and route evidence.

### Gate B — integrate and prove federation contract

1. bind the adapter to a read-only route;
2. add unit tests;
3. add route to deployment proof gates;
4. deploy through branch/PR/main workflow;
5. verify live contract and exact commit.

### Gate C — resolve Gmail credential proof

1. create or confirm Google OAuth desktop/web client as appropriate;
2. generate a refresh token with `gmail.readonly` scope;
3. store the matched secret set in the approved secret store;
4. redeploy without exposing values;
5. pass status, bounded fetch, persistence and retrieval gates.

### Gate D — implement recurring ingestion worker

1. replace placeholder worker with a queue consumer;
2. add scheduler or externally triggered bounded job;
3. implement idempotency and checkpoint resume;
4. add retry cap, dead-letter handling and incident-stop controls;
5. prove one recurring cycle without duplicate records.

### Gate E — implement real VTI worker

1. add source-job schema and queue;
2. implement lawful caption/upload intake first;
3. add optional frame/OCR pipeline;
4. persist provenance and evidence;
5. prove one complete job and retrieval path.

### Gate F — production hardening

1. TLS/domain;
2. backups and restore test;
3. monitoring and alerts;
4. branch protection;
5. staging separation;
6. security and dependency review;
7. rollback drill;
8. cost guardrails.

## 14. Approval gates

Explicit owner approval is required before:

- merging code that triggers production deployment;
- changing GitHub Actions secrets;
- changing DigitalOcean firewall, DNS, domain or droplet configuration;
- handling OAuth client credentials or refresh tokens;
- modifying production database schema or data;
- enabling recurring external ingestion;
- adding paid providers;
- enabling live trading, custody, transaction signing or money movement;
- destructive cleanup or repair-droplet use.

## 15. Completion definition for this stage

This documentation stage is complete when:

- the repository and current implementation have been inspected;
- historical proof is separated from current proof;
- the current runtime reachability problem is recorded without overclaiming;
- implemented, scaffolded, blocked and future functions are mapped;
- the architecture, API, data, security, deployment and verification framework is documented;
- exact next gates are ordered;
- no production secrets are exposed;
- no production deployment is triggered by this documentation-only branch.

This stage does **not** mean the full XRP/HBAR Apex Intelligence OS is production-complete. It means the current repository stage has been fully specified and truthfully bounded.

## 16. Proof labels for this stage

`REPO_TRUTH_INSPECTED`  
`CURRENT_IMPLEMENTATION_MAPPED`  
`HISTORICAL_DEPLOYMENT_PROOF_PRESERVED`  
`CURRENT_RUNTIME_REACHABILITY_UNVERIFIED`  
`GMAIL_EXTERNAL_CREDENTIAL_BLOCKER_CLASSIFIED`  
`VTI_SCAFFOLD_BOUNDARY_RECORDED`  
`NEWSLETTER_SCAFFOLD_BOUNDARY_RECORDED`  
`FEDERATION_ADAPTER_IMPLEMENTED_NOT_INTEGRATED`  
`PRODUCTION_CHANGE_NOT_TRIGGERED`  
`FULL_STAGE_SPECIFICATION_CREATED`  
`NEXT_GATES_ORDERED`  
`ZERO_SECRET_EXPOSURE`  

## 17. Current final status

**Best-supported status:** `DEPLOYED_UNVERIFIED / IMPLEMENTED_PARTIAL`  
**First exact blocker:** current production endpoint is not independently reachable from the present environment.  
**Second exact blocker:** valid matched Gmail OAuth credentials are not proven.  
**Next production action:** inspect and repair the latest deployment/runtime proof chain, then verify the current commit before enabling additional automation.
