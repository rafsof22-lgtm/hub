from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

from flask import request
from psycopg.types.json import Jsonb

from app import app, _db_connect, _json_response

MAX_BODY_BYTES = 1_000_000
MAX_ITEMS = 500
MAX_TEXT_CHARS = 900_000
TRACKING_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r'["\']?(?:api[_-]?key|client[_-]?secret|refresh[_-]?token|private[_-]?key|seed[_-]?phrase)["\']?\s*[:=]\s*["\']?[^\s,;"\']{8,}',
        re.I,
    ),
]
ALLOWED_STATES = {
    "DISCOVERED",
    "NORMALISED",
    "OFFICIAL_SOURCE_RESOLVED",
    "VERIFIED_CANDIDATE",
    "QUARANTINED",
    "SANDBOX_READY",
    "SANDBOX_PROVEN",
    "APPROVAL_REQUIRED",
    "CANARY",
    "APPROVED_PRODUCTION",
    "WATCHLIST",
    "DEPRECATED",
    "REVOKED",
    "REJECTED",
}
TRANSITIONS = {
    "DISCOVERED": {"NORMALISED", "REJECTED"},
    "NORMALISED": {"OFFICIAL_SOURCE_RESOLVED", "QUARANTINED", "REJECTED"},
    "OFFICIAL_SOURCE_RESOLVED": {"VERIFIED_CANDIDATE", "QUARANTINED", "REJECTED"},
    "VERIFIED_CANDIDATE": {"QUARANTINED", "SANDBOX_READY", "REJECTED"},
    "QUARANTINED": {"SANDBOX_READY", "REJECTED", "WATCHLIST"},
    "SANDBOX_READY": {"SANDBOX_PROVEN", "REJECTED"},
    "SANDBOX_PROVEN": {"APPROVAL_REQUIRED", "REJECTED"},
    "APPROVAL_REQUIRED": {"CANARY", "REJECTED"},
    "CANARY": {"APPROVED_PRODUCTION", "WATCHLIST", "REVOKED"},
    "APPROVED_PRODUCTION": {"WATCHLIST", "DEPRECATED", "REVOKED"},
    "WATCHLIST": {"SANDBOX_READY", "DEPRECATED", "REVOKED", "REJECTED"},
    "DEPRECATED": {"REVOKED"},
    "REJECTED": set(),
    "REVOKED": set(),
}
REASON_REQUIRED_STATES = {
    "APPROVAL_REQUIRED",
    "CANARY",
    "APPROVED_PRODUCTION",
    "WATCHLIST",
    "DEPRECATED",
    "REVOKED",
    "REJECTED",
}
APPROVAL_REFERENCE_REQUIRED_STATES = {"CANARY", "APPROVED_PRODUCTION"}
ROLLBACK_REFERENCE_REQUIRED_STATES = {"CANARY", "APPROVED_PRODUCTION"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonicalize_url(value: str) -> str:
    parsed = urlsplit(str(value or "").strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("only absolute http/https URLs are accepted")
    scheme = parsed.scheme.lower()
    host = parsed.hostname.rstrip(".").lower()
    port = parsed.port
    netloc = host
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    query = urlencode(
        sorted(
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key.lower() not in TRACKING_KEYS
        )
    )
    return urlunsplit((scheme, netloc, parsed.path or "/", query, ""))


def _candidate_id(url: str, source: str, tier: int) -> str:
    return hashlib.sha256(f"{url}|{source}|{tier}".encode("utf-8")).hexdigest()[:24]


def _decision_id(candidate_id: str, current: str, target: str, observed_at: str) -> str:
    return hashlib.sha256(
        f"{candidate_id}|{current}|{target}|{observed_at}".encode("utf-8")
    ).hexdigest()[:24]


def _contains_secret(text: str) -> bool:
    sample = text[:MAX_TEXT_CHARS]
    return any(pattern.search(sample) for pattern in SECRET_PATTERNS)


def _bounded_text(payload: dict, key: str) -> str:
    value = str(payload.get(key, ""))
    if len(value) > MAX_TEXT_CHARS:
        raise ValueError(f"{key} exceeds maximum size")
    if _contains_secret(value):
        raise ValueError(f"{key} appears to contain secret material")
    return value


def _validate_transition_request(
    current: str,
    target: str,
    reason: str,
    approval_reference: str,
    rollback_reference: str,
) -> str | None:
    if target not in ALLOWED_STATES:
        return "unknown target_state"
    if target not in TRANSITIONS.get(current, set()):
        return f"transition not allowed: {current} -> {target}"
    if target in REASON_REQUIRED_STATES and not reason:
        return f"reason is required for transition to {target}"
    if target in APPROVAL_REFERENCE_REQUIRED_STATES and not approval_reference:
        return f"approval_reference is required for transition to {target}"
    if target in ROLLBACK_REFERENCE_REQUIRED_STATES and not rollback_reference:
        return f"rollback_reference is required for transition to {target}"
    return None


class _BookmarkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[tuple[str, str]] = []
        self.href: str | None = None
        self.title: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            values = {str(key).lower(): value for key, value in attrs}
            if values.get("href"):
                self.href = str(values["href"]).strip()
                self.title = []

    def handle_data(self, data):
        if self.href is not None:
            self.title.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href is not None:
            self.items.append((self.href, "".join(self.title).strip()))
            self.href = None
            self.title = []


def _parse_candidates(kind: str, text: str, source: str, tier: int) -> list[dict]:
    raw: list[tuple[str, str]] = []
    if kind == "bookmarks":
        parser = _BookmarkParser()
        parser.feed(text)
        raw = parser.items
    elif kind == "opml":
        root = ET.fromstring(text)
        for node in root.findall(".//outline"):
            url = node.attrib.get("xmlUrl") or node.attrib.get("htmlUrl")
            if url:
                raw.append((url, node.attrib.get("title") or node.attrib.get("text") or ""))
    elif kind == "feed":
        root = ET.fromstring(text)
        for item in root.findall(".//item"):
            link = item.findtext("link")
            if link:
                raw.append((link, item.findtext("title") or ""))
        atom_ns = "{http://www.w3.org/2005/Atom}"
        for entry in root.findall(f".//{atom_ns}entry"):
            link = None
            for node in entry.findall(f"{atom_ns}link"):
                if node.attrib.get("rel", "alternate") == "alternate" and node.attrib.get("href"):
                    link = node.attrib["href"]
                    break
            if link:
                raw.append((link, entry.findtext(f"{atom_ns}title") or ""))
    elif kind == "json":
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON import must be a list")
        if len(data) > MAX_ITEMS:
            raise ValueError("JSON import exceeds maximum item count")
        for item in data:
            if isinstance(item, str):
                raw.append((item, ""))
            elif isinstance(item, dict):
                raw.append(
                    (
                        str(item.get("url") or item.get("source_url") or ""),
                        str(item.get("title") or ""),
                    )
                )
    else:
        raise ValueError("unsupported import kind")

    result: list[dict] = []
    seen: set[str] = set()
    for url, title in raw[:MAX_ITEMS]:
        try:
            canonical = _canonicalize_url(url)
        except ValueError:
            continue
        if canonical in seen:
            continue
        seen.add(canonical)
        result.append(
            {
                "candidate_id": _candidate_id(canonical, source, tier),
                "source_url": canonical,
                "title": title[:300],
                "discovery_source": source[:120],
                "discovery_tier": tier,
                "state": "NORMALISED",
            }
        )
    return result


def _ensure_source_tables(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS source_candidate (
                candidate_id TEXT PRIMARY KEY,
                source_url TEXT NOT NULL,
                canonical_url TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                discovery_source TEXT NOT NULL,
                discovery_tier INTEGER NOT NULL CHECK (discovery_tier BETWEEN 0 AND 3),
                state TEXT NOT NULL,
                decision_reason TEXT,
                metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )
        cur.execute(
            "ALTER TABLE source_candidate ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;"
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS integration_decision (
                decision_id TEXT PRIMARY KEY,
                candidate_id TEXT NOT NULL REFERENCES source_candidate(candidate_id) ON DELETE CASCADE,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                approval_reference TEXT,
                rollback_reference TEXT,
                evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
                decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )
        cur.execute("CREATE INDEX IF NOT EXISTS source_candidate_state_idx ON source_candidate(state);")
        cur.execute("CREATE INDEX IF NOT EXISTS source_candidate_url_idx ON source_candidate(canonical_url);")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS integration_decision_candidate_idx ON integration_decision(candidate_id, decided_at DESC);"
        )


def _format_row(row: dict) -> dict:
    return {
        "candidate_id": row["candidate_id"],
        "source_url": row["source_url"],
        "canonical_url": row["canonical_url"],
        "title": row["title"],
        "discovery_source": row["discovery_source"],
        "discovery_tier": row["discovery_tier"],
        "state": row["state"],
        "decision_reason": row["decision_reason"],
        "metadata": row["metadata"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }


@app.before_request
def source_discovery_request_guard():
    if not request.path.startswith("/source-discovery/"):
        return None
    if request.content_length and request.content_length > MAX_BODY_BYTES:
        return _json_response(
            {"status": "invalid", "error": "request body exceeds maximum size"},
            413,
        )
    return None


@app.get("/source-discovery/status")
def source_discovery_status():
    return _json_response(
        {
            "status": "ready",
            "proof_label": "SOURCE_DISCOVERY_RUNTIME_ROUTES_REGISTERED",
            "capabilities": [
                "bounded_import",
                "postgres_persistence",
                "read_only_retrieval",
                "governed_transition",
                "approval_and_rollback_evidence",
            ],
            "limits": {
                "outbound_fetch": False,
                "automatic_promotion": False,
                "production_credentials": False,
                "max_body_bytes": MAX_BODY_BYTES,
                "max_items": MAX_ITEMS,
            },
        }
    )


@app.post("/source-discovery/import/<kind>")
def source_discovery_import(kind: str):
    payload = request.get_json(silent=True) or {}
    try:
        text = _bounded_text(payload, "content")
        source = str(payload.get("discovery_source") or f"runtime_{kind}").strip()[:120]
        tier = int(payload.get("discovery_tier", 2))
        if tier < 0 or tier > 3:
            raise ValueError("discovery_tier must be between 0 and 3")
        candidates = _parse_candidates(kind, text, source, tier)
    except (ValueError, ET.ParseError, json.JSONDecodeError) as exc:
        return _json_response({"status": "invalid", "error": str(exc)}, 400)

    with _db_connect() as conn:
        _ensure_source_tables(conn)
        with conn.cursor() as cur:
            for item in candidates:
                metadata = {
                    "import_kind": kind,
                    "imported_at": _now(),
                    "automatic_promotion_allowed": False,
                }
                cur.execute(
                    """
                    INSERT INTO source_candidate (
                        candidate_id, source_url, canonical_url, title, discovery_source,
                        discovery_tier, state, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
                    ON CONFLICT (candidate_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        metadata = source_candidate.metadata || EXCLUDED.metadata,
                        updated_at = now();
                    """,
                    (
                        item["candidate_id"],
                        item["source_url"],
                        item["source_url"],
                        item["title"],
                        item["discovery_source"],
                        item["discovery_tier"],
                        item["state"],
                        Jsonb(metadata),
                    ),
                )
    return _json_response(
        {
            "status": "accepted",
            "proof_label": "SOURCE_DISCOVERY_BOUNDED_IMPORT_PERSISTED",
            "kind": kind,
            "count": len(candidates),
            "candidate_ids": [item["candidate_id"] for item in candidates],
            "limits": {
                "outbound_fetch": False,
                "automatic_promotion": False,
                "secret_material_rejected": True,
            },
        },
        201,
    )


@app.get("/source-discovery/candidates")
def source_discovery_candidates():
    state = request.args.get("state", "").strip()
    if state and state not in ALLOWED_STATES:
        return _json_response({"status": "invalid", "error": "unknown state"}, 400)
    try:
        limit = max(1, min(int(request.args.get("limit", "20")), 100))
    except ValueError:
        return _json_response({"status": "invalid", "error": "limit must be an integer"}, 400)
    with _db_connect() as conn:
        _ensure_source_tables(conn)
        with conn.cursor() as cur:
            if state:
                cur.execute(
                    "SELECT * FROM source_candidate WHERE state = %s ORDER BY updated_at DESC LIMIT %s;",
                    (state, limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM source_candidate ORDER BY updated_at DESC LIMIT %s;",
                    (limit,),
                )
            rows = cur.fetchall()
    return _json_response(
        {"status": "ok", "count": len(rows), "items": [_format_row(row) for row in rows]}
    )


@app.get("/source-discovery/candidates/<candidate_id>")
def source_discovery_candidate(candidate_id: str):
    with _db_connect() as conn:
        _ensure_source_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM source_candidate WHERE candidate_id = %s;",
                (candidate_id.strip(),),
            )
            row = cur.fetchone()
    if not row:
        return _json_response({"status": "not_found", "candidate_id": candidate_id}, 404)
    return _json_response({"status": "found", "candidate": _format_row(row)})


@app.post("/source-discovery/candidates/<candidate_id>/transition")
def source_discovery_transition(candidate_id: str):
    payload = request.get_json(silent=True) or {}
    target = str(payload.get("target_state") or "").strip()
    reason = str(payload.get("reason") or "").strip()[:500]
    approval_reference = str(payload.get("approval_reference") or "").strip()[:300]
    rollback_reference = str(payload.get("rollback_reference") or "").strip()[:300]
    if target not in ALLOWED_STATES:
        return _json_response({"status": "invalid", "error": "unknown target_state"}, 400)

    observed_at = _now()
    with _db_connect() as conn:
        _ensure_source_tables(conn)
        with conn.cursor() as cur:
            cur.execute(
                "SELECT state FROM source_candidate WHERE candidate_id = %s FOR UPDATE;",
                (candidate_id.strip(),),
            )
            row = cur.fetchone()
            if not row:
                return _json_response({"status": "not_found", "candidate_id": candidate_id}, 404)
            current = row["state"]
            error = _validate_transition_request(
                current,
                target,
                reason,
                approval_reference,
                rollback_reference,
            )
            if error:
                return _json_response({"status": "blocked", "error": error}, 409)
            cur.execute(
                "UPDATE source_candidate SET state = %s, decision_reason = %s, updated_at = now() WHERE candidate_id = %s;",
                (target, reason or None, candidate_id.strip()),
            )
            evidence = {
                "from_state": current,
                "to_state": target,
                "automatic_promotion": False,
                "recorded_at": observed_at,
            }
            cur.execute(
                """
                INSERT INTO integration_decision (
                    decision_id, candidate_id, decision, reason, approval_reference,
                    rollback_reference, evidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb);
                """,
                (
                    _decision_id(candidate_id.strip(), current, target, observed_at),
                    candidate_id.strip(),
                    target,
                    reason or "governed lifecycle transition",
                    approval_reference or None,
                    rollback_reference or None,
                    Jsonb(evidence),
                ),
            )
    return _json_response(
        {
            "status": "accepted",
            "proof_label": "SOURCE_DISCOVERY_GOVERNED_TRANSITION_PERSISTED",
            "candidate_id": candidate_id,
            "from_state": current,
            "to_state": target,
            "automatic_promotion": False,
            "approval_reference_recorded": bool(approval_reference),
            "rollback_reference_recorded": bool(rollback_reference),
        }
    )
