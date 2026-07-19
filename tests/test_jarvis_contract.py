import unittest

from federation.jarvis_contract import build_contract, validate_contract


class JarvisContractTests(unittest.TestCase):
    def test_partial_contract_is_truthful_and_valid(self):
        contract = build_contract(commit="abc123", environment="test")
        self.assertEqual(contract["repository_id"], "hub")
        self.assertEqual(contract["status"], "IMPLEMENTED_NOT_INTEGRATED")
        self.assertEqual(contract["health"]["readiness"], "partial")
        self.assertEqual(validate_contract(contract), [])

    def test_all_required_routes_can_report_ready(self):
        routes = {
            "/health": "pass",
            "/ready": "pass",
            "/deployment/status": "pass",
            "/vti/status": "pass",
            "/email/newsletter/status": "pass",
            "/evidence-pack/status": "pass",
            "/source-discovery/status": "pass",
        }
        contract = build_contract(route_state=routes)
        self.assertEqual(contract["health"]["readiness"], "ready")

    def test_missing_source_discovery_route_reports_partial(self):
        routes = {
            "/health": "pass",
            "/ready": "pass",
            "/deployment/status": "pass",
            "/vti/status": "pass",
            "/email/newsletter/status": "pass",
            "/evidence-pack/status": "pass",
        }
        contract = build_contract(route_state=routes)
        self.assertEqual(contract["health"]["readiness"], "partial")
        checks = {item["name"]: item["status"] for item in contract["health"]["checks"]}
        self.assertEqual(checks["/source-discovery/status"], "unknown")

    def test_no_secret_values_are_present(self):
        contract = build_contract()
        rendered = repr(contract).lower()
        for forbidden in ("oauth_client_secret", "refresh_token", "private_key", "bearer_token"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
