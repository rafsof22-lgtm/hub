# DigitalOcean Key And Secret Runbook

## Current Safe Status

DigitalOcean account key inventory currently includes the GitHub Actions deploy public key used by the latest workflow run:

- DigitalOcean key name: `github-actions-deploy-2026-07-16-active`
- DigitalOcean key id: `57820900`
- Fingerprint: `cd:d7:63:29:26:e0:75:f0:6d:49:b0:74:88:f3:2b:73`
- Public key: `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy`

A prior fresh ED25519 keypair was also generated for deployment use on 2026-07-15 and added to the DigitalOcean account:

- DigitalOcean key name: `xrp-hbar-github-actions-2026-07-15-fresh`
- DigitalOcean key id: `57804116`
- Fingerprint: `cd:a4:e3:6b:a3:a1:66:51:b6:f7:57:d9:ff:0b:30:5d`

Private keys, passwords, reset tokens, and one-time credentials must not be committed to this repo, pasted into chat, or stored in any non-secret file.

## Existing Droplet

- Droplet name: `Digital-ocean-XRP-Hbar-Apex`
- Droplet id: `584697763`
- Public IPv4: `134.199.144.115`
- Region: `syd1`
- Image: Ubuntu 24.04 LTS

## Important Existing-Droplet Rule

Adding a public key to the DigitalOcean account does not automatically install that key on an existing droplet.

For the existing droplet `Digital-ocean-XRP-Hbar-Apex` at `134.199.144.115`, the public key used by GitHub Actions must also be present in:

```text
/root/.ssh/authorized_keys
```

Use either an already-working SSH session or the DigitalOcean web console to append the public key.

## Current Access-Recovery Clue

A read-only Gmail search on 2026-07-16 found a recent DigitalOcean Support message for this exact droplet with subject `Your Droplet's password has been reset. (Digital-ocean-XRP-Hbar-Apex)`.

The password or reset value must not be copied into GitHub, docs, or chat. Use the original email or DigitalOcean console directly as an owner-controlled recovery path if no already-working SSH session is available.

After access is regained, append the current Actions public key to `/root/.ssh/authorized_keys`, then rerun the deploy workflow.

## GitHub Actions Secret Required

Set this GitHub Actions Secret:

```text
DIGITALOCEAN_SSH_KEY=<full private OpenSSH key block matching the public key authorized on the droplet>
```

The current workflow-derived public key is:

```text
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIC0VjJjMeayv3ggrElS2vZIDlXUIXw6fER+op4UVs4DQ github-actions-deploy
```

The private key value must include:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
...
-----END OPENSSH PRIVATE KEY-----
```

Do not include:

- `DIGITALOCEAN_SSH_KEY=`
- quotes
- markdown fences
- `COPY_START`
- `COPY_END`
- comments or extra wrapper text

## GitHub Actions Variables Required

Set these Actions Variables or Secrets:

```text
DIGITALOCEAN_HOST=134.199.144.115
DIGITALOCEAN_USER=root
DIGITALOCEAN_PORT=22
DIGITALOCEAN_DROPLET_ID=584697763
APP_DIR=/opt/xrp-hbar-apex
BASE_URL=https://<real-live-domain>
```

`BASE_URL` must be the real domain that should pass public workflow checks. Do not leave `YOUR-DOMAIN.com`.

## DigitalOcean API Token Improvement

A diagnostics workflow may be used when present at:

```text
.github/workflows/digitalocean-diagnostics.yml
```

To enable it, create a DigitalOcean personal access token with the minimum scopes needed for read-only droplet diagnostics where possible.

Store it only as a GitHub Actions Secret:

```text
DIGITALOCEAN_ACCESS_TOKEN=<token value>
```

Do not commit it to the repo and do not paste it into chat.

Recommended initial use:

- read droplet metadata
- read action status
- read firewall or domain metadata if needed
- probe SSH and public HTTP/HTTPS endpoints from GitHub Actions

Avoid using the token for destructive actions from CI unless a separate approval gate is added.

## Verification After Secret Placement

After the SSH key and variables are placed:

1. Rerun `DigitalOcean Auto Deploy`, or push a harmless commit to `main`.
2. Confirm `Prepare SSH key` passes.
3. Confirm SSH deploy connects to `root@134.199.144.115`.
4. Confirm droplet commit matches the latest `main` commit.
5. Confirm local checks pass:

```bash
curl -I http://127.0.0.1/health
curl -I http://127.0.0.1/ready
curl -I http://127.0.0.1/deployment/status
```

6. Confirm public checks pass:

```bash
curl -I https://<real-live-domain>/health
curl -I https://<real-live-domain>/ready
curl -I https://<real-live-domain>/deployment/status
```

Only then label the deployment fully verified.
