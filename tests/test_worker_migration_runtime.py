import sys
import tempfile
import unittest
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parents[1] / "deployment" / "runtime-scaffold-pack" / "services" / "xrp-hbar-apex"
sys.path.insert(0, str(SERVICE_DIR))

from migration_runner import migration_files  # noqa: E402
from worker_runtime import execute  # noqa: E402


class WorkerMigrationRuntimeTests(unittest.TestCase):
    def test_noop_job_executes_without_external_side_effects(self):
        result = execute({"job_type": "noop", "payload": {"proof": "worker-smoke"}})
        self.assertTrue(result["ok"])
        self.assertEqual(result["echo"]["proof"], "worker-smoke")
        self.assertIn("processed_at", result)

    def test_checkpoint_job_executes(self):
        result = execute({"job_type": "checkpoint", "payload": {"stage": "verified"}})
        self.assertTrue(result["ok"])
        self.assertEqual(result["checkpoint"]["stage"], "verified")

    def test_unsupported_job_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported job_type"):
            execute({"job_type": "external-fetch", "payload": {}})

    def test_migrations_are_sorted_and_sql_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "002_second.sql").write_text("SELECT 2;")
            (root / "001_first.sql").write_text("SELECT 1;")
            (root / "README.md").write_text("ignored")
            self.assertEqual([path.name for path in migration_files(root)], ["001_first.sql", "002_second.sql"])

    def test_runtime_worker_migration_is_packaged(self):
        migration = SERVICE_DIR / "migrations" / "001_runtime_worker.sql"
        self.assertTrue(migration.is_file())
        text = migration.read_text()
        self.assertIn("CREATE TABLE IF NOT EXISTS worker_job", text)
        self.assertIn("CREATE TABLE IF NOT EXISTS worker_heartbeat", text)


if __name__ == "__main__":
    unittest.main()
