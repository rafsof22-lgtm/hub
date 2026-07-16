# Runtime Scaffold Pack

This folder contains the deployment scaffold for the XRP/HBAR Apex runtime path.

## Current Target

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Runtime scaffold root: `deployment/runtime-scaffold-pack/`
- Service root: `deployment/runtime-scaffold-pack/services/xrp-hbar-apex/`
- DigitalOcean droplet: `Digital-ocean-XRP-Hbar-Apex`
- Public IPv4: `134.199.144.115`
- Workflow: `.github/workflows/digitalocean-auto-deploy.yml`

## Current Honest Status

The repo-side deployment scaffold and workflow are present, but production is not yet proven live.

Known verified pieces:

- GitHub workflow exists and targets pushes to `main` plus manual dispatch.
- `deploy.sh`, `docker-compose.prod.yml`, `Caddyfile`, `.env.production.example`, and the starter XRP/HBAR Flask service exist in this scaffold.
- The DigitalOcean droplet exists and is active.

Known unproven or blocked pieces:

- GitHub Actions run creation for a fresh `main` push is not yet proven.
- GitHub deploy secrets/variables are not yet proven.
- SSH host bootstrap state is not yet proven.
- Host-side `.env.production` with real values is not yet proven.
- Public endpoint probes to `http://134.199.144.115/health`, `/ready`, and `/deployment/status` returned `403 Forbidden` / `Domain forbidden` on 2026-07-16, so live public health is not proven.
- VTI/media runtime execution is not yet proven.

## Required Secrets And Values

Use GitHub Actions secrets or repository variables for deploy-time connection values. Do not commit secrets.

Required deploy values:

- `DIGITALOCEAN_SSH_KEY`: full private SSH key block for the droplet deploy user
- `DIGITALOCEAN_HOST`: `134.199.144.115`
- `DIGITALOCEAN_USER`: normally `root` for first bootstrap
- `DIGITALOCEAN_PORT`: normally `22`
- `APP_DIR`: `/opt/xrp-hbar-apex`
- `BASE_URL`: the exact public base URL used for endpoint checks

Host-side `.env.production` must contain real runtime values, including:

- `DOMAIN`
- `BASE_URL`
- `JOB_SIGNING_SECRET`
- `POSTGRES_PASSWORD`
- any provider API credentials needed by future runtime modules

## First Manual Boundary

From a terminal that can SSH to the droplet:

```bash
ssh root@134.199.144.115
cd /opt/xrp-hbar-apex/deployment/runtime-scaffold-pack
ls -la
cp .env.production.example .env.production
# Fill real non-placeholder values in .env.production.
chmod +x deploy.sh
./deploy.sh
```

Then verify from outside the host:

```bash
curl -i http://134.199.144.115/health
curl -i http://134.199.144.115/ready
curl -i http://134.199.144.115/deployment/status
```

If these still return `403 Domain forbidden`, inspect the host proxy and container routing before calling the runtime live.

## Live-Proof Gate

Do not call the runtime live until all of these are true:

- the workflow run exists for a fresh `main` commit or manual dispatch
- the workflow completes successfully
- the droplet has the intended repo and commit
- Docker services are running
- `/health` returns a 2xx response
- `/ready` returns a 2xx response
- `/deployment/status` returns a 2xx response
- the response identifies the intended service/version
- one VTI/media smoke path is tested before claiming VTI runtime proof
