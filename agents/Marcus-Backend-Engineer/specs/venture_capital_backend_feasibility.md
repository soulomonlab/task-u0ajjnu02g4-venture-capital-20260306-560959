# Venture Capital Backend — Feasibility & Security-Annotated Spec

## Situation
Kevin provided the frontend API contract and requested a backend feasibility document. Security requirements must be embedded to prevent PII leaks, auth/abuse gaps, and compliance issues.

## Complication
The backend must annotate each endpoint with concrete auth, rate-limiting, and data-classification requirements, plus a DB schema with PII flags and actionable infra controls. Effort must be mapped to implementable backend tasks.

## Resolution (deliverable)
This document annotates the API contract with security controls, defines PII classification for the DB schema, lists infra/security controls (VPC, KMS/Vault, backups, logging), and maps effort estimates to discrete backend tasks.

---

## 1) High-level decisions (Marcus)
- Auth: JWT access tokens (Bearer) 15m, refresh tokens 7d with rotation. OAuth2 client credentials for service-to-service. RBAC: roles = [public, user, investor, admin].
- Rate limiting: global per-account + per-IP. Default: 100 requests/min per user, 20 requests/min per IP for unauthenticated endpoints. Burstable with token bucket.
- PII handling: classify columns as [PII_HIGH, PII_MEDIUM, PII_LOW, NON_PII]. PII_HIGH requires encryption-at-rest with KMS-managed keys and field-level encryption in transit+at-rest.
- Observability: OpenTelemetry tracing on every API, redaction of PII from logs, structured logs with request_id.
- Compliance: GDPR-focused data subject deletion flow and data export endpoint (authenticated, rate-limited, logged).

## 2) API endpoints (annotated)
Format:
| Method | Path | Description | Auth | Rate-limit (per user) | Notes (PII / actions) |

| POST | /api/v1/auth/login | User login (email/password) | Public | 30 req/min per IP | Accepts email (PII_HIGH). Mask logs; store only salted hash. 2FA optional (future). |
| POST | /api/v1/auth/refresh | Rotate refresh token | Bearer (refresh) | 60 req/day per user | Refresh rotation; revoke on reuse. |
| POST | /api/v1/users | Create user | Bearer (admin) | 10 req/min per user | Payload includes email (PII_HIGH), name (PII_MEDIUM). Validate & encrypt at rest. |
| GET | /api/v1/users/:id | Get user by id | Bearer (admin, self) | 100 req/min | Response includes PII_HIGH fields only for allowed roles. Redact in logs. |
| GET | /api/v1/deals | List deals | Bearer (user, investor) | 200 req/min | Non-PII listing. Apply pagination. Cacheable (public fields only). |
| POST | /api/v1/deals | Create deal | Bearer (investor) | 50 req/min | Contains financial data (PII_MEDIUM). Store with encryption-at-rest; validate owner. Idempotency key required. |
| GET | /api/v1/deals/:id | Get deal | Bearer (user, investor) | 200 req/min | Some fields may be PII_MEDIUM. Access control enforced. |
| POST | /api/v1/documents/upload | Upload doc (investor DD) | Bearer (investor) | 20 req/min | File storage: S3 private bucket, server-side encryption with KMS. Scan for sensitive data (DLP) asynchronously. |
| GET | /api/v1/reports/export | Export user data (GDPR) | Bearer (admin, self) | 5 req/day per user | Must generate time-limited signed URL, audit logged, requires explicit consent check. |

Notes:
- All mutation endpoints require idempotency-key header for at-least-once safe operations.
- All endpoints must validate JSON schema strictly and return standardized error format {code, message, details}.

## 3) Database schema (summary) — PII classification
Schema below is illustrative; final schema to be normalized in implementation phase.

Tables:
- users
  - id (UUID) — NON_PI
  - email (text) — PII_HIGH (encrypt_at_rest=true)
  - password_hash (text) — NON_PI (bcrypt)
  - full_name (text) — PII_MEDIUM (encrypt_at_rest=false, redact_in_logs=true)
  - phone (text) — PII_HIGH (encrypt_at_rest=true)
  - role (enum) — NON_PI
  - created_at, updated_at — NON_PI

- deals
  - id (UUID) — NON_PI
  - title (text) — NON_PI
  - description (text) — PII_LOW
  - financials (jsonb) — PII_MEDIUM (encrypt_at_rest=true as needed)
  - owner_id (UUID fk users.id) — NON_PI
  - created_at, updated_at — NON_PI

- documents
  - id (UUID) — NON_PI
  - deal_id (UUID) — NON_PI
  - filename (text) — NON_PI
  - s3_key (text) — NON_PI
  - dlp_scan_status (enum) — NON_PI
  - uploaded_by (UUID) — NON_PI
  - created_at — NON_PI

Encryption guidance:
- PII_HIGH fields: use field-level encryption via application using KMS-managed keys before DB write OR use Postgres column-level encryption with pgcrypto and KMS-wrapped keys.
- Use envelope encryption; never store raw keys in env.

Retention & deletion:
- Soft-delete pattern with deleted_at + background purge that runs policy-based deletion (e.g., after 30d for trial data, configurable). Implement DSAR (data subject access request) flow.

## 4) Infra & security controls (concrete)
- Network: VPC-only private DB subnets; no public DB endpoints. Bastion host + OIDC to prod-only admins.
- Secrets: Use Vault or Cloud KMS; never ENV secrets in code. Rotate keys quarterly (automate via CI/CD secrets rotation job).
- Storage: S3 buckets private, SSE-KMS encryption, bucket policies to restrict by VPC endpoint.
- Backups: Automated encrypted backups, immutable retention policy 30-90 days per compliance. Test restore quarterly.
- Logging & monitoring: Structured logs, redact PII, centralize to SIEM. Retention 90 days; export alerts to PagerDuty.
- DLP: Asynchronous DLP job (Celery) for uploaded docs; quarantine documents flagged as leaking PII.
- IAM: Least-privilege service accounts, short-lived credentials, Open Policy Agent (OPA) for fine-grained authorization if needed.
- Rate-limit enforcement: Edge (API gateway) + app-level middleware, with dynamic throttling per account tier.
- Audit: All administrative actions, data exports, and auth events must be audited and immutable (append-only log).

## 5) Observability & tracing
- OpenTelemetry auto-instrumentation for FastAPI; propagate request_id and user_id (hashed) in traces.
- Span on DB calls and DLP jobs. Alert on >200ms DB queries, >500ms API latency.

## 6) Effort estimates mapped to backend tasks (P1 priority mapping)
Note: estimate scale = small (1-3d), medium (1-2 weeks), large (3-6 weeks).

Tasks:
1) Auth system (JWT + refresh rotation, RBAC enforcement) — medium
   - Implement token issuance, refresh rotation, blacklist on reuse, roles middleware, unit tests.
2) Field-level encryption for PII_HIGH fields — large
   - Integrate KMS/Vault, envelope encryption, migrate existing data, key management policies.
3) Rate-limiting middleware + gateway config — medium
   - Implement token-bucket, per-user and per-IP, integrate with Redis for counters.
4) DB schema with PII classification + migrations (Alembic) — small
   - Add column flags and encryption markers, create indexes for common queries.
5) Document upload pipeline + DLP integration — medium
   - S3 signed URLs, Celery workers for DLP, quarantine workflow.
6) GDPR export & deletion flow — medium
   - Export generator, signed temp URLs, audit log, deletion background job.
7) Observability & OTEL spans — small
   - Add tracing, request_id propagation, metrics (p95/p99), dashboards.
8) Backup + restore verification + infra hardening — medium
   - Automated backup, restore runbook, infra as code changes (VPC, policies).
9) Logging redaction & SIEM integration — small
   - Implement log redactors, structured logs, forwarder to SIEM.

## 7) Acceptance criteria (for backend tasks)
- All endpoints pass contract tests from frontend (JSON schema + sample payloads).
- PII_HIGH data is stored encrypted; logs contain no raw PII.
- auth: successful refresh rotation; reuse detected and revoked.
- Rate-limit enforced at both edge and app; test load shows limits work.
- DLP quarantines flagged docs and notifies admins.
- Backup restore tested successfully on staging.

## 8) Risks & mitigations
- Risk: Key compromise → Mitigation: KMS with rotation and least-privilege; if suspected, rotate keys and revoke tokens.
- Risk: Performance regressions from encryption → Mitigation: benchmark, cache decrypted results when safe, move heavy operations to background jobs.
- Risk: Incomplete PII discovery → Mitigation: add periodic data scans, developer training, CI-scan for schema changes.

---

## Next steps (technical)
1) Implement tasks 1,4,7 in first sprint (Auth, DB schema flags, Observability) — these reduce blast radius and enable secure work on the rest.
2) Create detailed tickets per task with acceptance tests and owners.

