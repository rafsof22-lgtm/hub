from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, Protocol

from .core import ALLOWED_STATES, Candidate, transition


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class CandidateRecord:
    candidate_id: str
    source_url: str
    canonical_url: str
    title: str
    discovery_source: str
    discovery_tier: int
    tags: list[str] = field(default_factory=list)
    state: str = "DISCOVERED"
    risk_class: str = "R0_PUBLIC_READ_ONLY"
    score: int | None = None
    recommendation: str | None = None
    hard_fail_reasons: list[str] = field(default_factory=list)
    official_url: str | None = None
    decision_reason: str | None = None
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @classmethod
    def from_candidate(cls, candidate: Candidate) -> "CandidateRecord":
        return cls(
            candidate_id=candidate.candidate_id,
            source_url=candidate.source_url,
            canonical_url=candidate.canonical_url,
            title=candidate.title,
            discovery_source=candidate.discovery_source,
            discovery_tier=candidate.discovery_tier,
            tags=list(candidate.tags),
        )

    def move_to(self, target: str, *, reason: str | None = None) -> None:
        self.state = transition(self.state, target)
        self.decision_reason = reason
        self.updated_at = _now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CandidateStore(Protocol):
    def upsert(self, record: CandidateRecord) -> CandidateRecord: ...
    def get(self, candidate_id: str) -> CandidateRecord | None: ...
    def list(self, *, limit: int = 100, state: str | None = None) -> list[CandidateRecord]: ...


class InMemoryCandidateStore:
    """Test and staging store. It performs no network calls and stores no secrets."""

    def __init__(self) -> None:
        self._records: dict[str, CandidateRecord] = {}

    def upsert(self, record: CandidateRecord) -> CandidateRecord:
        if record.state not in ALLOWED_STATES:
            raise ValueError("unknown candidate state")
        existing = self._records.get(record.candidate_id)
        if existing:
            record.created_at = existing.created_at
        record.updated_at = _now()
        self._records[record.candidate_id] = record
        return record

    def ingest(self, candidates: Iterable[Candidate]) -> list[CandidateRecord]:
        result: list[CandidateRecord] = []
        for candidate in candidates:
            result.append(self.upsert(CandidateRecord.from_candidate(candidate)))
        return result

    def get(self, candidate_id: str) -> CandidateRecord | None:
        return self._records.get(candidate_id)

    def list(self, *, limit: int = 100, state: str | None = None) -> list[CandidateRecord]:
        limit = max(1, min(int(limit), 500))
        if state is not None and state not in ALLOWED_STATES:
            raise ValueError("unknown candidate state")
        records = list(self._records.values())
        if state is not None:
            records = [record for record in records if record.state == state]
        records.sort(key=lambda record: (record.updated_at, record.candidate_id), reverse=True)
        return records[:limit]
