from __future__ import annotations

import json
import os
import socket
import time
import traceback
from datetime import datetime, timezone

import psycopg
import redis
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

QUEUE_NAME = os.getenv("WORKER_QUEUE", "jarvis:jobs")
PROCESSING_QUEUE = os.getenv("WORKER_PROCESSING_QUEUE", "jarvis:jobs:processing")
DLQ_NAME = os.getenv("WORKER_DLQ", "jarvis:jobs:dlq")
HEARTBEAT_SECONDS = max(5, int(os.getenv("WORKER_HEARTBEAT_SECONDS", "15")))
MAX_RETRIES = max(0, int(os.getenv("WORKER_MAX_RETRIES", "3")))
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
WORKER_ID = os.getenv("WORKER_ID", f"{socket.gethostname()}-{os.getpid()}")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def db_connect():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "xrp_hbar_apex"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me"),
        connect_timeout=10,
        row_factory=dict_row,
    )


def ensure_tables(conn) -> None:
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
            """
        )


def heartbeat(last_job_id: str | None = None, status: str = "ready") -> None:
    with db_connect() as conn:
        ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO worker_heartbeat (worker_id, status, queue_name, last_job_id, metadata)
                VALUES (%s, %s, %s, %s, %s::jsonb)
                ON CONFLICT (worker_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    queue_name = EXCLUDED.queue_name,
                    last_job_id = EXCLUDED.last_job_id,
                    metadata = EXCLUDED.metadata,
                    observed_at = now();
                """,
                (
                    WORKER_ID,
                    status,
                    QUEUE_NAME,
                    last_job_id,
                    Jsonb({"max_retries": MAX_RETRIES, "heartbeat_seconds": HEARTBEAT_SECONDS}),
                ),
            )
        conn.commit()


def execute(job: dict) -> dict:
    job_type = str(job.get("job_type") or "noop")
    payload = job.get("payload") if isinstance(job.get("payload"), dict) else {}
    if job_type == "noop":
        return {"ok": True, "echo": payload, "processed_at": now()}
    if job_type == "checkpoint":
        return {"ok": True, "checkpoint": payload, "processed_at": now()}
    raise ValueError(f"unsupported job_type: {job_type}")


def persist_status(job: dict, status: str, *, result: dict | None = None, error: str | None = None) -> None:
    job_id = str(job["job_id"])
    with db_connect() as conn:
        ensure_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO worker_job (
                    job_id, job_type, status, payload, result, retry_count, max_retries,
                    last_error, worker_id, started_at, completed_at
                ) VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s, %s,
                    CASE WHEN %s IN ('processing','completed','failed','dead_letter') THEN now() ELSE NULL END,
                    CASE WHEN %s IN ('completed','dead_letter') THEN now() ELSE NULL END)
                ON CONFLICT (job_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    result = EXCLUDED.result,
                    retry_count = EXCLUDED.retry_count,
                    max_retries = EXCLUDED.max_retries,
                    last_error = EXCLUDED.last_error,
                    worker_id = EXCLUDED.worker_id,
                    started_at = COALESCE(worker_job.started_at, EXCLUDED.started_at),
                    completed_at = EXCLUDED.completed_at,
                    updated_at = now();
                """,
                (
                    job_id,
                    str(job.get("job_type") or "noop"),
                    status,
                    Jsonb(job.get("payload") if isinstance(job.get("payload"), dict) else {}),
                    Jsonb(result or {}),
                    int(job.get("retry_count") or 0),
                    int(job.get("max_retries") or MAX_RETRIES),
                    error,
                    WORKER_ID,
                    status,
                    status,
                ),
            )
        conn.commit()


def run() -> None:
    client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=10)
    client.ping()
    heartbeat(status="ready")
    last_heartbeat = 0.0
    while True:
        current = time.monotonic()
        if current - last_heartbeat >= HEARTBEAT_SECONDS:
            heartbeat(status="ready")
            last_heartbeat = current
        raw = client.brpoplpush(QUEUE_NAME, PROCESSING_QUEUE, timeout=5)
        if raw is None:
            continue
        job: dict | None = None
        try:
            job = json.loads(raw)
            if not isinstance(job, dict) or not job.get("job_id"):
                raise ValueError("job must be an object with job_id")
            persist_status(job, "processing")
            result = execute(job)
            persist_status(job, "completed", result=result)
            client.lrem(PROCESSING_QUEUE, 1, raw)
            heartbeat(str(job["job_id"]), "ready")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            if job is None:
                client.lrem(PROCESSING_QUEUE, 1, raw)
                client.lpush(DLQ_NAME, json.dumps({"raw": raw, "error": error, "failed_at": now()}))
                continue
            job["retry_count"] = int(job.get("retry_count") or 0) + 1
            max_retries = int(job.get("max_retries") or MAX_RETRIES)
            if job["retry_count"] <= max_retries:
                persist_status(job, "retrying", error=error)
                client.lrem(PROCESSING_QUEUE, 1, raw)
                client.lpush(QUEUE_NAME, json.dumps(job, sort_keys=True))
            else:
                persist_status(job, "dead_letter", error=error, result={"traceback": traceback.format_exc(limit=5)})
                client.lrem(PROCESSING_QUEUE, 1, raw)
                client.lpush(DLQ_NAME, json.dumps(job, sort_keys=True))


if __name__ == "__main__":
    run()
