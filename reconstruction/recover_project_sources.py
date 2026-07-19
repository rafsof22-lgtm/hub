from __future__ import annotations

import argparse
import binascii
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx",
    ".py", ".css", ".html", ".csv", ".sql", ".sh", ".toml", ".xml", ".ini",
    ".prisma", ".env"
}
TEXT_BASENAMES = {
    "dockerfile", "package.json", "tsconfig.json", "requirements.txt", "readme",
    "license", ".env.example"
}


@dataclass(frozen=True)
class InventoryRecord:
    index: int
    name: str
    has_stream: bool
    is_dir: bool
    size: int
    crc32: str | None
    folder: int | None
    substream: int | None


@dataclass
class RecoveryResult:
    source_name: str
    source_size: int
    inventory_records: int
    folder0_streams_seen: int
    folder0_streams_recovered: int
    text_files_written: int
    crc_verified: int
    crc_mismatches: list[str]
    truncated_at_stream: str | None
    output_manifest: str


def _to_bool(value: str) -> bool:
    return str(value).strip().lower() == "true"


def _to_optional_int(value: str) -> int | None:
    value = str(value or "").strip()
    return int(value) if value else None


def load_inventory(path: Path) -> list[InventoryRecord]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    result: list[InventoryRecord] = []
    for raw in rows:
        # Handles both normal exports and the historical duplicated-index CSV header.
        name = raw.get("name") or raw.get("index,name") or ""
        index_value = raw.get("index") or raw.get("index,index") or "0"
        result.append(
            InventoryRecord(
                index=int(index_value),
                name=name,
                has_stream=_to_bool(raw.get("has_stream", "False")),
                is_dir=_to_bool(raw.get("is_dir", "False")),
                size=int(raw.get("size") or 0),
                crc32=(raw.get("crc32") or "").strip() or None,
                folder=_to_optional_int(raw.get("folder", "")),
                substream=_to_optional_int(raw.get("substream", "")),
            )
        )
    return result


def is_text_candidate(record: InventoryRecord, blob: bytes) -> bool:
    suffix = Path(record.name).suffix.lower()
    basename = Path(record.name).name.lower()
    if suffix not in TEXT_EXTENSIONS and basename not in TEXT_BASENAMES and record.size > 100_000:
        return False
    if b"\x00" in blob[:4096] and suffix != ".prisma":
        return False
    return True


def decode_text(blob: bytes) -> str | None:
    for encoding in ("utf-8", "utf-16"):
        try:
            return blob.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def safe_relative_path(name: str) -> Path:
    path = Path(name)
    parts = path.parts[1:] if path.parts and path.parts[0] == "KIMI_WORKSPACE_RAW" else path.parts
    safe = [part for part in parts if part not in {"", ".", ".."}]
    return Path(*safe)


def recover_folder0(partial_raw: Path, inventory_csv: Path, output_dir: Path) -> RecoveryResult:
    data = partial_raw.read_bytes()
    records = load_inventory(inventory_csv)
    output_dir.mkdir(parents=True, exist_ok=True)

    offset = 0
    recovered = 0
    text_files = 0
    crc_verified = 0
    mismatches: list[str] = []
    truncated_at: str | None = None
    file_manifest: list[dict] = []

    folder0 = [record for record in records if record.has_stream and record.folder == 0]
    for record in folder0:
        end = offset + record.size
        if end > len(data):
            truncated_at = record.name
            break
        blob = data[offset:end]
        offset = end
        recovered += 1

        observed_crc = f"{binascii.crc32(blob) & 0xffffffff:08x}"
        crc_ok = record.crc32 is None or observed_crc.lower() == record.crc32.lower()
        if crc_ok and record.crc32:
            crc_verified += 1
        elif record.crc32:
            mismatches.append(record.name)

        written_path: str | None = None
        if is_text_candidate(record, blob):
            text = decode_text(blob)
            if text is not None:
                destination = output_dir / safe_relative_path(record.name)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(text, encoding="utf-8")
                written_path = str(destination)
                text_files += 1

        file_manifest.append(
            {
                "index": record.index,
                "name": record.name,
                "size": record.size,
                "expected_crc32": record.crc32,
                "observed_crc32": observed_crc,
                "crc_ok": crc_ok,
                "sha256": hashlib.sha256(blob).hexdigest(),
                "written_path": written_path,
            }
        )

    manifest_path = output_dir / "recovery_manifest.json"
    result = RecoveryResult(
        source_name=partial_raw.name,
        source_size=len(data),
        inventory_records=len(records),
        folder0_streams_seen=len(folder0),
        folder0_streams_recovered=recovered,
        text_files_written=text_files,
        crc_verified=crc_verified,
        crc_mismatches=mismatches,
        truncated_at_stream=truncated_at,
        output_manifest=str(manifest_path),
    )
    manifest_path.write_text(
        json.dumps({"summary": asdict(result), "files": file_manifest}, indent=2),
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover verifiable folder-0 project sources from preserved raw bytes")
    parser.add_argument("--partial-raw", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = recover_folder0(args.partial_raw, args.inventory, args.output)
    print(json.dumps(asdict(result), indent=2))
    return 1 if result.crc_mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
