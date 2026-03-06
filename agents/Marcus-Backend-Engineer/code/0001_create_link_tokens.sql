-- Migration: create link_tokens table

CREATE TABLE IF NOT EXISTS link_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_hash TEXT NOT NULL,
    owner_id UUID NOT NULL,
    allowed_emails TEXT[],
    metadata JSONB,
    expiry TIMESTAMPTZ NOT NULL,
    single_use BOOLEAN NOT NULL DEFAULT FALSE,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_link_tokens_token_hash ON link_tokens (token_hash);
CREATE INDEX IF NOT EXISTS idx_link_tokens_owner_id ON link_tokens (owner_id);
CREATE INDEX IF NOT EXISTS idx_link_tokens_revoked ON link_tokens (revoked);
