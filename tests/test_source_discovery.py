import unittest

from source_discovery import (
    LifecycleError,
    canonicalize_url,
    classify_network_target,
    parse_bookmark_html,
    parse_opml,
    score_candidate,
    transition,
)


class SourceDiscoveryTests(unittest.TestCase):
    def test_canonical_url_removes_tracking_and_fragment(self):
        value = canonicalize_url("HTTPS://Example.COM:443/path?utm_source=x&b=2&a=1#frag")
        self.assertEqual(value, "https://example.com/path?a=1&b=2")

    def test_bookmark_parser_deduplicates(self):
        html = '''
        <a href="https://example.com/docs?utm_source=one">Docs</a>
        <a href="https://example.com/docs?utm_source=two">Duplicate</a>
        <a href="javascript:alert(1)">Unsafe scheme</a>
        '''
        items = parse_bookmark_html(html)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].canonical_url, "https://example.com/docs")

    def test_opml_parser_extracts_feed(self):
        opml = '''<?xml version="1.0"?><opml version="2.0"><body>
        <outline text="Official feed" xmlUrl="https://example.com/feed.xml" />
        </body></opml>'''
        items = parse_opml(opml)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Official feed")

    def test_private_network_targets_are_rejected(self):
        result = classify_network_target("http://127.0.0.1/admin")
        self.assertFalse(result["safe_for_sandbox_probe"])
        self.assertTrue(result["reasons"])

    def test_public_literal_target_is_allowed_by_static_check(self):
        result = classify_network_target("https://8.8.8.8/")
        self.assertTrue(result["safe_for_sandbox_probe"])

    def test_scoring_never_auto_promotes(self):
        result = score_candidate({
            "official_provenance": 100,
            "security": 100,
            "capability_fit": 100,
            "data_quality": 100,
            "least_privilege": 100,
            "maintenance": 100,
            "cost": 100,
            "interoperability": 100,
            "auditability": 100,
            "reversibility": 100,
        })
        self.assertEqual(result["score"], 100)
        self.assertFalse(result["automatic_promotion_allowed"])
        self.assertEqual(result["recommendation"], "PRIORITY_REVIEW")

    def test_hard_fail_overrides_high_score(self):
        result = score_candidate(
            {"official_provenance": 100, "security": 100, "capability_fit": 100},
            hard_fail_reasons=["requests seed phrase"],
        )
        self.assertEqual(result["recommendation"], "REJECTED")

    def test_lifecycle_rejects_skipping_approval(self):
        with self.assertRaises(LifecycleError):
            transition("SANDBOX_PROVEN", "APPROVED_PRODUCTION")
        self.assertEqual(transition("SANDBOX_PROVEN", "APPROVAL_REQUIRED"), "APPROVAL_REQUIRED")


if __name__ == "__main__":
    unittest.main()
