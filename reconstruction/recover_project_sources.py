from __future__ import annotations

import argparse
import binascii
import csv
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path, PurePosixPath

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
