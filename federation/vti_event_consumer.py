from __future__ import annotations

import hashlib
import hmac
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "1.0.0"
EXPECTED_PRODUCER = "vti-evidence-service"
EXPECTED_CONSUMER = "xrp-hbar-hub-runtime"
ALLOWED_EVENT_TYPES = {
    "research.requested", "research.completed", "research.failed",
    "transcript.requested", "transcript.completed", "evidence.created",
    "deployment.status", "health.status", "alert.created",
    "discrepancy.created", "incident.created", "cost.recorded",
}
ALLOWED_STATUSES = {
    "PENDING_INGEST", "SPEC_ONLY", "BACKLOGGED", "SCAFFOLDED",
    "IMPLEMENTED_NOT_INTEGRATED", "INTEGRATED_STAGING", "DEPLOYED_UNVERIFIED",
    "DONE_VERIFIED", "WAIVED", "BLOCKED",
}
REQUIRED_FIELDS = {
    "event_id", "event_type", "schema_version", "producer", "consumer",
    "occurred_at", "correlation_id", "idempotency_key", "source_refs",
    "approval_state", "payload", "evidence_refs", "retry_count", "status",
}


class EventValidationError(ValueError):
    pass


class EventAuthenticationError(ValueError):
    pass


def canonical_bytes(event: Mapping[str, Any]) -> bytes:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign_event(event: Mapping[str, Any], secret: str) -> str:
    if len(secret) < 32:
        raise EventAuthenticationError("signing secret must contain at least 32 characters")
    return hmac.new(secret.encode("utf-8"), canonical_bytes(event), hashlib.sha256).hexdigest()


def verify_signature(event: Mapping[str, Any], signature: str, secret: str) -> None:
    expected = sign_event(event, secret)
    if not signature or not hmac.compare_digest(expected, signature):
        raise EventAuthenticationError("invalid event signature")


def validate_event(event: Mapping[str, Any]) -> None:
    missing = sorted(REQUIRED_FIELDS.difference(event))
    if missing:
        raise EventValidationError(f"missing fields: {', '.join(missing)}")
    if event["schema_version"] != SCHEMA_VERSION:
        raise EventValidationError("unsupported schema_version")
    if event["producer"] != EXPECTED_PRODUCER:
        raise EventValidationError("unexpected producer")
    if event["consumer"] != EXPECTED_CONSUMER:
        raise EventValidationError("unexpected consumer")
    if event["event_type"] not in ALLOWED_EVENT_TYPES:
        raise EventValidationError("unsupported event_type")
    if event["status"] not in ALLOWED_STATUSES:
        raise EventValidationError("invalid governed status")
    if not isinstance(event["payload"], Mapping):
        raise EventValidationError("payload must be an object")
    for field in ("source_refs", "evidence_refs"):
        if not isinstance(event[field], list):
            raise EventValidationError(f"{field} must be an array")
    for field in ("event_id", "correlation_id", "idempotency_key"):
        if not isinstance(event[field], str) or not event[field].strip():
            raise EventValidationError(f"{field} must be non-empty")
    if int(event["retry_count"]) < 0:
        raise EventValidationError("retry_count must be non-negative")


@dataclass(frozen=True)
class EventAck:
    accepted: bool
    duplicate: bool
    event_id: str
    correlation_id: str
    status: str


class VtiEventConsumer:
    def __init__(self, database_path: str | Path, signing_secret: str, max_attempts: int = 3):
        self.database_path = str(database_path)
        self.signing_secret = signing_secret
        self.max_attempts = max(1, max_attempts)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS vti_federation_events (
                    event_id TEXT PRIMARY KEY,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    correlation_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    raw_event TEXT NOT NULL,
                    payload_hash TEXT NOT NULL,
                    processing_status TEXT NOT NULL DEFAULT 'accepted',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    received_at TEXT NOT NULL,
                    processed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_vti_events_correlation
                    ON vti_federation_events(correlation_id, received_at);
                CREATE TABLE IF NOT EXISTS vti_event_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL REFERENCES vti_federation_events(event_id) ON DELETE CASCADE,
                    attempt_number INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    error_code TEXT,
                    occurred_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS vti_event_dead_letters (
                    event_id TEXT PRIMARY KEY REFERENCES vti_federation_events(event_id) ON DELETE CASCADE,
                    reason TEXT NOT NULL,
                    raw_event TEXT NOT NULL,
                    failed_at TEXT NOT NULL,
                    replay_count INTEGER NOT NULL DEFAULT 0
                );
                """
            )

    def ingest(self, event: Mapping[str, Any], signature: str) -> EventAck:
        verify_signature(event, signature, self.signing_secret)
        validate_event(event)
        raw = canonical_bytes(event).decode("utf-8")
        payload_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            existing = db.execute(
                "SELECT event_id, correlation_id, processing_status FROM vti_federation_events WHERE idempotency_key = ?",
                (event["idempotency_key"],),
            ).fetchone()
            if existing:
                return EventAck(True, True, existing["event_id"], existing["correlation_id"], existing["processing_status"])
            db.execute(
                """INSERT INTO vti_federation_events
                (event_id,idempotency_key,correlation_id,event_type,raw_event,payload_hash,processing_status,received_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (event["event_id"], event["idempotency_key"], event["correlation_id"], event["event_type"], raw, payload_hash, "accepted", now),
            )
            db.execute(
                "INSERT INTO vti_event_attempts(event_id,attempt_number,status,occurred_at) VALUES (?,?,?,?)",
                (event["event_id"], 0, "accepted", now),
            )
        return EventAck(True, False, event["event_id"], event["correlation_id"], "accepted")

    def mark_processed(self, event_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            updated = db.execute(
                "UPDATE vti_federation_events SET processing_status='processed', processed_at=?, last_error=NULL WHERE event_id=?",
                (now, event_id),
            ).rowcount
            if not updated:
                raise KeyError(event_id)
            attempts = db.execute("SELECT attempts FROM vti_federation_events WHERE event_id=?", (event_id,)).fetchone()[0]
            db.execute(
                "INSERT INTO vti_event_attempts(event_id,attempt_number,status,occurred_at) VALUES (?,?,?,?)",
                (event_id, attempts, "processed", now),
            )

    def mark_failed(self, event_id: str, error_code: str) -> str:
        safe_error = str(error_code)[:500]
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as db:
            row = db.execute("SELECT attempts, raw_event FROM vti_federation_events WHERE event_id=?", (event_id,)).fetchone()
            if not row:
                raise KeyError(event_id)
            attempt = int(row["attempts"]) + 1
            status = "dead_letter" if attempt >= self.max_attempts else "retry_pending"
            db.execute(
                "UPDATE vti_federation_events SET attempts=?, processing_status=?, last_error=? WHERE event_id=?",
                (attempt, status, safe_error, event_id),
            )
            db.execute(
                "INSERT INTO vti_event_attempts(event_id,attempt_number,status,error_code,occurred_at) VALUES (?,?,?,?,?)",
                (event_id, attempt, status, safe_error, now),
            )
            if status == "dead_letter":
                db.execute(
                    "INSERT OR REPLACE INTO vti_event_dead_letters(event_id,reason,raw_event,failed_at,replay_count) VALUES (?,?,?,?,COALESCE((SELECT replay_count FROM vti_event_dead_letters WHERE event_id=?),0))",
                    (event_id, safe_error, row["raw_event"], now, event_id),
                )
            return status

    def replay_dead_letter(self, event_id: str) -> None:
        with self._connect() as db:
            row = db.execute("SELECT replay_count FROM vti_event_dead_letters WHERE event_id=?", (event_id,)).fetchone()
            if not row:
                raise KeyError(event_id)
            db.execute("UPDATE vti_event_dead_letters SET replay_count=replay_count+1 WHERE event_id=?", (event_id,))
            db.execute("UPDATE vti_federation_events SET attempts=0, processing_status='retry_pending', last_error=NULL WHERE event_id=?", (event_id,))

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM vti_federation_events WHERE event_id=?", (event_id,)).fetchone()
            return dict(row) if row else None
