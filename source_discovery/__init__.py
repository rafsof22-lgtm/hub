"""Governed Jarvis source-discovery primitives."""

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

__all__ = [
    "Candidate",
    "LifecycleError",
    "canonicalize_url",
    "classify_network_target",
    "parse_bookmark_html",
    "parse_opml",
    "score_candidate",
    "transition",
]
