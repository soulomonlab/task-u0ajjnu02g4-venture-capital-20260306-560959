QA Pre-Implementation Test Plan — DB Schema & PII Handling

Purpose
- Provide a measurable, automatable QA plan focused on DB schema, PII retention/deletion, encryption/RBAC, and search scalability (200 QPS baseline, autoscale to 2000 QPS).

Scope
- Schema correctness (tables, columns, types, constraints)
- Migration idempotency and reversibility
- PII retention & deletion: time-based deletion, manual deletion, logical vs physical deletion
- Encryption at rest for sensitive fields and access controls (RBAC)
- Search indexing and query performance characteristics
- Backup/restore and data integrity

Acceptance criteria (measurable)
- All automated tests pass locally and in CI for schema-related functionality
- PII deletion: given deletion event, records are removed/irreversibly anonymized within SLA (documented in product decisions)
- Encryption: verification tests confirm encrypted columns are not stored in plaintext and decryption works for authorized roles
- RBAC: unauthorized roles cannot access PII fields (negative tests)
- Migration: applying migrations twice is idempotent; rolling back works for dev environments
- Performance: Search baseline 200 QPS pass under simulated load; autoscale path verified with stress-tests in staging
- Coverage goal: >90% of DB schema and PII test cases automated

Test types and representative test cases
1) Schema verification (unit/integration)
   - Test: expected tables exist (users, investors, investments, audit_logs)
   - Test: PII columns present with correct types (e.g., ssn_hash, email_encrypted, created_at)
   - Test: NOT NULL and unique constraints enforced (e.g., email unique)
   - Test: indexes exist for search columns (e.g., name, company_name)

2) Migrations
   - Test: migrations apply cleanly on a fresh DB
   - Test: migrations are idempotent (apply twice -> no-op second time)
   - Test: rollback of last migration restores previous schema

3) PII retention & deletion
   - Test: retention policy enforces deletion/anonymization after TTL
   - Test: manual deletion endpoint triggers deletion and deletes related records where required
   - Test: deletion is irreversible for physical deletion policy; for soft-delete, anonymization of PII fields is validated
   - Test: audit entries created for deletion events

4) Encryption & keys
   - Test: encrypted columns are not plaintext in DB
   - Test: decryption only works with proper key and authorized service account
   - Test: key rotation process doesn't break decryption for existing data (migration test)

5) RBAC & access control
   - Test: role without 'view_pii' cannot access PII columns via API or direct DB queries (integration test with API layer)
   - Test: elevated role can access PII

6) Search & performance
   - Test: basic search queries return correct results (functional)
   - Load test: 200 QPS baseline sustained with < p95 latency target (to be defined by product)
   - Autoscaling test: simulate spikes up to 2,000 QPS in staging and verify system autoscale behavior

7) Backup/Restore & Data Integrity
   - Test: nightly backup process produces restorable snapshots
   - Test: restore of a backup restores expected row counts and constraints

Test data and fixtures
- Require realistic synthetic dataset with PII and non-PII variants
- Fixtures for multiple roles and authorization tokens
- Database connection string for CI: use ephemeral DB service or containerized DB

Automation plan
- Unit & integration tests in pytest under output/tests/
- Load tests in separate tool (locust/k6) with scripts in output/tests/load/
- CI: run schema tests on PRs; run load tests in staging pipeline

Dependencies and blockers for QA
- Marcus must create GH issues and implement DB schema & migrations
- Provide migration scripts, sample fixtures, and dev/staging DB endpoints
- Provide encryption key management plan or test key for QA

Deliverables created
- output/tests/db_schema_test_plan.md (this document)
- output/tests/test_db_schema.py (test skeletons and placeholders)

Next steps for backend (what I need from Marcus)
1) Create GH issues for each backend subtask (migrations, encryption, RBAC, search, backup)
2) Share dev/staging DB connection info and migration artifacts
3) Provide test key or key-management stub for encryption verification
4) Notify QA when a DB schema PR is ready for automated tests to run
