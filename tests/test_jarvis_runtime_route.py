import sys
import unittest
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1] / "deployment" / "runtime-scaffold-pack" / "services" / "xrp-hbar-apex"
sys.path.insert(0, str(SERVICE_DIR))

import jarvis_runtime  # noqa: E402


class JarvisRuntimeRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = jarvis_runtime.app.test_client()

    def test_health_contract_route(self):
        response = self.client.get("/.well-known/jarvis/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["repository_id"], "hub")
        self.assertEqual(payload["service_id"], "xrp-hbar-hub-runtime")
        self.assertEqual(payload["contract_version"], "1.0.0")
        self.assertEqual(payload["health"]["readiness"], "ready")
        self.assertNotIn("validation_errors", payload)

    def test_capabilities_contract_route(self):
        response = self.client.get("/.well-known/jarvis/capabilities")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["repository_id"], "hub")
        capability_ids = {item["id"] for item in payload["capabilities"]}
        self.assertIn("reliable-worker", capability_ids)
        self.assertIn("hash-locked-migrations", capability_ids)
        self.assertIn("outbound-fail-closed", capability_ids)
        self.assertIn("evidence_refs", payload)

    def test_runtime_control_routes_are_registered(self):
        rules = {rule.rule for rule in jarvis_runtime.app.url_map.iter_rules()}
        for route in ("/worker/status", "/worker/jobs", "/worker/jobs/<job_id>", "/migrations/status", "/outbound/status"):
            self.assertIn(route, rules)

    def test_outbound_route_is_fail_closed(self):
        response = self.client.get("/outbound/status")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "safe_disabled")
        self.assertFalse(payload["external_fetch_enabled"])

    def test_contract_does_not_expose_secret_fields(self):
        payload = self.client.get("/.well-known/jarvis/health").get_json()
        rendered = repr(payload).lower()
        for forbidden in ("oauth_client_secret", "refresh_token", "private_key", "bearer_token"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
