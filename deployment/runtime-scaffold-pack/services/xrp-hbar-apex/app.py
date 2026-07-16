import hashlib
import json
import os
from datetime import datetime, timezone
from email.utils import parseaddr
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import redis

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "xrp-hbar-apex")
APP_ENV = os.getenv("APP_ENV", "production")
APP_VERSION = os.getenv("APP_VERSION", "0.2.0")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "xrp_hbar_apex")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

GMAIL_REQUIRED_ENV = [
    "GMAIL_OAUTH_CLIENT_ID",
    "GMAIL_OAUTH_CLIENT_SECRET",
    "GMAIL_OAUTH_REFRESH_TOKEN",
]
GMAIL_OPTIONAL_ENV = [
    "GMAIL_OAUTH_TOKEN_URI",
    "GMAIL_NEWSLETTER_QUERY",
    "GMAIL_NEWSLETTER_MAX_RESULTS",
]
GMAIL_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
PLACEHOLDER_VALUES = {
    "",
    "change_me",
    "change-me",
    "placeholder",
    "todo",
    "your-client-id.apps.googleusercontent.com",
    "your-client-secret",
    "your-refresh-token",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _sha(value):
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _short_hash(*parts, length=24):
    return hashlib.sha256("|".join([str(part or "") for part in parts]).encode("utf-8")).hexdigest()[:length]


def _json_response(payload, status=200):
    return jsonify(payload), status


def _db_connect():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=3,
        row_factory=dict_row,
    )


def _ensure_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vti_smoke_evidence (
                source_id TEXT PRIMARY KEY,
                source_url TEXT NOT NULL,
                domain TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                proof_label TEXT NOT NULL,
                evidence JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_newsletter_proof (
                proof_id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                source_url TEXT,
                subject TEXT NOT NULL,
                received_at TEXT,
                proof_label TEXT NOT NULL,
                evidence JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gmail_fetch_proof (
                proof_id TEXT PRIMARY KEY,
                proof_label TEXT NOT NULL,
                query TEXT NOT NULL,
                message_count INTEGER NOT NULL,
                token_refresh_proven BOOLEAN NOT NULL,
                sanitized_messages JSONB NOT NULL,
                evidence JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS phase_checkpoint (
                phase_id TEXT PRIMARY KEY,
                proof_label TEXT NOT NULL,
                status TEXT NOT NULL,
                checkpoint JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS claim_candidate (
                claim_id TEXT PRIMARY KEY,
                source_proof_id TEXT NOT NULL,
                source_type TEXT NOT NULL,
                claim_text_hash TEXT NOT NULL,
                claim_preview TEXT NOT NULL,
                proof_label TEXT NOT NULL,
                evidence JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS evidence_pack_export (
                pack_id TEXT PRIMARY KEY,
                proof_label TEXT NOT NULL,
                pack JSONB NOT NULL,
                limits JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)


def _env_status(name, required):
    value = os.getenv(name, "").strip()
    configured = bool(value) and value.lower() not in PLACEHOLDER_VALUES
    return {"name": name, "required": required, "configured": configured, "value_visible": False}


def _configured_gmail_env():
    required = [_env_status(name, True) for name in GMAIL_REQUIRED_ENV]
    optional = [_env_status(name, False) for name in GMAIL_OPTIONAL_ENV]
    return required, optional, all(item["configured"] for item in required)


def _http_json(url, *, method="GET", headers=None, data=None, timeout=20):
    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8") if isinstance(data, dict) else data
    req = Request(url, data=body, method=method, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"error": raw[:500]}
        return e.code, payload
    except URLError as e:
        return 0, {"error": str(e.reason)}


def _gmail_refresh_token():
    token_uri = os.getenv("GMAIL_OAUTH_TOKEN_URI", "https://oauth2.googleapis.com/token").strip()
    body = urlencode({
        "client_id": os.getenv("GMAIL_OAUTH_CLIENT_ID", ""),
        "client_secret": os.getenv("GMAIL_OAUTH_CLIENT_SECRET", ""),
        "refresh_token": os.getenv("GMAIL_OAUTH_REFRESH_TOKEN", ""),
        "grant_type": "refresh_token",
    }).encode("utf-8")
    status, payload = _http_json(token_uri, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"}, data=body, timeout=20)
    access_token = payload.get("access_token") if isinstance(payload, dict) else None
    return {
        "ok": status == 200 and bool(access_token),
        "status_code": status,
        "access_token": access_token,
        "scope": payload.get("scope") if isinstance(payload, dict) else None,
        "expires_in_present": "expires_in" in payload if isinstance(payload, dict) else False,
        "error_type": payload.get("error") if isinstance(payload, dict) else "request_failed",
    }


def _gmail_api_get(path, access_token, params=None):
    query = f"?{urlencode(params)}" if params else ""
    return _http_json(f"https://gmail.googleapis.com/gmail/v1/{path}{query}", headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"}, timeout=20)


def _header_map(message):
    headers = message.get("payload", {}).get("headers", [])
    return {item.get("name", "").lower(): item.get("value", "") for item in headers}


def _sender_domain_hash(from_header):
    _, addr = parseaddr(from_header or "")
    domain = addr.split("@", 1)[1].lower() if "@" in addr else ""
    return _sha(domain)


def _sanitize_gmail_message(message):
    headers = _header_map(message)
    subject = headers.get("subject", "")
    from_header = headers.get("from", "")
    date_header = headers.get("date", "")
    list_id = headers.get("list-id", "")
    snippet = message.get("snippet", "")
    return {
        "message_id_hash": _sha(message.get("id", "")),
        "thread_id_hash": _sha(message.get("threadId", "")),
        "history_id_hash": _sha(str(message.get("historyId", ""))),
        "internal_date": message.get("internalDate"),
        "subject_sha256": _sha(subject),
        "subject_preview": subject[:90] if subject else None,
        "from_domain_sha256": _sender_domain_hash(from_header),
        "date_header_present": bool(date_header),
        "list_id_sha256": _sha(list_id),
        "snippet_sha256": _sha(snippet),
        "snippet_preview": snippet[:120] if snippet else None,
    }


def _store_checkpoint(phase_id, proof_label, status, checkpoint, limits):
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO phase_checkpoint (phase_id, proof_label, status, checkpoint, limits)
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (phase_id) DO UPDATE SET
                    proof_label = EXCLUDED.proof_label,
                    status = EXCLUDED.status,
                    checkpoint = EXCLUDED.checkpoint,
                    limits = EXCLUDED.limits,
                    updated_at = now();
            """, (phase_id, proof_label, status, Jsonb(checkpoint), Jsonb(limits)))


@app.route("/health")
def health():
    return _json_response({"status": "ok", "service": APP_NAME, "env": APP_ENV, "version": APP_VERSION})


@app.route("/ready")
def ready():
    db_ok = False
    redis_ok = False
    db_error = None
    redis_error = None
    try:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1;")
                cur.fetchone()
        db_ok = True
    except Exception as e:
        db_error = str(e)
    try:
        redis_ok = redis.from_url(REDIS_URL, socket_connect_timeout=3).ping()
    except Exception as e:
        redis_error = str(e)
    if db_ok and redis_ok:
        return _json_response({"status": "ready", "postgres": "ok", "redis": "ok"})
    return _json_response({"status": "not_ready", "postgres": "ok" if db_ok else db_error, "redis": "ok" if redis_ok else redis_error}, 503)


@app.route("/deployment/status")
def deployment_status():
    return _json_response({
        "status": "running",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "stack": ["app", "postgres", "redis", "caddy"],
        "framework_layers": {
            "gmail_readonly_fetch_smoke": "available_but_requires_runtime_credentials",
            "recurring_newsletter_checkpoint_scaffold": "available",
            "newsletter_claim_extraction_scaffold": "available",
            "vti_external_worker_checkpoint_scaffold": "available",
            "evidence_pack_export_scaffold": "available",
            "dedupe_retry_checkpoint_backfill_scaffold": "available",
        },
    })


@app.route("/email/newsletter/gmail/status")
def gmail_status():
    required_env, optional_env, configured = _configured_gmail_env()
    token_refresh = {"attempted": False, "succeeded": False, "status_code": None, "scope_contains_required": False, "access_token_visible": False, "error_type": None}
    if configured:
        result = _gmail_refresh_token()
        scope = result.get("scope") or ""
        token_refresh = {
            "attempted": True,
            "succeeded": result["ok"],
            "status_code": result["status_code"],
            "scope_contains_required": GMAIL_SCOPE in scope or not scope,
            "expires_in_present": result["expires_in_present"],
            "access_token_visible": False,
            "error_type": None if result["ok"] else result.get("error_type"),
        }
    ready = configured and token_refresh["succeeded"] and token_refresh["scope_contains_required"]
    return _json_response({
        "status": "ready_for_fetch_token_refresh_proven" if ready else ("credentials_present_but_token_refresh_failed" if configured else "pending_credentials"),
        "service": APP_NAME,
        "mode": "gmail_newsletter_runtime_status",
        "proof_label": "GMAIL_NEWSLETTER_STATUS_TOKEN_REFRESH_PROOF_GATE",
        "required_env": required_env,
        "optional_env": optional_env,
        "required_scopes": [GMAIL_SCOPE],
        "evidence": {"env_names_declared": True, "runtime_credentials_configured": configured, "token_refresh": token_refresh, "secret_values_hidden": True},
        "limits": {"gmail_messages_read": False, "gmail_fetch_proof_persisted": False, "recurring_sync_enabled": False, "claim_verification_enabled": False},
        "next_gate": "POST /email/newsletter/gmail/fetch" if ready else "install valid Gmail OAuth runtime credentials with gmail.readonly scope",
    }, 200 if not configured or ready else 503)


@app.route("/email/newsletter/gmail/fetch", methods=["POST"])
def gmail_fetch():
    _, _, configured = _configured_gmail_env()
    if not configured:
        return _json_response({"status": "blocked", "proof_label": "GMAIL_RUNTIME_CREDENTIALS_MISSING", "error": "required Gmail OAuth runtime env vars are not configured"}, 503)
    token = _gmail_refresh_token()
    if not token["ok"]:
        return _json_response({"status": "blocked", "proof_label": "GMAIL_TOKEN_REFRESH_FAILED", "error_type": token.get("error_type"), "status_code": token.get("status_code"), "secret_values_hidden": True}, 503)
    payload = request.get_json(silent=True) or {}
    query = str(payload.get("query") or os.getenv("GMAIL_NEWSLETTER_QUERY", "category:primary newer_than:30d")).strip()
    try:
        max_results = int(payload.get("max_results") or os.getenv("GMAIL_NEWSLETTER_MAX_RESULTS", "5"))
    except ValueError:
        max_results = 5
    max_results = max(1, min(max_results, 10))
    status, listing = _gmail_api_get("users/me/messages", token["access_token"], {"q": query, "maxResults": max_results})
    if status != 200:
        return _json_response({"status": "blocked", "proof_label": "GMAIL_MESSAGE_LIST_FAILED", "gmail_status_code": status, "gmail_error_type": listing.get("error", {}).get("status") if isinstance(listing, dict) else None}, 502)
    messages = []
    for item in listing.get("messages", [])[:max_results]:
        message_id = item.get("id")
        if not message_id:
            continue
        status, detail = _gmail_api_get(f"users/me/messages/{message_id}", token["access_token"], {"format": "metadata", "metadataHeaders": ["Subject", "From", "Date", "List-Id"]})
        if status == 200:
            messages.append(_sanitize_gmail_message(detail))
    proof_id = _short_hash(query, len(messages), _now())
    evidence = {"token_refresh_proven": True, "gmail_message_list_read": True, "gmail_metadata_messages_read": len(messages), "query_sha256": _sha(query), "result_size_estimate": listing.get("resultSizeEstimate"), "persisted_at_utc": _now(), "secret_values_hidden": True}
    limits = {"message_body_read": False, "attachments_read": False, "email_addresses_exposed": False, "recurring_sync_enabled": False, "claim_verification_enabled": False}
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO gmail_fetch_proof (proof_id, proof_label, query, message_count, token_refresh_proven, sanitized_messages, evidence, limits)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb)
                ON CONFLICT (proof_id) DO UPDATE SET
                    proof_label = EXCLUDED.proof_label,
                    query = EXCLUDED.query,
                    message_count = EXCLUDED.message_count,
                    token_refresh_proven = EXCLUDED.token_refresh_proven,
                    sanitized_messages = EXCLUDED.sanitized_messages,
                    evidence = EXCLUDED.evidence,
                    limits = EXCLUDED.limits,
                    updated_at = now();
            """, (proof_id, "GMAIL_READONLY_METADATA_FETCH_SMOKE_PROVEN", query, len(messages), True, Jsonb(messages), Jsonb(evidence), Jsonb(limits)))
    return _json_response({"status": "accepted", "proof_id": proof_id, "proof_label": "GMAIL_READONLY_METADATA_FETCH_SMOKE_PROVEN", "retrieval_url": f"/email/newsletter/gmail/proof/{proof_id}", "message_count": len(messages), "evidence": evidence, "limits": limits})


def _format_gmail_row(row):
    return {"proof_id": row["proof_id"], "proof_label": row["proof_label"], "query_sha256": _sha(row["query"]), "message_count": row["message_count"], "token_refresh_proven": row["token_refresh_proven"], "sanitized_messages": row["sanitized_messages"], "evidence": row["evidence"], "limits": row["limits"], "created_at": row["created_at"].isoformat(), "updated_at": row["updated_at"].isoformat()}


@app.route("/email/newsletter/gmail/proof/latest")
def gmail_latest_proof():
    try:
        with _db_connect() as conn:
            _ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM gmail_fetch_proof ORDER BY updated_at DESC, created_at DESC LIMIT 1;")
                row = cur.fetchone()
    except Exception as e:
        return _json_response({"status": "latest_retrieval_failed", "error": str(e)}, 503)
    if not row:
        return _json_response({"status": "not_found", "message": "no Gmail fetch proof has been persisted yet"}, 404)
    return _json_response({"status": "found", "mode": "gmail_latest_fetch_proof_retrieval", **_format_gmail_row(row)})


@app.route("/email/newsletter/gmail/proof/<proof_id>")
def gmail_proof(proof_id):
    try:
        with _db_connect() as conn:
            _ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM gmail_fetch_proof WHERE proof_id = %s;", (proof_id.strip(),))
                row = cur.fetchone()
    except Exception as e:
        return _json_response({"status": "retrieval_failed", "error": str(e)}, 503)
    if not row:
        return _json_response({"status": "not_found", "proof_id": proof_id}, 404)
    return _json_response({"status": "found", "mode": "gmail_fetch_proof_retrieval", **_format_gmail_row(row)})


@app.route("/email/newsletter/status")
def email_newsletter_status():
    return _json_response({"status": "ready", "proof_label": "EMAIL_NEWSLETTER_SCAFFOLD_STATUS_PROVEN", "capabilities": ["manual_newsletter_proof_persistence", "gmail_readonly_metadata_fetch_proof", "recurring_sync_checkpoint_scaffold", "claim_candidate_extraction_scaffold"], "limits": ["no_full_gmail_automation_claim", "no_claim_verification_claim"]})


@app.route("/email/newsletter/smoke", methods=["POST"])
def email_newsletter_smoke():
    payload = request.get_json(silent=True) or {}
    source_name = str(payload.get("source_name", "")).strip()
    subject = str(payload.get("subject", "")).strip()
    if not source_name or not subject:
        return _json_response({"status": "invalid", "error": "source_name and subject are required"}, 400)
    source_url = str(payload.get("source_url", "")).strip()
    received_at = str(payload.get("received_at", "")).strip()
    summary = str(payload.get("summary", "")).strip()
    tags = payload.get("tags", [])
    clean_tags = [str(tag).strip() for tag in tags if str(tag).strip()] if isinstance(tags, list) else []
    proof_id = _short_hash(source_name, source_url, subject, summary)
    evidence = {"manual_intake_captured": True, "summary_captured": bool(summary), "tags": clean_tags, "summary_sha256": _sha(summary), "persisted_at_utc": _now()}
    limits = {"gmail_connector_fetch": False, "recurring_newsletter_sync": False, "automatic_claim_extraction": False, "automatic_research_verification": False}
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO email_newsletter_proof (proof_id, source_name, source_url, subject, received_at, proof_label, evidence, limits)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (proof_id) DO UPDATE SET
                    source_name = EXCLUDED.source_name,
                    source_url = EXCLUDED.source_url,
                    subject = EXCLUDED.subject,
                    received_at = EXCLUDED.received_at,
                    proof_label = EXCLUDED.proof_label,
                    evidence = EXCLUDED.evidence,
                    limits = EXCLUDED.limits,
                    updated_at = now();
            """, (proof_id, source_name, source_url or None, subject, received_at or None, "EMAIL_NEWSLETTER_MANUAL_INTAKE_SMOKE_PROVEN", Jsonb(evidence), Jsonb(limits)))
    return _json_response({"status": "accepted", "proof_label": "EMAIL_NEWSLETTER_MANUAL_INTAKE_SMOKE_PROVEN", "proof_id": proof_id, "retrieval_url": f"/email/newsletter/proof/{proof_id}", "evidence": evidence, "limits": limits})


def _format_newsletter_row(row):
    return {"proof_label": row["proof_label"], "newsletter_record": {"proof_id": row["proof_id"], "source_name": row["source_name"], "source_url": row["source_url"], "subject": row["subject"], "received_at": row["received_at"]}, "evidence": row["evidence"], "limits": row["limits"], "created_at": row["created_at"].isoformat(), "updated_at": row["updated_at"].isoformat()}


@app.route("/email/newsletter/proof/latest")
def email_newsletter_latest_proof():
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM email_newsletter_proof ORDER BY updated_at DESC, created_at DESC LIMIT 1;")
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "message": "no email/newsletter proof has been persisted yet"}, 404)
    return _json_response({"status": "found", "mode": "email_newsletter_latest_proof_retrieval", **_format_newsletter_row(row)})


@app.route("/email/newsletter/proof/<proof_id>")
def email_newsletter_proof(proof_id):
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM email_newsletter_proof WHERE proof_id = %s;", (proof_id.strip(),))
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "proof_id": proof_id}, 404)
    return _json_response({"status": "found", "mode": "email_newsletter_proof_id_retrieval", **_format_newsletter_row(row)})


@app.route("/email/newsletter/proof")
def email_newsletter_proof_list():
    limit = max(1, min(int(request.args.get("limit", "10")), 50))
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM email_newsletter_proof ORDER BY updated_at DESC, created_at DESC LIMIT %s;", (limit,))
            rows = cur.fetchall()
    return _json_response({"status": "ok", "proof_label": "EMAIL_NEWSLETTER_PERSISTED_PROOF_LIST_RETRIEVAL_PROVEN", "count": len(rows), "items": [_format_newsletter_row(row) for row in rows]})


@app.route("/email/newsletter/sync/status")
def newsletter_sync_status():
    return _json_response({"status": "ready", "proof_label": "RECURRING_NEWSLETTER_SYNC_CHECKPOINT_SCAFFOLD_AVAILABLE", "limits": {"scheduler_enabled": False, "gmail_fetch_called_by_scheduler": False}})


@app.route("/email/newsletter/sync/checkpoint", methods=["POST"])
def newsletter_sync_checkpoint():
    payload = request.get_json(silent=True) or {}
    checkpoint = {"source": str(payload.get("source", "manual-or-gmail")).strip(), "last_seen_proof_id": str(payload.get("last_seen_proof_id", "")).strip() or None, "checkpointed_at_utc": _now()}
    limits = {"recurring_scheduler": False, "automatic_backfill": False}
    _store_checkpoint("newsletter-sync", "RECURRING_NEWSLETTER_SYNC_CHECKPOINT_PERSISTED", "checkpointed", checkpoint, limits)
    return _json_response({"status": "accepted", "proof_label": "RECURRING_NEWSLETTER_SYNC_CHECKPOINT_PERSISTED", "checkpoint": checkpoint, "limits": limits})


@app.route("/email/newsletter/claims/status")
def claim_status():
    return _json_response({"status": "ready", "proof_label": "NEWSLETTER_CLAIM_EXTRACTION_SCAFFOLD_AVAILABLE", "limits": {"claim_verification": False, "source_citation_validation": False}})


@app.route("/email/newsletter/claims/extract", methods=["POST"])
def claim_extract():
    payload = request.get_json(silent=True) or {}
    text = str(payload.get("text", "")).strip()
    source_proof_id = str(payload.get("source_proof_id", "manual")).strip()
    if not text:
        return _json_response({"status": "invalid", "error": "text is required for claim candidate extraction"}, 400)
    candidates = []
    for chunk in [part.strip() for part in text.replace("\n", " ").split(".") if part.strip()][:5]:
        preview = chunk[:180]
        claim_id = _short_hash(source_proof_id, preview)
        evidence = {"extraction_scaffold_used": True, "claim_preview_sha256": _sha(preview), "extracted_at_utc": _now()}
        limits = {"claim_verified": False, "source_checked": False, "ranking_updated": False}
        with _db_connect() as conn:
            _ensure_tables(conn)
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO claim_candidate (claim_id, source_proof_id, source_type, claim_text_hash, claim_preview, proof_label, evidence, limits)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                    ON CONFLICT (claim_id) DO UPDATE SET
                        evidence = EXCLUDED.evidence,
                        limits = EXCLUDED.limits,
                        updated_at = now();
                """, (claim_id, source_proof_id, "newsletter_or_gmail_metadata", _sha(chunk), preview, "NEWSLETTER_CLAIM_CANDIDATE_EXTRACTION_SCAFFOLD_PROVEN", Jsonb(evidence), Jsonb(limits)))
        candidates.append({"claim_id": claim_id, "claim_preview": preview, "limits": limits})
    return _json_response({"status": "accepted", "proof_label": "NEWSLETTER_CLAIM_CANDIDATE_EXTRACTION_SCAFFOLD_PROVEN", "candidate_count": len(candidates), "candidates": candidates})


@app.route("/vti/status")
def vti_status():
    return _json_response({"status": "ready", "proof_label": "VTI_SMOKE_AND_WORKER_SCAFFOLD_AVAILABLE", "limits": {"external_media_fetch": False, "caption_worker": False, "ocr_worker": False, "claim_verification_worker": False}})


@app.route("/vti/smoke", methods=["POST"])
def vti_smoke():
    payload = request.get_json(silent=True) or {}
    source_url = str(payload.get("source_url", "")).strip()
    if not source_url:
        return _json_response({"status": "invalid", "error": "source_url is required"}, 400)
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return _json_response({"status": "invalid", "error": "source_url must be an http or https URL"}, 400)
    transcript = str(payload.get("transcript", "")).strip()
    ocr_text = str(payload.get("ocr_text", "")).strip()
    title = str(payload.get("title", "")).strip()
    platform = str(payload.get("platform", "")).strip() or parsed.netloc
    source_id = _short_hash(source_url, transcript[:2000], ocr_text[:2000])
    evidence = {"copied_link_captured": True, "manual_transcript_captured": bool(transcript), "ocr_text_captured": bool(ocr_text), "transcript_word_count": len(transcript.split()), "ocr_word_count": len(ocr_text.split()), "transcript_sha256": _sha(transcript), "ocr_text_sha256": _sha(ocr_text), "persisted_at_utc": _now()}
    limits = {"automatic_media_fetch": False, "automatic_caption_fetch": False, "automatic_ocr_worker": False, "claim_verification_worker": False}
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO vti_smoke_evidence (source_id, source_url, domain, platform, title, proof_label, evidence, limits)
                VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (source_id) DO UPDATE SET
                    source_url = EXCLUDED.source_url,
                    domain = EXCLUDED.domain,
                    platform = EXCLUDED.platform,
                    title = EXCLUDED.title,
                    proof_label = EXCLUDED.proof_label,
                    evidence = EXCLUDED.evidence,
                    limits = EXCLUDED.limits,
                    updated_at = now();
            """, (source_id, source_url, parsed.netloc, platform, title or None, "VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN", Jsonb(evidence), Jsonb(limits)))
    return _json_response({"status": "accepted", "proof_label": "VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN", "retrieval_url": f"/vti/evidence/{source_id}", "source_record": {"source_id": source_id, "source_url": source_url, "domain": parsed.netloc, "platform": platform, "title": title or None}, "evidence": evidence, "limits": limits})


def _format_vti_row(row):
    return {"proof_label": row["proof_label"], "source_record": {"source_id": row["source_id"], "source_url": row["source_url"], "domain": row["domain"], "platform": row["platform"], "title": row["title"]}, "evidence": row["evidence"], "limits": row["limits"], "created_at": row["created_at"].isoformat(), "updated_at": row["updated_at"].isoformat()}


@app.route("/vti/evidence/<source_id>")
def vti_evidence(source_id):
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vti_smoke_evidence WHERE source_id = %s;", (source_id.strip(),))
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "source_id": source_id}, 404)
    return _json_response({"status": "found", "mode": "vti_evidence_retrieval", **_format_vti_row(row)})


@app.route("/vti/evidence/latest")
def vti_latest():
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vti_smoke_evidence ORDER BY updated_at DESC, created_at DESC LIMIT 1;")
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "message": "no VTI smoke evidence has been persisted yet"}, 404)
    return _json_response({"status": "found", "mode": "vti_latest_evidence_retrieval", **_format_vti_row(row)})


@app.route("/vti/evidence")
def vti_list():
    limit = max(1, min(int(request.args.get("limit", "10")), 50))
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vti_smoke_evidence ORDER BY updated_at DESC, created_at DESC LIMIT %s;", (limit,))
            rows = cur.fetchall()
    return _json_response({"status": "ok", "proof_label": "VTI_PERSISTED_EVIDENCE_LIST_RETRIEVAL_PROVEN", "count": len(rows), "items": [_format_vti_row(row) for row in rows]})


@app.route("/vti/worker/status")
def vti_worker_status():
    return _json_response({"status": "ready", "proof_label": "VTI_EXTERNAL_MEDIA_CAPTION_OCR_WORKER_SCAFFOLD_AVAILABLE", "limits": {"external_fetch_enabled": False, "caption_fetch_enabled": False, "ocr_execution_enabled": False}})


@app.route("/vti/worker/checkpoint", methods=["POST"])
def vti_worker_checkpoint():
    payload = request.get_json(silent=True) or {}
    checkpoint = {"source_url": str(payload.get("source_url", "")).strip() or None, "worker_stage": str(payload.get("worker_stage", "queued")).strip(), "checkpointed_at_utc": _now()}
    limits = {"media_downloaded": False, "caption_downloaded": False, "ocr_completed": False}
    _store_checkpoint("vti-worker", "VTI_EXTERNAL_WORKER_CHECKPOINT_PERSISTED", "checkpointed", checkpoint, limits)
    return _json_response({"status": "accepted", "proof_label": "VTI_EXTERNAL_WORKER_CHECKPOINT_PERSISTED", "checkpoint": checkpoint, "limits": limits})


@app.route("/evidence-pack/status")
def evidence_pack_status():
    return _json_response({"status": "ready", "proof_label": "EVIDENCE_PACK_EXPORT_SCAFFOLD_AVAILABLE", "limits": {"file_export": False, "full_claim_verification": False}})


@app.route("/evidence-pack/latest")
def evidence_pack_latest():
    pack = {"generated_at_utc": _now(), "service": APP_NAME, "latest": {}}
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            for key, table in [("gmail", "gmail_fetch_proof"), ("newsletter", "email_newsletter_proof"), ("vti", "vti_smoke_evidence")]:
                cur.execute(f"SELECT * FROM {table} ORDER BY updated_at DESC, created_at DESC LIMIT 1;")
                row = cur.fetchone()
                pack["latest"][key] = bool(row)
    pack_id = _short_hash(json.dumps(pack, sort_keys=True), _now())
    limits = {"downloadable_file_created": False, "claim_verification_included": False}
    with _db_connect() as conn:
        _ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO evidence_pack_export (pack_id, proof_label, pack, limits)
                VALUES (%s, %s, %s::jsonb, %s::jsonb)
                ON CONFLICT (pack_id) DO UPDATE SET pack = EXCLUDED.pack, limits = EXCLUDED.limits, updated_at = now();
            """, (pack_id, "EVIDENCE_PACK_LATEST_JSON_EXPORT_SCAFFOLD_PROVEN", Jsonb(pack), Jsonb(limits)))
    return _json_response({"status": "accepted", "pack_id": pack_id, "proof_label": "EVIDENCE_PACK_LATEST_JSON_EXPORT_SCAFFOLD_PROVEN", "pack": pack, "limits": limits})


@app.route("/ops/dedupe-retry-backfill/status")
def ops_status():
    return _json_response({"status": "ready", "proof_label": "DEDUPE_RETRY_CHECKPOINT_BACKFILL_SCAFFOLD_AVAILABLE", "limits": {"automatic_backfill_worker": False, "dead_letter_queue": False}})


@app.route("/ops/dedupe-retry-backfill/checkpoint", methods=["POST"])
def ops_checkpoint():
    payload = request.get_json(silent=True) or {}
    checkpoint = {"dedupe_key_sha256": _sha(str(payload.get("dedupe_key", "")).strip()), "retry_count": int(payload.get("retry_count", 0) or 0), "backfill_cursor": str(payload.get("backfill_cursor", "")).strip() or None, "checkpointed_at_utc": _now()}
    limits = {"automatic_retry_worker": False, "automatic_backfill_worker": False}
    _store_checkpoint("dedupe-retry-backfill", "DEDUPE_RETRY_BACKFILL_CHECKPOINT_PERSISTED", "checkpointed", checkpoint, limits)
    return _json_response({"status": "accepted", "proof_label": "DEDUPE_RETRY_BACKFILL_CHECKPOINT_PERSISTED", "checkpoint": checkpoint, "limits": limits})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
