import sys
import unittest
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1] / "deployment" / "runtime-scaffold-pack" / "services" / "xrp-hbar-apex"
sys.path.insert(0, str(SERVICE_DIR))

import jarvis_runtime  # noqa: E402


class SourceDiscoveryRuntimeRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = jarvis_runtime.app.test_client()

    def test_status_route_is_registered_and_non_executing(self):
        response = self.client.get("/source-discovery/status")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["proof_label"], "SOURCE_DISCOVERY_RUNTIME_ROUTES_REGISTERED")
        self.assertFalse(payload["limits"]["outbound_fetch"])
        self.assertFalse(payload["limits"]["automatic_promotion"])
        self.assertFalse(payload["limits"]["production_credentials"])

    def test_secret_material_is_rejected_before_persistence(self):
        response = self.client.post(
            "/source-discovery/import/json",
            json={"content": '[{"url":"https://example.com","api_key":"secret-value-12345678"}]'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("secret material", response.get_json()["error"])

    def test_malformed_json_is_rejected_before_persistence(self):
        response = self.client.post(
            "/source-discovery/import/json",
            json={"content": "[not-valid-json"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["status"], "invalid")

    def test_unknown_import_kind_is_rejected(self):
        response = self.client.post(
            "/source-discovery/import/unknown",
            json={"content": "https://example.com"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("unsupported import kind", response.get_json()["error"])

    def test_body_limit_is_enforced(self):
        response = self.client.post(
            "/source-discovery/import/json",
            data=b"x" * 1_000_001,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 413)

    def test_federation_health_includes_source_discovery_route(self):
        response = self.client.get("/.well-known/jarvis/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        checks = {item["name"]: item["status"] for item in payload["health"]["checks"]}
        self.assertEqual(checks.get("/source-discovery/status"), "pass")


if __name__ == "__main__":
    unittest.main()
