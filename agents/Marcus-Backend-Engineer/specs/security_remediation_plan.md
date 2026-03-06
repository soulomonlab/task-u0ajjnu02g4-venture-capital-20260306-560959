# Backend Security Remediation Plan — PII & Injection Hardening

Author: Marcus (Backend)
Date: 2026-03-06

## Situation
Isabella completed a security review (output/reports/security_review_venture_capital.md) and flagged high-risk backend items: unclassified PII, lack of field-level encryption, missing strict input validation, raw SQL/parameterization gaps, and no secrets management.

## Objective
Deliver a concrete, reversible remediation plan covering:
- DB DDL updates to mark and store encrypted PII
- Field-level encryption design (application-level AES-GCM with KMS/Vault envelope keys)
- Input validation schema requirements for all existing endpoints
- ORM/parameterization enforcement and tests
- Secrets management guidance (Vault/KMS) and rollout steps

## Decisions (summary)
- Encryption: application-level AES-GCM per-field with per-record nonce; keys stored in Vault/KMS and only fetched by service at startup or via short-lived tokens.
- Storage: add bytea columns suffixed `_enc` for encrypted values; keep plaintext columns temporarily as `_plain` during migration; mark plaintext columns to be dropped after successful backfill and audit.
- Validation: use Pydantic models (FastAPI) with strict types, maxLength, regex patterns, formats, and forbid additionalProperties.
- DB Access: adopt SQLAlchemy ORM only; ban raw string interpolation for SQL. Any necessary raw SQL must use bind parameters and be reviewed.
- Secrets: integrate Vault (recommended) or KMS (GCP/AWS) with env var pointer and sidecar auth; never store plaintext keys in repo or env without vault agent.

## Files created (this task)
- output/specs/security_remediation_plan.md — this document
- output/code/backend/db/ddl.sql — updated DDL with PII annotations + migration statements
- output/docs/openapi_v1.yaml — updated OpenAPI with strict validation and x-pii markers
- output/code/backend/utils/field_encryption.py — encryption helper (AES-GCM) used by service

## Migration Plan (high level)
1. Deploy code that supports new `_enc` columns and reads/writes encrypted fields (backwards compatible): service reads plaintext if `_enc` NULL, but writes to `_enc` on update.
2. Add `_enc` columns via safe DB migration (non-blocking ADD COLUMN).
3. Run backfill job (batch, rate-limited) to encrypt existing plaintext into `_enc` columns. Track progress in a migration table.
4. After full backfill and QA verification, switch read path to prefer `_enc` and stop writing plaintext.
5. Drop plaintext `_plain` columns in a subsequent migration.

## Implementation Notes
- Use envelope encryption: data key (DEK) generated per-service stored encrypted by a KMS-wrapped key (KEK). DEKs cached in memory with TTL; keys rotated via KMS and rewrapped.
- Store metadata columns: `<field>_enc_version` integer, `<field>_enc_iv` bytea, to allow key rotation and algorithm upgrades.
- Ensure OpenTelemetry spans around encryption operations.

## Acceptance criteria
- SQL DDL includes PII annotations and `_enc` columns for all PII fields.
- OpenAPI schemas include validation (maxLength, pattern) and x-pii markers.
- Encryption helper is present and importable; service passes unit tests for encrypt/decrypt.
- 3 GitHub issues created: encrypt-PII, input-validation, DB-parameterization, secrets-management.

## Next steps (action items for owners)
- Marcus (me): implement code changes & migrations (this task) — done (files attached).
- Dana (#ai-qa): run QA tests for backfill, encryption correctness, validation rejection cases.
- Isabella (#ai-security): re-review the updated artifacts.

