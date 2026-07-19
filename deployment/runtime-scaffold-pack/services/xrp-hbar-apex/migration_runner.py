from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

import psycopg


def connect():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "xrp_hbar_apex"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "change_me"),
        connect_timeout=10,
    )


def ensure_ledger(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migration (
                migration_name TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            """
        )


def migration_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ValueError(f"migration directory does not exist: {directory}")
    return sorted(path for path in directory.glob("*.sql") if path.is_file())


def apply_migrations(directory: Path, *, check_only: bool = False) -> dict:
    files = migration_files(directory)
    applied: list[str] = []
    already_applied: list[str] = []
    with connect() as conn:
        ensure_ledger(conn)
        for path in files:
            sql_bytes = path.read_bytes()
            digest = hashlib.sha256(sql_bytes).hexdigest()
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT sha256 FROM schema_migration WHERE migration_name = %s;",
                    (path.name,),
                )
                row = cur.fetchone()
                if row:
                    existing = row[0]
                    if existing != digest:
                        raise RuntimeError(
                            f"migration hash mismatch for {path.name}: expected {existing}, observed {digest}"
                        )
                    already_applied.append(path.name)
                    continue
                if check_only:
                    raise RuntimeError(f"pending migration: {path.name}")
                cur.execute(sql_bytes.decode("utf-8"))
                cur.execute(
                    "INSERT INTO schema_migration (migration_name, sha256) VALUES (%s, %s);",
                    (path.name, digest),
                )
                applied.append(path.name)
        if check_only:
            conn.rollback()
        else:
            conn.commit()
    return {
        "status": "verified" if check_only else "applied",
        "directory": str(directory),
        "migration_count": len(files),
        "applied": applied,
        "already_applied": already_applied,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply hash-locked PostgreSQL migrations")
    parser.add_argument("--directory", type=Path, default=Path("/app/migrations"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = apply_migrations(args.directory, check_only=args.check)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
