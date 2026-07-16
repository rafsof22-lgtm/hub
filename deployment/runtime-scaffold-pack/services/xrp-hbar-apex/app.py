import hashlib
import os
from datetime import datetime, timezone
from urllib.parse import urlparse

from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import redis

app = Flask(__name__)

APP_NAME = os.getenv("APP_NAME", "xrp-hbar-apex")
APP_ENV = os.getenv("APP_ENV", "production")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "xrp_hbar_apex")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_me")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
GMAIL_NEWSLETTER_REQUIRED_ENV = [
    "GMAIL_OAUTH_CLIENT_ID",
    "GMAIL_OAUTH_CLIENT_SECRET",
    "GMAIL_OAUTH_REFRESH_TOKEN"
]
GMAIL_NEWSLETTER_OPTIONAL_ENV = [
    "GMAIL_OAUTH_TOKEN_URI",
    "GMAIL_NEWSLETTER_QUERY",
    "GMAIL_NEWSLETTER_MAX_RESULTS"
]
GMAIL_NEWSLETTER_REQUIRED_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]
PLACEHOLDER_VALUES = {
    "",
    "change_me",
    "your-client-id.apps.googleusercontent.com",
    "your-client-secret",
    "your-refresh-token",
    "your-token-uri",
    "placeholder",
    "todo"
}

VTI_SMOKE_EVIDENCE_PROOF_OBJECT_SCHEMA = {
    "source_record": {
        "source_id": "deterministic sha256 prefix of source_url, transcript, and ocr_text",
        "source_url": "copied link URL",
        "domain": "parsed URL domain",
        "platform": "submitted platform or parsed domain",
        "title": "submitted title or null"
    },
    "evidence": {
        "copied_link_captured": "boolean",
        "manual_transcript_captured": "boolean",
        "ocr_text_captured": "boolean",
        "transcript_word_count": "integer",
        "ocr_word_count": "integer",
        "transcript_sha256": "sha256 hash or null",
        "ocr_text_sha256": "sha256 hash or null",
        "persisted_at_utc": "ISO-8601 timestamp"
    },
    "limits": {
        "automatic_media_fetch": "boolean",
        "automatic_caption_fetch": "boolean",
        "automatic_ocr_worker": "boolean",
        "claim_verification_worker": "boolean"
    }
}

EMAIL_NEWSLETTER_PROOF_OBJECT_SCHEMA = {
    "newsletter_record": {
        "proof_id": "deterministic sha256 prefix of source_name, source_url, subject, and summary",
        "source_name": "newsletter, alert, or research-email source name",
        "source_url": "source or archive URL, if available",
        "subject": "email/newsletter subject or title",
        "received_at": "submitted timestamp or null"
    },
    "evidence": {
        "manual_intake_captured": "boolean",
        "summary_captured": "boolean",
        "tags": "list of strings",
        "summary_sha256": "sha256 hash or null",
        "persisted_at_utc": "ISO-8601 timestamp"
    },
    "limits": {
        "gmail_connector_fetch": "boolean",
        "recurring_newsletter_sync": "boolean",
        "automatic_claim_extraction": "boolean",
        "automatic_research_verification": "boolean"
    }
}

GMAIL_NEWSLETTER_READINESS_PROOF_OBJECT_SCHEMA = {
    "readiness_record": {
        "route": "/email/newsletter/gmail/status",
        "required_env": "Gmail OAuth env vars needed before live fetch",
        "optional_env": "non-secret query/tuning env vars for later Gmail fetch",
        "required_scopes": "minimum OAuth scopes required for read-only newsletter fetch"
    },
    "evidence": {
        "env_names_declared": "boolean",
        "required_scope_declared": "boolean",
        "secret_values_hidden": "boolean",
        "runtime_credentials_configured": "boolean"
    },
    "limits": {
        "gmail_fetch_attempted": "boolean",
        "gmail_credentials_validated": "boolean",
        "gmail_messages_read": "boolean",
        "recurring_sync_enabled": "boolean"
    }
}


def _db_connect():
    return psycopg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=3,
        row_factory=dict_row
    )


def _ensure_vti_evidence_table(conn):
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


def _ensure_email_newsletter_proof_table(conn):
    with conn.cursor() as cur:
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


def _text_digest(value):
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _env_status(name, required):
    raw_value = os.getenv(name, "")
    normalized = raw_value.strip()
    configured = bool(normalized) and normalized.lower() not in PLACEHOLDER_VALUES
    return {
        "name": name,
        "required": required,
        "configured": configured,
        "value_visible": False
    }


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION
    }), 200

@app.route("/ready")
def ready():
    db_ok = False
    redis_ok = False
    db_error = None
    redis_error = None

    try:
        conn = _db_connect()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        conn.close()
        db_ok = True
    except Exception as e:
        db_error = str(e)

    try:
        r = redis.from_url(REDIS_URL, socket_connect_timeout=3)
        redis_ok = r.ping()
    except Exception as e:
        redis_error = str(e)

    if db_ok and redis_ok:
        return jsonify({
            "status": "ready",
            "postgres": "ok",
            "redis": "ok"
        }), 200

    return jsonify({
        "status": "not_ready",
        "postgres": "ok" if db_ok else db_error,
        "redis": "ok" if redis_ok else redis_error
    }), 503

@app.route("/deployment/status")
def deployment_status():
    return jsonify({
        "status": "running",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "stack": ["app", "postgres", "redis", "caddy"],
        "framework_layers": {
            "vti_smoke": "available",
            "vti_evidence_persistence": "available",
            "email_newsletter_ingestion": "manual_smoke_persistence_available_not_recurring_proven",
            "gmail_newsletter_readiness": "readiness_route_available_fetch_pending_credentials"
        }
    }), 200


@app.route("/vti/status")
def vti_status():
    return jsonify({
        "status": "ready",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "capabilities": [
            "copied_link_metadata_intake",
            "manual_transcript_intake",
            "ocr_text_intake",
            "source_record_hashing",
            "postgres_smoke_evidence_persistence",
            "source_id_evidence_retrieval",
            "latest_evidence_retrieval",
            "evidence_list_retrieval"
        ],
        "proof_object_schema": VTI_SMOKE_EVIDENCE_PROOF_OBJECT_SCHEMA,
        "proof_label": "VTI_SMOKE_AND_RETRIEVAL_ROUTES_AVAILABLE",
        "limits": [
            "no_external_media_download_yet",
            "no_automatic_caption_or_ocr_worker_yet",
            "no_claim_verification_worker_yet"
        ]
    }), 200


@app.route("/vti/smoke", methods=["POST"])
def vti_smoke():
    payload = request.get_json(silent=True) or {}
    source_url = str(payload.get("source_url", "")).strip()
    transcript = str(payload.get("transcript", "")).strip()
    ocr_text = str(payload.get("ocr_text", "")).strip()
    title = str(payload.get("title", "")).strip()
    platform = str(payload.get("platform", "")).strip()

    if not source_url:
        return jsonify({
            "status": "invalid",
            "error": "source_url is required"
        }), 400

    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return jsonify({
            "status": "invalid",
            "error": "source_url must be an http or https URL"
        }), 400

    transcript_words = transcript.split()
    ocr_words = ocr_text.split()
    source_id = hashlib.sha256(
        "|".join([source_url, transcript[:2000], ocr_text[:2000]]).encode("utf-8")
    ).hexdigest()[:24]
    proof_label = "VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN"
    evidence = {
        "copied_link_captured": True,
        "manual_transcript_captured": bool(transcript),
        "ocr_text_captured": bool(ocr_text),
        "transcript_word_count": len(transcript_words),
        "ocr_word_count": len(ocr_words),
        "transcript_sha256": _text_digest(transcript),
        "ocr_text_sha256": _text_digest(ocr_text),
        "persisted_at_utc": datetime.now(timezone.utc).isoformat()
    }
    limits = {
        "automatic_media_fetch": False,
        "automatic_caption_fetch": False,
        "automatic_ocr_worker": False,
        "claim_verification_worker": False
    }
    source_record = {
        "source_id": source_id,
        "source_url": source_url,
        "domain": parsed.netloc,
        "platform": platform or parsed.netloc,
        "title": title or None
    }

    try:
        with _db_connect() as conn:
            _ensure_vti_evidence_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO vti_smoke_evidence (
                        source_id, source_url, domain, platform, title,
                        proof_label, evidence, limits
                    )
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
                    """,
                    (
                        source_id,
                        source_url,
                        parsed.netloc,
                        platform or parsed.netloc,
                        title or None,
                        proof_label,
                        Jsonb(evidence),
                        Jsonb(limits)
                    )
                )
    except Exception as e:
        return jsonify({
            "status": "persistence_failed",
            "error": str(e),
            "source_record": source_record,
            "evidence": evidence,
            "limits": limits
        }), 503

    return jsonify({
        "status": "accepted",
        "service": APP_NAME,
        "mode": "vti_smoke",
        "proof_label": proof_label,
        "persistence": "stored",
        "retrieval_url": f"/vti/evidence/{source_id}",
        "source_record": source_record,
        "evidence": evidence,
        "limits": limits
    }), 200


@app.route("/vti/evidence/<source_id>")
def vti_evidence(source_id):
    clean_source_id = source_id.strip()
    if not clean_source_id:
        return jsonify({
            "status": "invalid",
            "error": "source_id is required"
        }), 400

    try:
        with _db_connect() as conn:
            _ensure_vti_evidence_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT source_id, source_url, domain, platform, title,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM vti_smoke_evidence
                    WHERE source_id = %s;
                    """,
                    (clean_source_id,)
                )
                row = cur.fetchone()
    except Exception as e:
        return jsonify({
            "status": "retrieval_failed",
            "error": str(e)
        }), 503

    if not row:
        return jsonify({
            "status": "not_found",
            "source_id": clean_source_id
        }), 404

    return jsonify({
        "status": "found",
        "service": APP_NAME,
        "mode": "vti_evidence_retrieval",
        "proof_label": row["proof_label"],
        "source_record": {
            "source_id": row["source_id"],
            "source_url": row["source_url"],
            "domain": row["domain"],
            "platform": row["platform"],
            "title": row["title"]
        },
        "evidence": row["evidence"],
        "limits": row["limits"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat()
    }), 200


def _format_vti_evidence_row(row):
    return {
        "proof_label": row["proof_label"],
        "source_record": {
            "source_id": row["source_id"],
            "source_url": row["source_url"],
            "domain": row["domain"],
            "platform": row["platform"],
            "title": row["title"]
        },
        "evidence": row["evidence"],
        "limits": row["limits"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat()
    }


@app.route("/vti/evidence/latest")
def vti_latest_evidence():
    try:
        with _db_connect() as conn:
            _ensure_vti_evidence_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT source_id, source_url, domain, platform, title,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM vti_smoke_evidence
                    ORDER BY updated_at DESC, created_at DESC
                    LIMIT 1;
                    """
                )
                row = cur.fetchone()
    except Exception as e:
        return jsonify({
            "status": "latest_retrieval_failed",
            "error": str(e)
        }), 503

    if not row:
        return jsonify({
            "status": "not_found",
            "message": "no VTI smoke evidence has been persisted yet"
        }), 404

    return jsonify({
        "status": "found",
        "service": APP_NAME,
        "mode": "vti_latest_evidence_retrieval",
        **_format_vti_evidence_row(row)
    }), 200


@app.route("/vti/evidence")
def vti_evidence_list():
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        return jsonify({
            "status": "invalid",
            "error": "limit must be an integer"
        }), 400

    limit = max(1, min(limit, 50))

    try:
        with _db_connect() as conn:
            _ensure_vti_evidence_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT source_id, source_url, domain, platform, title,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM vti_smoke_evidence
                    ORDER BY updated_at DESC, created_at DESC
                    LIMIT %s;
                    """,
                    (limit,)
                )
                rows = cur.fetchall()
    except Exception as e:
        return jsonify({
            "status": "list_retrieval_failed",
            "error": str(e)
        }), 503

    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "mode": "vti_evidence_list_retrieval",
        "proof_label": "VTI_PERSISTED_EVIDENCE_LIST_RETRIEVAL_PROVEN",
        "proof_object_schema": VTI_SMOKE_EVIDENCE_PROOF_OBJECT_SCHEMA,
        "count": len(rows),
        "limit": limit,
        "items": [_format_vti_evidence_row(row) for row in rows]
    }), 200


def _format_email_newsletter_proof_row(row):
    return {
        "proof_label": row["proof_label"],
        "newsletter_record": {
            "proof_id": row["proof_id"],
            "source_name": row["source_name"],
            "source_url": row["source_url"],
            "subject": row["subject"],
            "received_at": row["received_at"]
        },
        "evidence": row["evidence"],
        "limits": row["limits"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat()
    }


@app.route("/email/newsletter/status")
def email_newsletter_status():
    return jsonify({
        "status": "ready",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "capabilities": [
            "manual_newsletter_source_record_intake",
            "manual_newsletter_summary_hashing",
            "postgres_newsletter_proof_persistence",
            "proof_id_newsletter_retrieval",
            "latest_newsletter_proof_retrieval",
            "newsletter_proof_list_retrieval",
            "gmail_runtime_env_readiness_status"
        ],
        "proof_object_schema": EMAIL_NEWSLETTER_PROOF_OBJECT_SCHEMA,
        "proof_label": "EMAIL_NEWSLETTER_MANUAL_PROOF_ROUTE_AVAILABLE",
        "limits": [
            "no_gmail_connector_fetch_in_runtime_yet",
            "no_recurring_newsletter_sync_yet",
            "no_automatic_claim_extraction_yet",
            "no_automatic_research_verification_yet"
        ]
    }), 200


@app.route("/email/newsletter/gmail/status")
def email_newsletter_gmail_status():
    required_env = [_env_status(name, True) for name in GMAIL_NEWSLETTER_REQUIRED_ENV]
    optional_env = [_env_status(name, False) for name in GMAIL_NEWSLETTER_OPTIONAL_ENV]
    required_configured = all(item["configured"] for item in required_env)

    return jsonify({
        "status": "ready_for_fetch_credentials_present" if required_configured else "pending_credentials",
        "service": APP_NAME,
        "env": APP_ENV,
        "version": APP_VERSION,
        "mode": "gmail_newsletter_readiness_status",
        "proof_label": "GMAIL_NEWSLETTER_READINESS_ROUTE_PROVEN",
        "proof_object_schema": GMAIL_NEWSLETTER_READINESS_PROOF_OBJECT_SCHEMA,
        "required_env": required_env,
        "optional_env": optional_env,
        "required_scopes": GMAIL_NEWSLETTER_REQUIRED_SCOPES,
        "evidence": {
            "env_names_declared": True,
            "required_scope_declared": True,
            "secret_values_hidden": True,
            "runtime_credentials_configured": required_configured
        },
        "limits": {
            "gmail_fetch_attempted": False,
            "gmail_credentials_validated": False,
            "gmail_messages_read": False,
            "recurring_sync_enabled": False
        },
        "next_gate": (
            "add Gmail OAuth credentials to the runtime secret store, then add a read-only Gmail fetch smoke route"
            if not required_configured
            else "add a read-only Gmail fetch smoke route and verify OAuth token refresh without exposing message content"
        )
    }), 200


@app.route("/email/newsletter/smoke", methods=["POST"])
def email_newsletter_smoke():
    payload = request.get_json(silent=True) or {}
    source_name = str(payload.get("source_name", "")).strip()
    source_url = str(payload.get("source_url", "")).strip()
    subject = str(payload.get("subject", "")).strip()
    received_at = str(payload.get("received_at", "")).strip()
    summary = str(payload.get("summary", "")).strip()
    tags = payload.get("tags", [])

    if not source_name:
        return jsonify({
            "status": "invalid",
            "error": "source_name is required"
        }), 400
    if not subject:
        return jsonify({
            "status": "invalid",
            "error": "subject is required"
        }), 400
    if not isinstance(tags, list):
        return jsonify({
            "status": "invalid",
            "error": "tags must be a list"
        }), 400

    clean_tags = [str(tag).strip() for tag in tags if str(tag).strip()]
    proof_id = hashlib.sha256(
        "|".join([source_name, source_url, subject, summary[:2000]]).encode("utf-8")
    ).hexdigest()[:24]
    proof_label = "EMAIL_NEWSLETTER_MANUAL_INTAKE_SMOKE_PROVEN"
    evidence = {
        "manual_intake_captured": True,
        "summary_captured": bool(summary),
        "tags": clean_tags,
        "summary_sha256": _text_digest(summary),
        "persisted_at_utc": datetime.now(timezone.utc).isoformat()
    }
    limits = {
        "gmail_connector_fetch": False,
        "recurring_newsletter_sync": False,
        "automatic_claim_extraction": False,
        "automatic_research_verification": False
    }

    try:
        with _db_connect() as conn:
            _ensure_email_newsletter_proof_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO email_newsletter_proof (
                        proof_id, source_name, source_url, subject, received_at,
                        proof_label, evidence, limits
                    )
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
                    """,
                    (
                        proof_id,
                        source_name,
                        source_url or None,
                        subject,
                        received_at or None,
                        proof_label,
                        Jsonb(evidence),
                        Jsonb(limits)
                    )
                )
    except Exception as e:
        return jsonify({
            "status": "persistence_failed",
            "error": str(e),
            "newsletter_record": {
                "proof_id": proof_id,
                "source_name": source_name,
                "source_url": source_url or None,
                "subject": subject,
                "received_at": received_at or None
            },
            "evidence": evidence,
            "limits": limits
        }), 503

    return jsonify({
        "status": "accepted",
        "service": APP_NAME,
        "mode": "email_newsletter_manual_smoke",
        "proof_label": proof_label,
        "persistence": "stored",
        "retrieval_url": f"/email/newsletter/proof/{proof_id}",
        "newsletter_record": {
            "proof_id": proof_id,
            "source_name": source_name,
            "source_url": source_url or None,
            "subject": subject,
            "received_at": received_at or None
        },
        "evidence": evidence,
        "limits": limits
    }), 200


@app.route("/email/newsletter/proof/latest")
def email_newsletter_latest_proof():
    try:
        with _db_connect() as conn:
            _ensure_email_newsletter_proof_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT proof_id, source_name, source_url, subject, received_at,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM email_newsletter_proof
                    ORDER BY updated_at DESC, created_at DESC
                    LIMIT 1;
                    """
                )
                row = cur.fetchone()
    except Exception as e:
        return jsonify({
            "status": "latest_retrieval_failed",
            "error": str(e)
        }), 503

    if not row:
        return jsonify({
            "status": "not_found",
            "message": "no email/newsletter proof has been persisted yet"
        }), 404

    return jsonify({
        "status": "found",
        "service": APP_NAME,
        "mode": "email_newsletter_latest_proof_retrieval",
        **_format_email_newsletter_proof_row(row)
    }), 200


@app.route("/email/newsletter/proof/<proof_id>")
def email_newsletter_proof(proof_id):
    clean_proof_id = proof_id.strip()
    if not clean_proof_id:
        return jsonify({
            "status": "invalid",
            "error": "proof_id is required"
        }), 400

    try:
        with _db_connect() as conn:
            _ensure_email_newsletter_proof_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT proof_id, source_name, source_url, subject, received_at,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM email_newsletter_proof
                    WHERE proof_id = %s;
                    """,
                    (clean_proof_id,)
                )
                row = cur.fetchone()
    except Exception as e:
        return jsonify({
            "status": "retrieval_failed",
            "error": str(e)
        }), 503

    if not row:
        return jsonify({
            "status": "not_found",
            "proof_id": clean_proof_id
        }), 404

    return jsonify({
        "status": "found",
        "service": APP_NAME,
        "mode": "email_newsletter_proof_id_retrieval",
        **_format_email_newsletter_proof_row(row)
    }), 200


@app.route("/email/newsletter/proof")
def email_newsletter_proof_list():
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        return jsonify({
            "status": "invalid",
            "error": "limit must be an integer"
        }), 400

    limit = max(1, min(limit, 50))

    try:
        with _db_connect() as conn:
            _ensure_email_newsletter_proof_table(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT proof_id, source_name, source_url, subject, received_at,
                           proof_label, evidence, limits, created_at, updated_at
                    FROM email_newsletter_proof
                    ORDER BY updated_at DESC, created_at DESC
                    LIMIT %s;
                    """,
                    (limit,)
                )
                rows = cur.fetchall()
    except Exception as e:
        return jsonify({
            "status": "list_retrieval_failed",
            "error": str(e)
        }), 503

    return jsonify({
        "status": "ok",
        "service": APP_NAME,
        "mode": "email_newsletter_proof_list_retrieval",
        "proof_label": "EMAIL_NEWSLETTER_PERSISTED_PROOF_LIST_RETRIEVAL_PROVEN",
        "proof_object_schema": EMAIL_NEWSLETTER_PROOF_OBJECT_SCHEMA,
        "count": len(rows),
        "limit": limit,
        "items": [_format_email_newsletter_proof_row(row) for row in rows]
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
