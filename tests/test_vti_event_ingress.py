from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from federation.vti_event_consumer import VtiEventConsumer, sign_event
from federation.vti_event_ingress import ingest_request
from federation.vti_module_router import VtiModuleRouter

SECRET = "test-secret-with-at-least-thirty-two-characters"


def event():
    return {
        "event_id": "evt-1", "event_type": "evidence.created", "schema_version": "1.0.0",
        "producer": "vti-evidence-service", "consumer": "xrp-hbar-hub-runtime",
        "occurred_at": "2026-07-20T00:00:00Z", "correlation_id": "corr-1", "idempotency_key": "idem-1",
        "source_refs": ["source-1"], "approval_state": "not_required",
        "payload": {"destination_modules": ["xrp-hbar-apex", "command-centre"], "artifact_type": "evidence_zip", "artifact_ref": "pack-1"},
        "evidence_refs": ["pack-1"], "retry_count": 0, "status": "INTEGRATED_STAGING",
    }


class IngressTests(unittest.TestCase):
    def test_signed_ingress_and_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            consumer = VtiEventConsumer(Path(tmp) / "events.sqlite3", SECRET)
            payload = event()
            body = json.dumps(payload).encode()
            headers = {"x-vti-signature": sign_event(payload, SECRET), "x-correlation-id": "corr-1"}
            status, ack = ingest_request(body, headers, consumer)
            self.assertEqual(status, 202); self.assertFalse(ack["duplicate"])
            status, ack = ingest_request(body, headers, consumer)
            self.assertEqual(status, 202); self.assertTrue(ack["duplicate"])

    def test_bad_signature_and_correlation(self):
        with tempfile.TemporaryDirectory() as tmp:
            consumer = VtiEventConsumer(Path(tmp) / "events.sqlite3", SECRET)
            payload = event(); body = json.dumps(payload).encode()
            self.assertEqual(ingest_request(body, {"x-vti-signature": "bad"}, consumer)[0], 401)
            headers = {"x-vti-signature": sign_event(payload, SECRET), "x-correlation-id": "wrong"}
            self.assertEqual(ingest_request(body, headers, consumer)[0], 400)

    def test_destination_router_allowlist(self):
        with tempfile.TemporaryDirectory() as tmp:
            router = VtiModuleRouter(Path(tmp) / "routes.sqlite3")
            rows = router.route(event())
            self.assertEqual({row["destination_module"] for row in rows}, {"xrp-hbar-apex", "command-centre"})
            bad = event(); bad["payload"]["destination_modules"] = ["unknown-module"]
            with self.assertRaises(ValueError): router.route(bad)


if __name__ == "__main__":
    unittest.main()
