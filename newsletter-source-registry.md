# Newsletter Source Registry

Last updated: 2026-07-16

Proof labels: `GMAIL_ACCESS_PROVEN`, `READ_ONLY_SAMPLE_COMPLETED`, `SANITIZED_PROVENANCE_ONLY`, `NO_SECRET_CONTENT_STORED`, `MAILBOX_WRITE_LIMITED_TO_REVIEW_LABEL`.

## Scope

This registry records source candidates discovered through the connected Gmail newsletter/intelligence pass for the XRP/HBAR Apex Intelligence OS. It stores only sanitized metadata, not full email bodies, private links, reset tokens, passwords, or credentials.

Search query used:

```text
newer_than:14d -in:spam -in:trash (xrp OR hbar OR ripple OR hedera OR crypto OR tokenization OR ETF OR macro OR newsletter)
```

Sample size: 5 messages read from 10 matching IDs.

## Gmail Inventory Snapshot

| label | total messages | unread messages | notes |
|---|---:|---:|---|
| INBOX | 1389 | 1315 | live Gmail label count returned |
| UNREAD | 1315 | 1315 | live Gmail label count returned |
| CATEGORY_PROMOTIONS | 318 | 316 | high newsletter density |
| CATEGORY_UPDATES | 673 | 616 | high alert/update density |

## Source Candidates

| source | sender | sample subject | category | relevance | action |
|---|---|---|---|---|---|
| DigitalOcean Support | support@digitalocean.com | Droplet password reset notice for Digital-ocean-XRP-Hbar-Apex | deployment/security | critical operational signal | labeled `XRP-HBAR Apex/Deployment Review`; keep unread/in inbox for owner review |
| Lona | hello@lona.agency | Welcome to Lona - build your first trading strategy | trading/backtesting tool | medium; possible paper-strategy/backtest source candidate | track as tool candidate, do not treat marketing claims as proven |
| The Rundown AI | news@daily.therundown.ai | AI jobs/regulation/newsletter issue | AI/macro/source scouting | medium; useful for AI infrastructure and regulation watchlist, not XRP/HBAR-specific proof | retain as broad intelligence source candidate |
| Metricool | info@metricool.com | Social media account onboarding | social intelligence tooling | low-to-medium; possible social scheduling/analytics tool, not current core proof | track as connector/tool candidate only |

## Review Rules

- Do not archive, delete, forward, or mark resolved any security/deployment message without explicit owner approval.
- Do not store one-time codes, reset passwords, private links, or credentials in repo files.
- Treat newsletter claims as unverified until checked against primary sources.
- Treat tool marketing claims as source candidates, not recommendations.

## Current Status

Gmail live access is proven. Email/newsletter live-ingestion is partially proven at the read/search/classify/label stage, but not yet fully proven as an automated durable pipeline because this pass did not run a scheduled ingestion job or write to a production knowledge database.
