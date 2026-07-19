# Start.me and API Source Discovery Framework

Date: 2026-07-19
Status: SPECIFICATION_READY / IMPLEMENTATION_BACKLOGGED
Owner: XRP/HBAR Apex Runtime Hub / Jarvis SourceScout

## 1. Purpose

Add a governed discovery layer that uses public Start.me pages, user-authorised Start.me exports, official API directories, MCP registries, package registries, public repositories, standards catalogues, vendor documentation, changelogs, research indexes and curated expert sources to discover useful APIs, datasets, tools, feeds, endpoints and integration opportunities for Jarvis.

This layer is discovery-first. It must never treat a bookmark, directory listing, community page or Start.me page as proof that an API is safe, current, lawful, useful or production-ready.

## 2. Core rule

`DISCOVER -> NORMALISE -> VERIFY_OFFICIAL_SOURCE -> SCORE -> QUARANTINE -> SANDBOX_TEST -> SECURITY_REVIEW -> COST_REVIEW -> APPROVAL -> CANARY -> MONITOR -> PROMOTE_OR_ROLLBACK`

No discovered endpoint may be called with production credentials, private data, signing authority, trading authority, payment authority or privileged scopes before the approval and verification gates pass.

## 3. Start.me role

Start.me is classified as a source-curation and navigation surface.

Allowed uses:
- ingest public Start.me page URLs;
- ingest user-exported bookmarks or OPML files;
- extract bookmark titles, descriptions, categories, tags, feed URLs and destination URLs;
- track page changes when lawfully accessible;
- use Start.me collections to seed topic-specific source maps;
- use Start.me as an analyst dashboard for approved links, alerts and source categories;
- maintain separate pages for official sources, candidate APIs, research, security, deployment, crypto, finance and other Jarvis modules.

Disallowed assumptions:
- a Start.me link is not an endorsement;
- a bookmark is not proof of ownership, reliability or permission;
- a public page is not permission to crawl linked private systems;
- Start.me must not store secrets, API keys, OAuth tokens, seed phrases or production credentials;
- authenticated/private pages must not be scraped without explicit user authorisation and a supported export or connector path.

## 4. Source classes

### Tier A: canonical
- official API documentation;
- official OpenAPI, AsyncAPI, GraphQL or MCP specifications;
- official repositories and release notes;
- regulator and government sources;
- standards bodies;
- official status pages and pricing pages.

### Tier B: strong secondary
- recognised package registries;
- reputable engineering publications;
- peer-reviewed research;
- established security databases;
- maintained public reference implementations.

### Tier C: discovery-only
- Start.me pages;
- curated bookmark collections;
- community API lists;
- newsletters;
- social posts;
- forum threads;
- influencer recommendations;
- aggregator directories.

Tier C findings must be independently verified through Tier A evidence before integration.

## 5. Discovery adapters

Jarvis should support pluggable read-only discovery adapters for:

- Start.me public pages;
- Netscape bookmark HTML exports;
- OPML feed exports;
- RSS and Atom feeds;
- OpenAPI and AsyncAPI indexes;
- MCP registries;
- GitHub repositories, topics, releases and issues;
- npm, PyPI, crates.io, Maven and container registries;
- public API catalogues;
- government data portals;
- academic search providers;
- CVE, OSV and vendor security advisories;
- cloud marketplaces and official integration directories;
- vendor changelogs and deprecation feeds;
- model and dataset hubs;
- blockchain explorers and official chain developer portals;
- official XRP, Ripple, Hedera and HBAR developer sources.

Each adapter must emit a common CandidateSource record.

## 6. CandidateSource schema

Required fields:
- candidate_id;
- discovered_url;
- resolved_url;
- title;
- description;
- source_class;
- discovery_origin;
- discovered_at;
- topic tags;
- proposed Jarvis module;
- API or resource type;
- official-source status;
- authentication type;
- requested scopes;
- data sensitivity;
- write capability;
- financial or trading capability;
- pricing and rate limits;
- jurisdiction and terms flags;
- maintenance activity;
- security evidence;
- dependency and licence data;
- score breakdown;
- review status;
- approval status;
- test evidence;
- rollback and revoke instructions.

## 7. Endpoint and API verification

For every candidate, verify where applicable:

1. Domain ownership and official provenance.
2. TLS validity and redirect chain.
3. Documentation freshness.
4. Published authentication method.
5. Required scopes and least-privilege option.
6. Read versus write authority.
7. Rate limits, quotas and commercial terms.
8. Data-retention and privacy terms.
9. Jurisdiction and regulatory exposure.
10. SDK and specification availability.
11. Changelog and deprecation policy.
12. Status page and uptime history.
13. Security advisories and known vulnerabilities.
14. Package or container supply-chain risk.
15. Webhook signing and replay protection.
16. Idempotency and retry behaviour.
17. Pagination and backfill support.
18. Sandbox or test environment.
19. Export and account-deletion support.
20. Revocation and rollback procedure.

Unknowns remain GAP records. Unknown must never be interpreted as safe.

## 8. Scoring model

Score each candidate from 0 to 100 using weighted dimensions:

- official provenance: 15;
- security posture: 15;
- least-privilege compatibility: 10;
- functionality and Jarvis fit: 15;
- data quality: 10;
- reliability and maintenance: 10;
- cost efficiency: 10;
- interoperability and open standards: 5;
- observability and auditability: 5;
- reversibility and vendor-lock-in risk: 5.

Hard-fail conditions override the numeric score:
- malware or credential theft indicators;
- unverifiable ownership;
- prohibited or unlawful use;
- seed phrase or private-key request;
- mandatory excessive scopes without justification;
- undocumented write or transaction authority;
- inability to revoke access;
- terms incompatible with intended use;
- material unresolved security advisory;
- hidden recurring cost or billing authority.

## 9. Risk classes

- R0: public read-only metadata, no credentials.
- R1: API key, read-only, non-sensitive data.
- R2: OAuth or service account with limited read access.
- R3: write access, webhooks, private data or operational changes.
- R4: financial actions, trading, signing, production infrastructure, health, legal or regulated data.
- R5: destructive, irreversible, custody, seed phrase, private key or broad administrative authority.

R0-R1 may progress through automated sandbox checks. R2 requires credential-owner approval. R3-R5 require explicit scoped approval, independent verification, rollback proof and production release controls. R5 should normally be denied or redesigned to remove the authority.

## 10. Safe integration factory

For approved candidates, generate:
- integration manifest;
- adapter interface;
- `.env.example` names only;
- secret-placement map;
- least-privilege scope list;
- sandbox test suite;
- mock fixtures;
- timeout and retry policy;
- rate-limit controls;
- circuit breaker;
- schema validation;
- webhook verification;
- idempotency keys;
- audit events;
- health and readiness checks;
- cost and usage guardrails;
- data-retention policy;
- revoke and rollback runbook;
- PR-ready implementation;
- evidence record.

No real secret values are written to the repository, issues, logs or chat.

## 11. Jarvis placement

### SourceScout
Discovers and classifies Start.me links and other source candidates.

### Source Registry
Stores canonical source records, provenance, freshness and ownership evidence.

### Integration Registry
Tracks candidate, sandboxed, approved, active, deprecated and revoked integrations.

### Security Council
Reviews scopes, supply-chain risk, data sensitivity, secrets and write authority.

### Cost Router
Compares free/local, cheapest suitable paid and premium alternatives.

### Integration Factory
Creates adapters, tests, manifests and deployment artifacts.

### Evidence and Verification Layer
Stores test outputs, official-source citations, decisions, waivers and runtime proof.

### Command Centre
Shows traffic-light state, capability gain, cost, risk, owner, approval and next action.

## 12. Start.me dashboard design

Recommended pages:
- Jarvis Official Sources;
- APIs and MCP Candidates;
- AI Models and Tooling;
- Security and CVEs;
- GitHub and Open Source;
- Deployment and Infrastructure;
- XRP, Ripple, HBAR and Hedera;
- Finance, Macro and Regulation;
- Video, Social and Newsletter Intelligence;
- Research Papers and Standards;
- Free Tiers, Grants and Cost Opportunities;
- Deprecated, Rejected and High-Risk Sources.

Start.me remains a human-readable navigation dashboard. The canonical machine truth remains in GitHub-backed registries and the Jarvis database.

## 13. API discovery workflow

1. Import public page or authorised export.
2. Hash and preserve raw import.
3. Extract and normalise links.
4. Deduplicate redirects and mirrors.
5. Classify topic and proposed module.
6. Identify likely official source.
7. Resolve official documentation.
8. Search for specifications, SDKs, pricing, status and security evidence.
9. Create CandidateSource.
10. Score and risk-classify.
11. Reject, quarantine or sandbox.
12. Generate integration proposal.
13. Run mock and sandbox tests.
14. Conduct security and cost review.
15. Request the smallest necessary approval.
16. Canary release.
17. Monitor errors, spend, scope and data use.
18. Promote, suspend or rollback.
19. Recheck on changelog, CVE, price, terms or deprecation events.

## 14. Continuous intelligence

Scheduled scans may detect:
- new APIs and MCP servers;
- new official SDKs;
- price or free-tier changes;
- deprecations;
- breaking schema changes;
- security advisories;
- licence changes;
- new rate limits;
- ownership or domain changes;
- superior lower-cost alternatives;
- duplicated integrations;
- unused credentials;
- abandoned dependencies.

A detected change creates a delta record. It does not silently modify production.

## 15. Missing capabilities added by this framework

- endpoint ownership verification;
- API specification ingestion;
- source confidence and freshness scoring;
- Start.me import and export handling;
- API/MCP candidate quarantine;
- least-privilege scope analyser;
- terms, jurisdiction and privacy review;
- supply-chain and CVE scanning;
- cost and rate-limit forecasting;
- duplicate integration detection;
- sandbox contract testing;
- webhook and replay-security checks;
- provider kill switch;
- credential rotation and revoke evidence;
- deprecation and breaking-change monitoring;
- capability-gap matching;
- integration ROI scoring;
- provenance-linked recommendation records;
- human-readable Start.me dashboards backed by canonical registries.

## 16. Acceptance criteria

This module is not complete until:
- importers exist for public Start.me pages and user-provided HTML/OPML exports;
- CandidateSource schema is implemented;
- official-source verification is enforced;
- scoring and hard-fail rules are tested;
- no candidate can directly execute in production;
- sandbox and approval state transitions are enforced;
- secrets are excluded from persistence and logs;
- at least one low-risk API candidate completes sandbox verification;
- at least one unsafe candidate is correctly rejected;
- registries and Command Centre status are updated;
- rollback and revoke paths are tested;
- end-to-end evidence is stored.

## 17. Governed statuses

`DISCOVERED`, `NORMALISED`, `OFFICIAL_SOURCE_UNVERIFIED`, `VERIFIED_CANDIDATE`, `QUARANTINED`, `REJECTED`, `SANDBOX_READY`, `SANDBOX_PROVEN`, `SECURITY_REVIEW_REQUIRED`, `COST_REVIEW_REQUIRED`, `APPROVAL_REQUIRED`, `CANARY`, `ACTIVE_VERIFIED`, `SUSPENDED`, `DEPRECATED`, `REVOKED`.

## 18. Immediate implementation backlog

P0:
- CandidateSource JSON schema;
- bookmark HTML and OPML parsers;
- Start.me public-page importer with robots and rate-limit compliance;
- URL normalisation and dedupe;
- official-domain resolver;
- risk and scoring engine;
- registry persistence;
- dry-run API probe framework;
- tests proving no secret ingestion or production execution.

P1:
- OpenAPI/AsyncAPI ingestion;
- MCP registry adapter;
- GitHub and package-registry enrichment;
- CVE and licence checks;
- cost and rate-limit model;
- Command Centre cards;
- changelog and deprecation watcher.

P2:
- sandbox adapter generation;
- automated mock creation;
- canary integration controller;
- continuous alternative-provider comparison;
- Start.me dashboard export/update helper.

## 19. Proof boundary

This document defines the framework and implementation contract. It does not prove that Start.me ingestion, API discovery, sandbox adapters or production integrations are live. Runtime completion requires code, tests, deployment evidence and verified operation.