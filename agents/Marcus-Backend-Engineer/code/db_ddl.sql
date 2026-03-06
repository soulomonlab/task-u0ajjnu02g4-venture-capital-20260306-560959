-- Updated DDL with PII annotations and encrypted columns
-- File: output/code/backend/db/ddl.sql

-- Example: users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_plain TEXT, -- PII: email (temporary plaintext column)
    email_enc BYTEA, -- encrypted email (AES-GCM)
    email_enc_iv BYTEA,
    email_enc_version INTEGER DEFAULT 1,
    full_name_plain TEXT, -- PII: name (temporary)
    full_name_enc BYTEA,
    full_name_enc_iv BYTEA,
    full_name_enc_version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- PII classification metadata (for DBA/tools)
COMMENT ON COLUMN users.email_plain IS 'PII: email; data_classification=PII; retention_policy=7y; encrypt=application_aes_gcm';
COMMENT ON COLUMN users.email_enc IS 'PII: encrypted_email; encryption=application_aes_gcm; stores_ciphertext';
COMMENT ON COLUMN users.full_name_plain IS 'PII: full_name; data_classification=PII; retention_policy=7y; encrypt=application_aes_gcm';
COMMENT ON COLUMN users.full_name_enc IS 'PII: encrypted_full_name; encryption=application_aes_gcm; stores_ciphertext';

-- Migration helper table to track backfill status
CREATE TABLE IF NOT EXISTS pii_migrations (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    status TEXT NOT NULL, -- pending|in_progress|completed|failed
    processed_rows BIGINT DEFAULT 0,
    total_rows BIGINT DEFAULT 0,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

-- Indexes for performance on non-PII lookup fields
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Notes:
-- - After backfill and verification, drop *_plain columns in a later migration.
-- - For searching on PII fields, implement deterministic tokenization or indexed hash columns (store SHA256(email) as indexed column) rather than decrypting and scanning.

