from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ALLOWED_MODULES = {
    "xrp-hbar-apex", "creator-reliability", "claim-verification", "jarvis-knowledge",
    "command-centre", "research-archive", "risk-intelligence", "cost-ledger",
}


class VtiModuleRouter:
    def __init__(self, database_path: str | Path):
        self.database_path = str(database_path)
        with sqlite3.connect(self.database_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS vti_module_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL,
                correlation_id TEXT NOT NULL, destination_module TEXT NOT NULL,
                artifact_type TEXT NOT NULL, artifact_ref TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL,
                delivered_at TEXT, last_error TEXT,
                UNIQUE(event_id,destination_module,artifact_ref)
            )""")

    def route(self, event: Mapping[str, Any]) -> list[dict[str, Any]]:
        payload = event.get("payload") or {}
        destinations = payload.get("destination_modules") or []
        if not isinstance(destinations, list) or not destinations:
            raise ValueError("destination_modules required")
        unknown = sorted(set(destinations).difference(ALLOWED_MODULES))
        if unknown:
            raise ValueError(f"unapproved destination modules: {', '.join(unknown)}")
        artifact_type = str(payload.get("artifact_type") or event.get("event_type") or "unknown")
        artifact_ref = str(payload.get("artifact_ref") or event.get("event_id"))
        now = datetime.now(timezone.utc).isoformat()
        rows = []
        with sqlite3.connect(self.database_path) as db:
            for module in sorted(set(destinations)):
                db.execute("""INSERT OR IGNORE INTO vti_module_deliveries
                    (event_id,correlation_id,destination_module,artifact_type,artifact_ref,status,created_at)
                    VALUES (?,?,?,?,?,'pending',?)""",
                    (event["event_id"], event["correlation_id"], module, artifact_type, artifact_ref, now))
                rows.append({"destination_module": module, "artifact_type": artifact_type, "artifact_ref": artifact_ref, "status": "pending"})
        return rows

    def pending(self) -> list[dict[str, Any]]:
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute("SELECT * FROM vti_module_deliveries WHERE status='pending' ORDER BY id")]
