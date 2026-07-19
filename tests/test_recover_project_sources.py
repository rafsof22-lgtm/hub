import csv
import json
import tempfile
import unittest
import zlib
from pathlib import Path

from reconstruction.recover_project_sources import recover_folder0, safe_relative_path


class ProjectSourceRecoveryTests(unittest.TestCase):
    def test_rejects_absolute_and_parent_paths(self):
        with self.assertRaises(ValueError):
            safe_relative_path("/etc/passwd")
        with self.assertRaises(ValueError):
            safe_relative_path("KIMI_WORKSPACE_RAW/../secret.txt")

    def test_recovers_text_and_verifies_crc(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = b"hello world"
            partial = root / "folder0_partial.raw"
            partial.write_bytes(raw)
            inventory = root / "source_inventory.csv"
            with inventory.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["index", "name", "has_stream", "is_dir", "size", "crc32", "folder", "substream"])
                writer.writeheader()
                writer.writerow({
                    "index": 1,
                    "name": "KIMI_WORKSPACE_RAW/docs/readme.md",
                    "has_stream": "True",
                    "is_dir": "False",
                    "size": len(raw),
                    "crc32": f"{zlib.crc32(raw) & 0xffffffff:08x}",
                    "folder": 0,
                    "substream": 0,
                })
            out = root / "out"
            result = recover_folder0(partial, inventory, out)
            self.assertEqual(result.folder0_streams_recovered, 1)
            self.assertEqual(result.text_files_written, 1)
            self.assertEqual(result.crc_verified, 1)
            self.assertEqual(result.crc_mismatches, [])
            self.assertEqual((out / "docs/readme.md").read_text(), "hello world")
            manifest = json.loads((out / "recovery_manifest.json").read_text())
            self.assertTrue(manifest["files"][0]["crc_ok"])

    def test_crc_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = root / "folder0_partial.raw"
            partial.write_bytes(b"abc")
            inventory = root / "source_inventory.csv"
            with inventory.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["index", "name", "has_stream", "is_dir", "size", "crc32", "folder", "substream"])
                writer.writeheader()
                writer.writerow({"index": 1, "name": "KIMI_WORKSPACE_RAW/a.txt", "has_stream": "True", "is_dir": "False", "size": 3, "crc32": "00000000", "folder": 0, "substream": 0})
            result = recover_folder0(partial, inventory, root / "out")
            self.assertEqual(result.crc_mismatches, ["KIMI_WORKSPACE_RAW/a.txt"])

    def test_truncation_is_accounted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            partial = root / "folder0_partial.raw"
            partial.write_bytes(b"ab")
            inventory = root / "source_inventory.csv"
            with inventory.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["index", "name", "has_stream", "is_dir", "size", "crc32", "folder", "substream"])
                writer.writeheader()
                writer.writerow({"index": 1, "name": "KIMI_WORKSPACE_RAW/a.txt", "has_stream": "True", "is_dir": "False", "size": 3, "crc32": "", "folder": 0, "substream": 0})
            result = recover_folder0(partial, inventory, root / "out")
            self.assertEqual(result.folder0_streams_recovered, 0)
            self.assertEqual(result.truncated_at_stream, "KIMI_WORKSPACE_RAW/a.txt")


if __name__ == "__main__":
    unittest.main()
