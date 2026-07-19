BEGIN;

CREATE TABLE IF NOT EXISTS source_candidate (
    candidate_id TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    canonical_url TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    discovery_source TEXT NOT NULL,
    discovery_tier INTEGER NOT NULL CHECK (discovery_tier BETWEEN 0 AND 3),
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    state TEXT NOT NULL DEFAULT 'DISCOVERED',
    risk_class TEXT NOT NULL DEFAULT 'R0_PUBLIC_READ_ONLY',
    score INTEGER CHECK (score BETWEEN 0 AND 100),
    recommendation TEXT,
    hard_fail_reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
    official_url TEXT,
    decision_reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (canonical_url, discovery_source, discovery_tier)
);

ALTER TABLE source_candidate
    ADD COLUMN IF NOT EXISTS metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

CREATE INDEX IF NOT EXISTS source_candidate_state_idx ON source_candidate (state, updated_at DESC);
CREATE INDEX IF NOT EXISTS source_candidate_canonical_url_idx ON source_candidate (canonical_url);

CREATE TABLE IF NOT EXISTS source_verification (
    verification_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES source_candidate(candidate_id) ON DELETE CASCADE,
    verification_type TEXT NOT NULL,
    status TEXT NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    limits JSONB NOT NULL DEFAULT '{}'::jsonb,
    verified_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS source_verification_candidate_idx ON source_verification (candidate_id, verified_at DESC);

CREATE TABLE IF NOT EXISTS integration_decision (
    decision_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES source_candidate(candidate_id) ON DELETE CASCADE,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL,
    approval_reference TEXT,
    rollback_reference TEXT,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS integration_decision_candidate_idx ON integration_decision (candidate_id, decided_at DESC);

CREATE TABLE IF NOT EXISTS source_watch (
    watch_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL REFERENCES source_candidate(candidate_id) ON DELETE CASCADE,
    watch_type TEXT NOT NULL,
    last_value_hash TEXT,
    last_checked_at TIMESTAMPTZ,
    next_check_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'PENDING',
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS source_watch_due_idx ON source_watch (status, next_check_at);

COMMIT;
