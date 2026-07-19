from __future__ import annotations

import hashlib
import ipaddress
import socket
from dataclasses import dataclass, field
from html.parser import HTMLParser
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

ALLOWED_STATES = {
    "DISCOVERED",
    "NORMALISED",
    "OFFICIAL_SOURCE_RESOLVED",
    "VERIFIED_CANDIDATE",
    "QUARANTINED",
    "SANDBOX_READY",
    "SANDBOX_PROVEN",
    "APPROVAL_REQUIRED",
    "CANARY",
    "APPROVED_PRODUCTION",
    "WATCHLIST",
    "DEPRECATED",
    "REVOKED",
    "REJECTED",
}

TRANSITIONS = {
    "DISCOVERED": {"NORMALISED", "REJECTED"},
    "NORMALISED": {"OFFICIAL_SOURCE_RESOLVED", "QUARANTINED", "REJECTED"},
    "OFFICIAL_SOURCE_RESOLVED": {"VERIFIED_CANDIDATE", "QUARANTINED", "REJECTED"},
    "VERIFIED_CANDIDATE": {"QUARANTINED", "SANDBOX_READY", "REJECTED"},
    "QUARANTINED": {"SANDBOX_READY", "REJECTED", "WATCHLIST"},
    "SANDBOX_READY": {"SANDBOX_PROVEN", "REJECTED"},
    "SANDBOX_PROVEN": {"APPROVAL_REQUIRED", "REJECTED"},
    "APPROVAL_REQUIRED": {"CANARY", "REJECTED"},
    "CANARY": {"APPROVED_PRODUCTION", "WATCHLIST", "REVOKED"},
    "APPROVED_PRODUCTION": {"WATCHLIST", "DEPRECATED", "REVOKED"},
    "WATCHLIST": {"SANDBOX_READY", "DEPRECATED", "REVOKED", "REJECTED"},
    "DEPRECATED": {"REVOKED"},
    "REJECTED": set(),
    "REVOKED": set(),
}

TRACKING_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
}


class LifecycleError(ValueError):
    pass


@dataclass(frozen=True)
class Candidate:
    source_url: str
    title: str = ""
    discovery_source: str = "manual"
    discovery_tier: int = 3
    tags: tuple[str, ...] = field(default_factory=tuple)

    @property
    def canonical_url(self) -> str:
        return canonicalize_url(self.source_url)

    @property
    def candidate_id(self) -> str:
        raw = f"{self.canonical_url}|{self.discovery_source}|{self.discovery_tier}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class _BookmarkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict[str, str]] = []
        self._href: str | None = None
        self._title: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        values = {key.lower(): value for key, value in attrs}
        href = values.get("href")
        if href:
            self._href = href.strip()
            self._title = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._title.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.items.append({"url": self._href, "title": "".join(self._title).strip()})
            self._href = None
            self._title = []


def canonicalize_url(url: str) -> str:
    parsed = urlsplit(url.strip())
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        raise ValueError("only absolute http/https URLs are accepted")
    scheme = parsed.scheme.lower()
    host = parsed.hostname.rstrip(".").lower()
    port = parsed.port
    netloc = host
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    path = parsed.path or "/"
    query = urlencode(sorted((k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if k.lower() not in TRACKING_KEYS))
    return urlunsplit((scheme, netloc, path, query, ""))


def classify_network_target(url: str, *, resolve_dns: bool = False) -> dict[str, object]:
    canonical = canonicalize_url(url)
    host = urlsplit(canonical).hostname or ""
    reasons: list[str] = []
    addresses: list[str] = []

    try:
        literal = ipaddress.ip_address(host)
        addresses.append(str(literal))
    except ValueError:
        if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
            reasons.append("local hostname")
        if resolve_dns:
            try:
                addresses.extend(sorted({item[4][0] for item in socket.getaddrinfo(host, None)}))
            except socket.gaierror:
                reasons.append("dns resolution failed")

    for value in addresses:
        ip = ipaddress.ip_address(value)
        if not ip.is_global:
            reasons.append(f"non-global address:{value}")

    return {
        "url": canonical,
        "host": host,
        "addresses": addresses,
        "safe_for_sandbox_probe": not reasons,
        "reasons": sorted(set(reasons)),
    }


def parse_bookmark_html(text: str, *, discovery_source: str = "bookmark_html") -> list[Candidate]:
    parser = _BookmarkParser()
    parser.feed(text)
    result: list[Candidate] = []
    seen: set[str] = set()
    for item in parser.items:
        try:
            candidate = Candidate(item["url"], item["title"], discovery_source, 2)
            key = candidate.canonical_url
        except ValueError:
            continue
        if key not in seen:
            result.append(candidate)
            seen.add(key)
    return result


def parse_opml(text: str, *, discovery_source: str = "opml") -> list[Candidate]:
    root = ET.fromstring(text)
    result: list[Candidate] = []
    seen: set[str] = set()
    for outline in root.findall(".//outline"):
        url = outline.attrib.get("xmlUrl") or outline.attrib.get("htmlUrl")
        if not url:
            continue
        title = outline.attrib.get("title") or outline.attrib.get("text") or ""
        try:
            candidate = Candidate(url, title, discovery_source, 2)
            key = candidate.canonical_url
        except ValueError:
            continue
        if key not in seen:
            result.append(candidate)
            seen.add(key)
    return result


def score_candidate(scores: dict[str, int], *, hard_fail_reasons: list[str] | None = None) -> dict[str, object]:
    weights = {
        "official_provenance": 15,
        "security": 15,
        "capability_fit": 15,
        "data_quality": 10,
        "least_privilege": 10,
        "maintenance": 10,
        "cost": 10,
        "interoperability": 5,
        "auditability": 5,
        "reversibility": 5,
    }
    unknown = sorted(set(scores) - set(weights))
    if unknown:
        raise ValueError(f"unknown score dimensions: {', '.join(unknown)}")
    normalised = {name: max(0, min(100, int(scores.get(name, 0)))) for name in weights}
    total = round(sum(normalised[name] * weight for name, weight in weights.items()) / 100)
    hard_fail_reasons = [reason.strip() for reason in (hard_fail_reasons or []) if reason.strip()]
    return {
        "score": total,
        "components": normalised,
        "hard_fail": bool(hard_fail_reasons),
        "hard_fail_reasons": hard_fail_reasons,
        "recommendation": "REJECTED" if hard_fail_reasons else ("PRIORITY_REVIEW" if total >= 75 else "REVIEW" if total >= 50 else "WATCHLIST"),
        "automatic_promotion_allowed": False,
    }


def transition(current: str, target: str) -> str:
    if current not in ALLOWED_STATES or target not in ALLOWED_STATES:
        raise LifecycleError("unknown lifecycle state")
    if target not in TRANSITIONS[current]:
        raise LifecycleError(f"transition not allowed: {current} -> {target}")
    return target
