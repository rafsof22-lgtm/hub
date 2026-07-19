from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone

import redis
from flask import request
from psycopg.types.json import Jsonb

from app import app, _db_connect, _json_response

QUEUE_NAME = os.getenv("WORKER_QUEUE", "jarvis:jobs")
PROCESSING_QUEUE = os.getenv("WORKER_PROCESSING_QUEUE", "jarvis:jobs:processing")
DLQ_NAME = os.getenv("WORKER_DLQ", "jarvis:jobs:dlq")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
MAX_RETRIES = max(0, int(os.getenv("WORKER_MAX_RETRIES", "3")))


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_id(job_type: str, payload: dict) -> str:
    material = json.dumps({"job_type": job_type, "payload": payload}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{material}|{_now()}".encode("utf-8")).hexdigest()[:24]


def _redis():
    return redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)


def _ensure_runtime_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS worker_job (
                job_id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                result JSONB NOT NULL DEFAULT '{}'::jsonb,
                retry_count INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 3,
                last_error TEXT,
                worker_id TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                started_at TIMESTAMPTZ,
                completed_at TIMESTAMPTZ,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS worker_heartbeat (
                worker_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                queue_name TEXT NOT NULL,
                last_job_id TEXT,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                observed_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS schema_migration (
                migration_name TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )


def _format_job(row: dict) -> dict:
    return {
        "job_id": row["job_id"],
        "job_type": row["job_type"],
        "status": row["status"],
        "payload": row["payload"],
        "result": row["result"],
        "retry_count": row["retry_count"],
        "max_retries": row["max_retries"],
        "last_error": row["last_error"],
        "worker_id": row["worker_id"],
        "created_at": row["created_at"].isoformat(),
        "started_at": row["started_at"].isoformat() if row["started_at"] else None,
        "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
        "updated_at": row["updated_at"].isoformat(),
    }


@app.get("/worker/status")
def worker_status():
    client = _redis()
    try:
        queue_depth = client.llen(QUEUE_NAME)
        processing_depth = client.llen(PROCESSING_QUEUE)
        dlq_depth = client.llen(DLQ_NAME)
    except Exception as exc:
        return _json_response({"status": "not_ready", "error": str(exc)}, 503)
    with _db_connect() as conn:
        _ensure_runtime_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM worker_heartbeat ORDER BY observed_at DESC LIMIT 1;"
            )
            heartbeat = cur.fetchone()
    heartbeat_payload = None
    if heartbeat:
        heartbeat_payload = {
            "worker_id": heartbeat["worker_id"],
            "status": heartbeat["status"],
            "queue_name": heartbeat["queue_name"],
            "last_job_id": heartbeat["last_job_id"],
            "metadata": heartbeat["metadata"],
            "observed_at": heartbeat["observed_at"].isoformat(),
        }
    ready = heartbeat_payload is not None
    return _json_response(
        {
            "status": "ready" if ready else "starting",
            "proof_label": "RELIABLE_WORKER_RUNTIME_STATUS",
            "queue": {
                "name": QUEUE_NAME,
                "depth": queue_depth,
                "processing_depth": processing_depth,
                "dead_letter_depth": dlq_depth,
            },
            "heartbeat": heartbeat_payload,
            "limits": {"external_side_effect_jobs_enabled": False, "supported_job_types": ["noop", "checkpoint"]},
        },
        200 if ready else 503,
    )


@app.post("/worker/jobs")
def enqueue_job():
    payload = request.get_json(silent=True) or {}
    job_type = str(payload.get("job_type") or "noop").strip()
    job_payload = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
    if job_type not in {"noop", "checkpoint"}:
        return _json_response({"status": "invalid", "error": "unsupported job_type"}, 400)
    try:
        max_retries = int(payload.get("max_retries", MAX_RETRIES))
    except (TypeError, ValueError):
        return _json_response({"status": "invalid", "error": "max_retries must be an integer"}, 400)
    max_retries = max(0, min(max_retries, 10))
    job = {
        "job_id": _job_id(job_type, job_payload),
        "job_type": job_type,
        "payload": job_payload,
        "retry_count": 0,
        "max_retries": max_retries,
        "enqueued_at": _now(),
    }
    with _db_connect() as conn:
        _ensure_runtime_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO worker_job (job_id, job_type, status, payload, max_retries)
                VALUES (%s, %s, 'queued', %s::jsonb, %s);
                """,
                (job["job_id"], job_type, Jsonb(job_payload), max_retries),
            )
        conn.commit()
    _redis().lpush(QUEUE_NAME, json.dumps(job, sort_keys=True))
    return _json_response(
        {
            "status": "accepted",
            "proof_label": "RELIABLE_WORKER_JOB_ENQUEUED",
            "job_id": job["job_id"],
            "retrieval_url": f"/worker/jobs/{job['job_id']}",
            "limits": {"external_side_effects": False},
        },
        202,
    )


@app.get("/worker/jobs/<job_id>")
def get_job(job_id: str):
    with _db_connect() as conn:
        _ensure_runtime_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM worker_job WHERE job_id = %s;", (job_id.strip(),))
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "job_id": job_id}, 404)
    return _json_response({"status": "found", "job": _format_job(row)})


@app.get("/migrations/status")
def migration_status():
    with _db_connect() as conn:
        _ensure_runtime_tables(conn)
        with conn.cursor() as cur:
            cur.execute("SELECT migration_name, sha256, applied_at FROM schema_migration ORDER BY migration_name;")
            rows = cur.fetchall()
    return _json_response(
        {
            "status": "ready" if rows else "pending",
            "proof_label": "HASH_LOCKED_MIGRATION_LEDGER_STATUS",
            "count": len(rows),
            "migrations": [
                {"migration_name": row["migration_name"], "sha256": row["sha256"], "applied_at": row["applied_at"].isoformat()}
                for row in rows
            ],
        },
        200 if rows else 503,
    )


@app.get("/outbound/status")
def outbound_status():
    return _json_response(
        {
            "status": "safe_disabled",
            "proof_label": "OUTBOUND_EXECUTION_FAIL_CLOSED",
            "external_fetch_enabled": False,
            "required_before_enable": [
                "DNS rebinding resistant resolution",
                "private and reserved network blocking",
                "ownership or allowlist validation",
                "per-source quotas",
                "audit trail",
                "explicit approval ticket",
            ],
        }
    )
