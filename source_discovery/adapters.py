from __future__ import annotations

import json
from xml.etree import ElementTree as ET

from .core import Candidate


def _dedupe(candidates: list[Candidate]) -> list[Candidate]:
    result: list[Candidate] = []
    seen: set[str] = set()
    for candidate in candidates:
        try:
            key = candidate.canonical_url
        except ValueError:
            continue
        if key not in seen:
            result.append(candidate)
            seen.add(key)
    return result


def parse_rss_atom(text: str, *, discovery_source: str = "rss_atom") -> list[Candidate]:
    ""