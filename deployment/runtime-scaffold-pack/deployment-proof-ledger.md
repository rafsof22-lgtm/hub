# Deployment Proof Ledger

## 2026-07-17 Batched Remediation Pass

Target:

- Repo: `rafsof22-lgtm/hub`
- Branch: `main`
- Production URL: `http://134.199.144.115`

Repo-side changes in this pass:

- Added explicit `PUBLIC_ROUTE_PROOF` log labels to the DigitalOcean deploy workflow.
- Preserved fatal core/public route checks for non-Gmail production proof routes.
- Preserved separate Gmail OAuth proof handling so Gmail `invalid_grant` does not masquerade as core production failure.
- Updated runtime README with the current Gmail secret replacement gate and required Gmail readonly scope.

Known evidence entering this pass from DigitalOcean Auto Deploy #130:

- Core production proof passed.
- Gmail proof failed only at `/email/newsletter/gmail/status` with HTTP 503.
- Gmail token refresh attempted and failed with `invalid_grant` / HTTP 400.
- Required scope included `https://www.googleapis.com/auth/gmail.readonly`.
- Secret values remained hidden.

Current public-route recheck during this pass:

- `/health`: `403 Domain forbidden`
- `/ready`: `403 Domain forbidden`
- `/deployment/status`: `403 Domain forbidden`
- `/email/newsletter/status`: `403 Domain forbidden`
- `/email/newsletter/gmail/status`: `403 Domain forbidden`
- `/email/newsletter/gmail/proof/latest`: `403 Domain forbidden`

Current blocker classes:

- `PUBLIC_ROUTE_PROOF_FAILED_CURRENT_403_DOMAIN_FORBIDDEN`
- `GMAIL_OAUTH_INVALID_GRANT_REFRESH_TOKEN_REPLACE_REQUIRED`

Manual secret action required after public route proof is restored:

- Replace `GMAIL_OAUTH_REFRESH_TOKEN`.
- If the new token was generated against a different OAuth client, replace `GMAIL_OAUTH_CLIENT_ID`, `GMAIL_OAUTH_CLIENT_SECRET`, and `GMAIL_OAUTH_REFRESH_TOKEN` together.

Required scope:

- `https://www.googleapis.com/auth/gmail.readonly`

Next proof gate:

- Rerun or trigger DigitalOcean Auto Deploy from a non-doc `main` commit, verify `PUBLIC_ROUTE_PROOF=PASS`, then verify `GMAIL_OAUTH_PROOF=PASS` after the OAuth secret replacement.
