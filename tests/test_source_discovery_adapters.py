import unittest

from source_discovery import (
    InMemoryCandidateStore,
    parse_candidate_json,
    parse_rss_atom,
)


class SourceDiscoveryAdapterTests(unittest.TestCase):
    def test_rss_parser_extracts_and_deduplicates(self):
        text = """<rss><channel>
        <item><title>One</title><link>https://example.com/a?utm_source=x</link></item>
        <item><title>Duplicate</title><link>https://example.com/a?utm_source=y</link></item>
        </channel></rss>"""
        items = parse_rss_atom(text)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].canonical_url, "https://example.com/a")

    def test_atom_parser_extracts_alternate_link(self):
        text = """<feed xmlns='http://www.w3.org/2005/Atom'>
        <entry><title>Release</title><link rel='alternate' href='https://example.com/release'/></entry>
        </feed>"""
        items = parse_rss_atom(text)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "Release")

    def test_json_parser_accepts_strings_and_objects(self):
        items = parse_candidate_json('["https://example.com/a", {"url":"https://example.com/b", "title":"B", "tags":["api"]}]')
        self.assertEqual(len(items), 2)
        self.assertEqual(items[1].tags, ("api",))

    def test_json_parser_rejects_unbounded_payload(self):
        payload = "[" + ",".join('"https://example.com"' for _ in range(5001)) + "]"
        with self.assertRaises(ValueError):
            parse_candidate_json(payload)

    def test_registry_ingest_get_filter_and_transition(self):
        store = InMemoryCandidateStore()
        record = store.ingest(parse_candidate_json('["https://example.com/api"]'))[0]
        self.assertEqual(store.get(record.candidate_id).state, "DISCOVERED")
        record.move_to("NORMALISED", reason="canonical URL stored")
        store.upsert(record)
        self.assertEqual(len(store.list(state="NORMALISED")), 1)
        self.assertEqual(store.list(state="NORMALISED")[0].decision_reason, "canonical URL stored")


if __name__ == "__main__":
    unittest.main()
