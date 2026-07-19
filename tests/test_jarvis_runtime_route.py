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
        self.assertTrue(payload["capabilities"])
        self.assertIn("evidence_refs", payload)

    def test_contract_does_not_expose_secret_fields(self):
        payload = self.client.get("/.well-known/jarvis/health").get_json()
        rendered = repr(payload).lower()
        for forbidden in ("oauth_client_secret", "refresh_token", "private_key", "bearer_token"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
