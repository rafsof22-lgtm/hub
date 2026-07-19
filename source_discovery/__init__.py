"""Governed Jarvis source-discovery primitives."""

from .adapters import parse_candidate_json, parse_rss_atom
from .core import (
    Candidate,
    LifecycleError,
    canonicalize_url,
    classify_network_target,
    parse_bookmark_html,
    parse_opml,
    score_candidate,
    transition,
)
from .registry import CandidateRecord, CandidateStore, InMemoryCandidateStore

__all__ = [
    "Candidate",
    "CandidateRecord",
    "CandidateStore",
    "InMemoryCandidateStore",
    "LifecycleError",
    "canonicalize_url",
    "classify_network_target",
    "parse_bookmark_html",
    "parse_candidate_json",
    "parse_opml",
    "parse_rss_atom",
    "score_candidate",
    "transition",
]
