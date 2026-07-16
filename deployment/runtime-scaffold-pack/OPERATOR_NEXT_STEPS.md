# XRP/HBAR Apex Deployment Operator Next Steps

Current blocker: public routes return `403 Domain forbidden` from `envoy`, so the app is not proven live through the public edge.

Use this runbook after checking the GitHub Actions run for the latest trigger commit.

## Decision Tree

### 1. If GitHub Actions did not run

- Enable GitHub Actions for `rafsof22-lgtm/hub`.
- Manually run `DigitalOcean Auto Deploy` from the Actions tab.
- Recheck public routes.

### 2. If GitHub Actions failed at SSH

Add or replace this repository secret:

- `DIGITALOCEAN_SSH_KEY`

The value must be the full private SSH key block for root access to the intended droplet. Do not store it in chat, docs, or repo files.

Then rerun the workflow.

### 3. If GitHub Actions reached the host but failed env validation

SSH or console into the intended droplet and create:

```bash
/opt/xrp-hbar-apex/deployment/runtime-scaffold-pack/.env.production
```

Required non-placeholder values:

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`

Runtime OAuth/API values can be added later, but Gmail runtime proof needs:

- `GMAIL_OAUTH_CLIENT_ID`
- `GMAIL_OAUTH_CLIENT_SECRET`
- `GMAIL_OAUTH_REFRESH_TOKEN`

### 4. If the host is reachable but public routes still show envoy/domain errors

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

Only call the runtime deployed after these return app JSON externally:

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

returns token-refresh-proven readiness, and a bounded read-only fetch succeeds.

## Current Status Labels

- `REPO_SCAFFOLD_PRESENT`
- `HOST_SELF_HEAL_SCRIPT_ADDED`
- `PUBLIC_ROUTE_BLOCKED`
- `GITHUB_ACTIONS_RUN_STATUS_NEEDS_UI_CHECK`
- `SECRET_OWNER_ACTION_REQUIRED`
- `PRODUCTION_NOT_PROVEN`

## Do Not Claim Yet

Do not claim any of these until route-level proof exists:

- production deployment complete
- auto-deploy proven
- saved-video access proven
- private Facebook/Instagram/X/YouTube access proven
- Gmail autopilot production-ready
- VTI end-to-end transcription automation ready
