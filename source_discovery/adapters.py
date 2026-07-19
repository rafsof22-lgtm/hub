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
    """Parse RSS 2.x or Atom feed entries into discovery candidates."""
    root = ET.fromstring(text)
    candidates: list[Candidate] = []

    # RSS 2.x
    for item in root.findall(".//item"):
        link = (item.findtext("link") or "").strip()
        title = (item.findtext("title") or "").strip()
        if link:
            candidates.append(Candidate(link, title, discovery_source, 2))

    # Atom, namespace-agnostic
    for entry in root.iter():
        if not entry.tag.endswith("entry"):
            continue
        title = ""
        link = ""
        for child in list(entry):
            if child.tag.endswith("title") and child.text:
                title = child.text.strip()
            elif child.tag.endswith("link"):
                href = (child.attrib.get("href") or "").strip()
                rel = (child.attrib.get("rel") or "alternate").strip()
                if href and rel in {"alternate", ""}:
                    link = href
                    break
        if link:
            candidates.append(Candidate(link, title, discovery_source, 2))

    return _dedupe(candidates)


def parse_candidate_json(text: str, *, discovery_source: str = "json_import") -> list[Candidate]:
    """Parse a bounded JSON list of URLs or candidate objects.

    Accepted forms:
    - ["https://example.com"]
    - [{"url": "https://example.com", "title": "Example", "tags": ["api"]}]
    - {"items": [...]} 
    """
    payload = json.loads(text)
    if isinstance(payload, dict):
        payload = payload.get("items", [])
    if not isinstance(payload, list):
        raise ValueError("candidate JSON must be a list or an object containing an items list")
    if len(payload) > 5000:
        raise ValueError("candidate JSON exceeds the 5000-item safety limit")

    candidates: list[Candidate] = []
    for item in payload:
        if isinstance(item, str):
            url = item
            title = ""
            tags: tuple[str, ...] = ()
        elif isinstance(item, dict):
            url = str(item.get("url") or item.get("source_url") or "").strip()
            title = str(item.get("title") or "").strip()
            raw_tags = item.get("tags", [])
            tags = tuple(str(tag).strip() for tag in raw_tags if str(tag).strip()) if isinstance(raw_tags, list) else ()
        else:
            continue
        if url:
            candidates.append(Candidate(url, title, discovery_source, 2, tags))

    return _dedupe(candidates)
