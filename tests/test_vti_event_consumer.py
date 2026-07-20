import tempfile
import unittest
from pathlib import Path

from federation.vti_event_consumer import (
    EventAuthenticationError,
    EventValidationError,
    VtiEventConsumer,
    sign_event,
)

SECRET = "test-secret-with-at-least-thirty-two-characters"


def valid_event(**overrides):
    event = {
        "event_id": "evt-001",
        "event_type": "evidence.created",
        "schema_version": "1.0.0",
        "producer": "vti-evidence-service",
        "consumer": "xrp-hbar-hub-runtime",
        "occurred_at": "2026-07-20T00:00:00Z",
        "correlation_id": "corr-001",
        "idempotency_key": "idem-001",
        "source_refs": ["source-001"],
        "approval_state": "approved",
        "payload": {"asset_tags": ["XRP", "Ripple"], "claim_count": 1},
        "evidence_refs": ["evidence-001"],
        "retry_count": 0,
        "status": "INTEGRATED_STAGING",
    }
    event.update(overrides)
    return event


class VtiEventConsumerTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Path(self.tempdir.name) / "events.sqlite3"
        self.consumer = VtiEventConsumer(self.database, SECRET, max_attempts=2)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_authenticated_event_is_persisted_and_acknowledged(self):
        event = valid_event()
        ack = self.consumer.ingest(event, sign_event(event, SECRET))
        self.assertTrue(ack.accepted)
        self.assertFalse(ack.duplicate)
        stored = self.consumer.get_event(event["event_id"])
        self.assertEqual(stored["correlation_id"], "corr-001")
        self.assertEqual(stored["processing_status"], "accepted")
        self.assertNotIn(SECRET, stored["raw_event"])

    def test_duplicate_idempotency_key_returns_same_ack_without_new_event(self):
        event = valid_event()
        signature = sign_event(event, SECRET)
        first = self.consumer.ingest(event, signature)
        duplicate = dict(event, event_id="evt-duplicate")
        second = self.consumer.ingest(duplicate, sign_event(duplicate, SECRET))
        self.assertEqual(first.event_id, second.event_id)
        self.assertTrue(second.duplicate)
        self.assertIsNone(self.consumer.get_event("evt-duplicate"))

    def test_modified_event_signature_is_rejected(self):
        event = valid_event()
        signature = sign_event(event, SECRET)
        event["payload"] = {"claim_count": 999}
        with self.assertRaises(EventAuthenticationError):
            self.consumer.ingest(event, signature)

    def test_missing_correlation_id_is_rejected(self):
        event = valid_event()
        del event["correlation_id"]
        with self.assertRaises(EventValidationError):
            self.consumer.ingest(event, sign_event(event, SECRET))

    def test_unsupported_schema_is_rejected(self):
        event = valid_event(schema_version="2.0.0")
        with self.assertRaises(EventValidationError):
            self.consumer.ingest(event, sign_event(event, SECRET))

    def test_retry_exhaustion_moves_event_to_dead_letter_and_allows_controlled_replay(self):
        event = valid_event()
        self.consumer.ingest(event, sign_event(event, SECRET))
        self.assertEqual(self.consumer.mark_failed(event["event_id"], "HUB_MODULE_UNAVAILABLE"), "retry_pending")
        self.assertEqual(self.consumer.mark_failed(event["event_id"], "HUB_MODULE_UNAVAILABLE"), "dead_letter")
        self.assertEqual(self.consumer.get_event(event["event_id"])["processing_status"], "dead_letter")
        self.consumer.replay_dead_letter(event["event_id"])
        replayed = self.consumer.get_event(event["event_id"])
        self.assertEqual(replayed["processing_status"], "retry_pending")
        self.assertEqual(replayed["attempts"], 0)

    def test_processed_event_preserves_raw_event_and_marks_completion(self):
        event = valid_event()
        self.consumer.ingest(event, sign_event(event, SECRET))
        self.consumer.mark_processed(event["event_id"])
        stored = self.consumer.get_event(event["event_id"])
        self.assertEqual(stored["processing_status"], "processed")
        self.assertIsNotNone(stored["processed_at"])
        self.assertIn("evidence.created", stored["raw_event"])


if __name__ == "__main__":
    unittest.main()
