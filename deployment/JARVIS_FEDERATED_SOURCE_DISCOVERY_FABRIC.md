# Jarvis Federated Source Discovery Fabric

Status: `SPECIFICATION_COMPLETE_IMPLEMENTATION_PENDING`
Updated: 2026-07-19

## Objective

Create a continuously extensible, governed discovery layer that finds APIs, MCP servers, feeds, datasets, SDKs, models, tools, research sources, security intelligence and lower-cost infrastructure without allowing a directory, bookmark page or community list to become trusted production authority.

## Core architecture

`DISCOVER -> NORMALISE -> DEDUPLICATE -> RESOLVE_OFFICIAL_SOURCE -> VERIFY_OWNERSHIP -> SCORE -> QUARANTINE -> SANDBOX -> APPROVAL -> CANARY -> PROMOTE_OR_REJECT -> MONITOR`

## Source hierarchy

### Tier 0: canonical machine-readable registries

1. Official MCP Registry and its REST API.
2. Google APIs Discovery Service.
3. Provider-owned OpenAPI, AsyncAPI, GraphQL introspection and SDK manifests.
4. Official cloud, model, blockchain, government and regulator catalogs.
5. Official package registries and signed release channels.

### Tier 1: structured API networks and catalogs

1. APIs.guru OpenAPI Directory.
2. Postman API Network and verified publisher workspaces.
3. GitHub repositories containing official specifications, releases and security advisories.
4. Hugging Face model and dataset metadata.
5. Government open-data portals and standards catalogs.

Tier 1 discovers candidates. Official provider evidence is still required before production integration.

### Tier 2: curated dashboards and knowledge collections

1. Start.me public pages and authorised exports.
2. Raindrop.io collections and API-authorised bookmark libraries.
3. Linkwarden, Karakeep/Hoarder, Wallabag and browser bookmark exports.
4. OPML, RSS and Atom collections.
5. Internal Jarvis source dashboards.

These sources provide categorisation and human curation but have no execution authority.

### Tier 3: community discovery surfaces

1. Awesome lists.
2. Public API lists.
3. MCP community catalogs.
4. Newsletters, forums, Reddit, Discord, Telegram and social posts.
5. Conference lists, tutorials and blog roundups.

Tier 3 is discovery-only and must be independently verified.

## Source adapters

| Adapter | Input | Output | Default trust |
|---|---|---|---|
| MCP Registry adapter | Registry API/server.json | MCP candidate records | Structured candidate |
| OpenAPI directory adapter | APIs.guru list and definitions | API candidates + schemas | Structured candidate |
| Postman adapter | Public workspaces/collections | Requests, schemas, examples | Candidate |
| Google Discovery adapter | APIs Directory + discovery docs | Google API methods/scopes | Canonical for Google |
| GitHub source adapter | Repositories/releases/advisories | Ownership, activity, releases, CVEs | Conditional |
| Start.me adapter | Public page or authorised export | Bookmarks, groups, feeds | Discovery only |
| Bookmark adapter | HTML/CSV/JSON | Normalised links and tags | Discovery only |
| OPML adapter | OPML | Feed candidates | Discovery only |
| RSS/Atom adapter | Feed URL | Update stream and source metadata | Conditional |
| Model-hub adapter | Model/dataset metadata | Model candidates and licences | Conditional |
| Package adapter | npm/PyPI/container metadata | Dependency candidates | Conditional |
| Government-data adapter | Official catalogs | Datasets and APIs | Canonical when official |

## Candidate record contract

Each candidate must store:

- `candidate_id`
- `source_url`
- `discovery_source`
- `discovery_tier`
- `resolved_official_url`
- `provider_identity`
- `resource_type`
- `specification_type`
- `specification_url`
- `authentication_type`
- `requested_scopes`
- `read_write_class`
- `data_classes`
- `jurisdiction`
- `pricing_url`
- `rate_limits`
- `licence`
- `terms_url`
- `privacy_url`
- `status_url`
- `repository_url`
- `latest_release`
- `maintenance_score`
- `security_score`
- `capability_score`
- `cost_score`
- `interoperability_score`
- `reversibility_score`
- `overall_score`
- `risk_class`
- `quarantine_status`
- `decision`
- `decision_reason`
- `sandbox_evidence`
- `approval_reference`
- `rollback_reference`
- `last_verified_at`
- `next_review_at`

## Required verification

1. Resolve redirects and canonical domain.
2. Confirm provider ownership through official documentation, DNS, repository ownership or registry namespace proof.
3. Locate official specification and changelog.
4. Determine authentication method and exact scopes.
5. Classify read, write, financial, destructive and administrative capability.
6. Check TLS, signing, webhook validation, replay protection and token handling.
7. Check pricing, free tier, overages, rate limits, egress and minimum spend.
8. Check licence, terms, privacy, retention and jurisdiction.
9. Check release cadence, maintenance activity, issue backlog and deprecation policy.
10. Check security advisories, dependency risk and supply-chain integrity.
11. Compare duplicate or existing Jarvis capability.
12. Define sandbox, test data, kill switch, rollback and revoke path.

## Risk classes

- `R0_PUBLIC_READ_ONLY`: public data with no credentials.
- `R1_SCOPED_READ_KEY`: read-only API key.
- `R2_OAUTH_OR_SERVICE_READ`: private read access.
- `R3_WRITE_OR_WEBHOOK`: write actions, webhooks or private data processing.
- `R4_HIGH_IMPACT`: finance, trading, health, legal, identity or infrastructure control.
- `R5_CUSTODY_OR_DESTRUCTIVE_ADMIN`: private keys, custody, irreversible or administrator-level actions; deny by default.

## MCP-specific controls

The official MCP Registry is the primary discovery source, but registry presence is not an approval. The registry is preview-stage and may change. Jarvis must:

- pin server and package versions;
- validate namespace ownership;
- inspect declared transports and package sources;
- generate an allowlisted tool manifest;
- limit tools exposed to any one model context;
- reject ambiguous or unsafe tool descriptions;
- test prompt-injection and tool-poisoning resistance;
- enforce per-tool identity, scope, timeout and cost budgets;
- block recursive unrestricted server discovery;
- isolate filesystem, shell, browser, credential and network tools;
- keep write-capable MCP tools behind explicit approval;
- maintain independent server health and revoke controls.

## Context and capability budgeting

Jarvis must not expose the entire discovered tool universe to a model. Use a hierarchical router:

`Task classification -> module shortlist -> approved integration shortlist -> minimum required tool set -> execution`

Default limits:

- only relevant approved tools enter a task context;
- prefer fewer than 10 tools for routine workers;
- split broad jobs into specialist agents;
- compact and test tool descriptions;
- track token cost, selection errors and unnecessary calls;
- fail closed when tool identity or capability is uncertain.

## Scoring

| Dimension | Weight |
|---|---:|
| Official provenance | 15 |
| Security | 15 |
| Jarvis capability fit | 15 |
| Data quality | 10 |
| Least privilege | 10 |
| Reliability and maintenance | 10 |
| Total operating cost | 10 |
| Interoperability | 5 |
| Auditability | 5 |
| Reversibility | 5 |

Automatic promotion is prohibited. Scores prioritise review only.

## Integration states

`DISCOVERED -> NORMALISED -> OFFICIAL_SOURCE_RESOLVED -> VERIFIED_CANDIDATE -> QUARANTINED -> SANDBOX_READY -> SANDBOX_PROVEN -> APPROVAL_REQUIRED -> CANARY -> APPROVED_PRODUCTION -> WATCHLIST -> DEPRECATED -> REVOKED`

Rejected candidates remain in the registry to prevent repeated evaluation.

## Best Jarvis placement

- `SourceScout`: broad discovery and source monitoring.
- `Integration Factory`: adapters, schemas, mocks and tests.
- `Security Authority`: scopes, package risk, prompt-injection and secret review.
- `Cost Router`: free/local/cheap/best-value/premium comparison.
- `Evidence Engine`: proof records and provenance.
- `Model Router`: minimum-context tool selection.
- `Command Centre`: traffic-light status, approvals, cost and health.
- `Continuity Ledger`: decisions, rejected options, migrations and rollback.

## Priority source stack

### APIs and schemas

- Official provider documentation and API catalogs
- APIs.guru
- Postman API Network
- Google Discovery Service
- GitHub official repositories
- OpenAPI, AsyncAPI and GraphQL specifications

### MCP and agent tools

- Official MCP Registry
- Provider-owned MCP documentation
- GitHub source and releases
- Package registry metadata
- Security advisories and independent sandbox evidence

### Models and datasets

- Official model-provider catalogs
- Hugging Face Hub
- Papers with Code and peer-reviewed repositories where applicable
- Government and institutional datasets

### Security

- NVD/CVE and vendor advisories
- GitHub Security Advisories
- OSV
- CISA and relevant national cyber authorities
- package and container scanners

### Research and current intelligence

- official changelogs and status feeds
- Crossref, OpenAlex, Semantic Scholar and domain-specific scholarly indexes
- government and regulator feeds
- reputable news feeds used only as secondary evidence

### Human-curated discovery

- Start.me
- Raindrop.io
- authorised bookmarks and OPML
- internal Jarvis dashboards
- curated community lists

## Implementation backlog

1. Add `source_candidate`, `source_verification`, `integration_decision` and `source_watch` tables.
2. Implement HTML bookmark, OPML and RSS/Atom parsers.
3. Implement APIs.guru list/spec adapter.
4. Implement official MCP Registry adapter.
5. Implement Google Discovery adapter.
6. Add canonical URL and ownership resolver.
7. Add schema/specification validator.
8. Add scoring and duplicate-capability engine.
9. Add quarantine and lifecycle state machine.
10. Add sandbox endpoint probe with SSRF protection and strict egress policy.
11. Add MCP manifest analyser and tool-description quality checks.
12. Add package, licence and vulnerability enrichment.
13. Add cost/rate-limit and projected-usage calculator.
14. Add approval tickets, canary controls, revoke and rollback paths.
15. Add read-only status and candidate retrieval routes.
16. Add scheduled refresh only after worker and queue are proven.
17. Integrate approved state into the Jarvis federation contract and Command Centre.

## Completion gate

This layer is complete only when one low-risk source from each canonical adapter is discovered, verified, deduplicated, sandboxed and retrieved through an evidence-backed API; one malicious or unsafe candidate is rejected by policy; refresh, rollback and revocation are tested; and no discovered endpoint can execute without explicit integration approval.
