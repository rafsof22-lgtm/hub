import hashlib
import os
from urllib.parse import urlparse

from flask import Flask, jsonify, request
import psycopg
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


def _text_digest(value):
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
        conn = psycopg.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            connect_timeout=3
        )
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
            "email_newsletter_ingestion": "partial_live_access_not_recurring_proven"
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
            "source_record_hashing"
        ],
        "proof_label": "VTI_SMOKE_ROUTE_AVAILABLE",
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

    return jsonify({
        "status": "accepted",
        "service": APP_NAME,
        "mode": "vti_smoke",
        "proof_label": "VTI_COPIED_LINK_TRANSCRIPT_OCR_SMOKE_PROVEN",
        "source_record": {
            "source_id": source_id,
            "source_url": source_url,
            "domain": parsed.netloc,
            "platform": platform or parsed.netloc,
            "title": title or None
        },
        "evidence": {
            "copied_link_captured": True,
            "manual_transcript_captured": bool(transcript),
            "ocr_text_captured": bool(ocr_text),
            "transcript_word_count": len(transcript_words),
            "ocr_word_count": len(ocr_words),
            "transcript_sha256": _text_digest(transcript),
            "ocr_text_sha256": _text_digest(ocr_text)
        },
        "limits": {
            "automatic_media_fetch": False,
            "automatic_caption_fetch": False,
            "automatic_ocr_worker": False,
            "claim_verification_worker": False
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
