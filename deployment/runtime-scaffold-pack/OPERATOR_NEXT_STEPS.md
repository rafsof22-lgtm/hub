# XRP/HBAR Apex Deployment Operator Next Steps

Current blocker: Gmail runtime proof is not complete. The last connector-visible deploy proof reached the main host, synced commit `1b451c51e3f85510203370fe56fac1d9673a884c`, started the Docker/Caddy runtime, and returned HTTP 200 for core public scaffold, VTI smoke, newsletter smoke, evidence-pack, and checkpoint routes from the GitHub Actions runner. That run failed at `/email/newsletter/gmail/status` because the live runtime reported the canonical Gmail env vars were not configured.

Deploy-relevant workflow head is `5aaf80900e47ed3f740eab85ea1a24b404f0fc63`, one deploy-relevant commit ahead of the last deployed commit. That workflow change maps supported Gmail/Google GitHub Actions secret aliases into canonical host env names without printing values. Current `main` may also include later docs-only commits; those should not trigger deploy because the workflow ignores Markdown-only path changes. A fresh `DigitalOcean Auto Deploy` workflow run on `main` is required to test the alias-mapping logic.

Use this runbook after checking the latest GitHub Actions run for current `main`.

## Decision Tree

### 1. If the latest workflow did not run on current `main`

Manually run `DigitalOcean Auto Deploy` from the Actions tab, or approve a workflow dispatch through a connected tool that supports dispatch.

Do not rerun an old job if the goal is to test the current workflow file. A rerun of an old job can reuse the old workflow definition and miss the Gmail alias-mapping change.

### 2. If GitHub Actions fails at SSH

Add or replace this repository secret:

- `DIGITALOCEAN_SSH_KEY`

The value must be the full private SSH key block for root access to the intended droplet. Do not store it in chat, docs, or repo files.

Then rerun the workflow.

### 3. If GitHub Actions reaches the host but fails env validation

SSH or console into the intended droplet and create or repair:

```bash
/opt/xrp-hbar-apex/deployment/runtime-scaffold-pack/.env.production
```

Required non-placeholder core values:

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`

Runtime OAuth/API values can be added later, but Gmail runtime proof needs:

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`

The current workflow can also import these from supported GitHub Actions secret aliases if the values already exist under any of the checked alias names:

- `GMAIL_OAUTH_CLIENT_ID`
- `GOOGLE_OAUTH_CLIENT_ID`
- `GOOGLE_CLIENT_ID`
- `GMAIL_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GOOGLE_OAUTH_CLIENT_SECRET`
- `GOOGLE_CLIENT_SECRET`
- `GMAIL_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`
- `GOOGLE_OAUTH_REFRESH_TOKEN`
- `GOOGLE_REFRESH_TOKEN`
- `GMAIL_REFRESH_TOKEN`

### 4. If public routes regress to envoy/domain errors

Run the host self-heal script from a root shell on the intended droplet:

```bash
cd /opt/xrp-hbar-apex/deployment/runtime-scaffold-pack
bash host-self-heal.sh
```

If the repo is not cloned yet:

```bash
git clone --branch main https://github.com/rafsof22-lgtm/hub.git /opt/xrp-hbar-apex
cd /opt/xrp-hbar-apex/deployment/runtime-scaffold-pack
bash host-self-heal.sh
```

The script installs Docker if missing, syncs repo code, checks env values, frees ports 80/443 from old proxy services, runs deploy, and performs local route checks.

## Required Public Proof Gates

Only call the runtime deployed after these return app JSON externally from an allowed network path such as GitHub Actions:

```bash
curl -i $BASE_URL/health
curl -i $BASE_URL/ready
curl -i $BASE_URL/deployment/status
curl -i $BASE_URL/vti/status
curl -i $BASE_URL/email/newsletter/status
curl -i $BASE_URL/evidence-pack/status
```

Only call Gmail runtime ready after:

```bash
curl -i $BASE_URL/email/newsletter/gmail/status
```

returns `ready_for_fetch_token_refresh_proven`, and a bounded read-only fetch succeeds:

```bash
curl -i -X POST "$BASE_URL/email/newsletter/gmail/fetch" \
  -H 'Content-Type: application/json' \
  --data '{"query":"category:primary newer_than:30d","max_results":3}'

curl -i $BASE_URL/email/newsletter/gmail/proof/latest
```

## Current Status Labels

- `CORE_RUNTIME_DEPLOYMENT_PREVIOUSLY_PROVEN_FROM_ACTIONS_RUNNER`
- `VTI_SMOKE_ROUTE_PREVIOUSLY_PROVEN_FROM_ACTIONS_RUNNER`
- `EMAIL_NEWSLETTER_SMOKE_PREVIOUSLY_PROVEN_FROM_ACTIONS_RUNNER`
- `EVIDENCE_PACK_STATUS_PREVIOUSLY_PROVEN_FROM_ACTIONS_RUNNER`
- `GMAIL_RUNTIME_CREDENTIALS_PENDING`
- `WORKFLOW_DISPATCH_REQUIRED_FOR_ALIAS_TEST`
- `PRODUCTION_NOT_FULLY_PROVEN`

## Do Not Claim Yet

Do not claim any of these until route-level proof exists on the current workflow/run:

- Gmail runtime token-refresh proven
- bounded Gmail metadata fetch proven
- Gmail proof persistence proven
- recurring Gmail/newsletter production automation ready
- full production deployment complete
- saved-video access proven
- private Facebook/Instagram/X/YouTube access proven
- VTI end-to-end transcription automation ready
