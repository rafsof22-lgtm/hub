import unittest

from federation.jarvis_contract import REQUIRED_ROUTES, build_contract, validate_contract


class JarvisContractTests(unittest.TestCase):
    def test_partial_contract_is_truthful_and_valid(self):
        contract = build_contract(commit="abc123", environment="test")
        self.assertEqual(contract["repository_id"], "hub")
        self.assertEqual(contract["status"], "IMPLEMENTED_NOT_INTEGRATED")
        self.assertEqual(contract["health"]["readiness"], "partial")
        self.assertEqual(validate_contract(contract), [])

    def test_all_required_routes_can_report_ready(self):
        routes = {route: "pass" for route in REQUIRED_ROUTES}
        contract = build_contract(route_state=routes)
        self.assertEqual(contract["health"]["readiness"], "ready")

    def test_missing_worker_route_reports_partial(self):
        routes = {route: "pass" for route in REQUIRED_ROUTES if route != "/worker/status"}
        contract = build_contract(route_state=routes)
        self.assertEqual(contract["health"]["readiness"], "partial")
        checks = {item["name"]: item["status"] for item in contract["health"]["checks"]}
        self.assertEqual(checks["/worker/status"], "unknown")

    def test_required_runtime_routes_are_governed(self):
        self.assertIn("/source-discovery/status", REQUIRED_ROUTES)
        self.assertIn("/worker/status", REQUIRED_ROUTES)
        self.assertIn("/migrations/status", REQUIRED_ROUTES)
        self.assertIn("/outbound/status", REQUIRED_ROUTES)

    def test_no_secret_values_are_present(self):
        contract = build_contract()
        rendered = repr(contract).lower()
        for forbidden in ("oauth_client_secret", "refresh_token", "private_key", "bearer_token"):
            self.assertNotIn(forbidden, rendered)


if __name__ == "__main__":
    unittest.main()
