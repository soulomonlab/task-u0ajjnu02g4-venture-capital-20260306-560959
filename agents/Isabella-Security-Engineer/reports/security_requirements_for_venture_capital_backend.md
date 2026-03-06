Title: Security Requirements & Threat Model — Venture Capital Backend

Situation
- Frontend requirements and API contract for the Venture Capital feature are finalized: output/specs/venture_capital_frontend_requirements.md
- Marcus must produce the backend feasibility doc. Security must be embedded in that doc to avoid rework and compliance gaps.

Complication
- The feature exposes public discovery plus user-driven actions (bookmark, express interest). These mix public and sensitive flows that create risks for PII leakage, abuse (spam/DoS), injection attacks, and unauthorized access if not designed correctly.

Resolution (Deliverable)
- This file lists the security requirements, threat model (STRIDE), OWASP Top-10 checklist, privacy blockers, recommended controls, and per-item effort estimates that Marcus must include in the backend feasibility doc.

1) High-level assets
- Venture profiles (public fields + restricted fields)
- User accounts & tokens
- Contact/expression-of-interest submissions
- Media (logos, pitch decks)
- Database backups, logs, and analytics

2) Top threats (STRIDE) — prioritized
- Spoofing: stolen JWTs or replayed refresh tokens → unauthorized actions (bookmark/express_interest)
- Tampering: unauthorized edits to venture data, malicious uploads (malware in pitch_deck)
- Repudiation: insufficient audit logs for user/admin actions
- Information disclosure: PII leaks (emails/phones) in API responses, logs, or backups
- Denial of Service: high-volume search or express_interest spam impacting availability
- Elevation of privilege: broken access control allowing curator/admin actions

3) OWASP/Platform checklist (apply to every API and DB interaction)
- Authentication & Session Management
  - JWT access tokens: expiry 15 minutes; refresh tokens: 7 days; rotation on refresh; store refresh tokens server-side (or use http-only secure cookies with CSRF protections).
  - Implement token revocation list (support logout/revocation).
  - Use strong signing keys (RSA-2048 or HMAC-SHA256 with 256-bit secret) and rotate keys quarterly.
- Authorization
  - Enforce least-privilege RBAC: is_admin, is_curator, is_user. Validate server-side for every privileged endpoint.
  - Deny-by-default for admin/curation endpoints; never rely on frontend flags.
- Input validation & Injection
  - Parameterize DB queries or use ORM properly. No string concatenation for queries.
  - Sanitize/whitelist search filter inputs; rate-limit wildcard search inputs.
  - Escape or sanitize markdown rendering on detail view to prevent XSS — use safe markdown libraries and CSP.
- Data Protection
  - Do not return email/phone in public endpoints by default. Contact flow must be mediated server-side.
  - Encrypt sensitive PII at rest (field-level AES-256) and use KMS/Vault for keys.
  - TLS 1.2+ (prefer 1.3) mandatory for all endpoints and services. HSTS enabled.
- Media & Uploads
  - Scan uploads (pitch_deck_url destination) for malware. Serve media from signed URLs or CDN with access controls for non-public assets.
- Logging & Audit
  - Audit log for admin/curation actions, express_interest submissions, bookmark events (user id + timestamp); redact PII in logs; ensure immutability/append-only.
  - Log access to PII fields and store access logs for GDPR/soc2 purposes.
- Rate Limiting & Abuse Prevention
  - Global and per-endpoint rate limits (e.g., express_interest: per-user per-day limits, IP throttling).
  - CAPTCHA or email verification for express_interest if spam observed.
- Secrets Management & CI/CD
  - No secrets in repo; use Vault or cloud KMS; provide .env.example (no secrets).
  - CI pipeline must run SAST (Bandit for Python), dependency scans (Snyk/OSS), container scans (Trivy), and run unit tests.
- Monitoring & Incident Response
  - Alerting for anomalous rates, error spikes, auth failures. Define playbooks for P0 incidents and data breaches.
- Testing
  - Include security-focused tests: SAST, DAST, auth integration tests, and one integration test verifying PII is not exposed in public endpoints.

4) Privacy blockers & GDPR-specific controls
- Consent flags and lawful basis for storing user-submitted messages. Track consent timestamp and source.
- Right to erasure: provide backend endpoint to soft-delete or redact PII and ensure removal from analytics/backups within retention SLA.
- Data minimization: only persist fields required for workflows. E.g., store user_id for bookmarks; avoid storing user messages longer than necessary unless consented.
- Data transfer: if using third-party services (search engine, CDN), ensure data processing agreements and data residency requirements.

5) Secure API design notes (map to frontend endpoints)
- GET /api/v1/ventures (list)
  - Public read: OK for non-PII fields. Add ETag/Last-Modified. Sanitize query params. Use cursor pagination; protect heavy search with rate limits and require API key for advanced searches.
- GET /api/v1/ventures/{id}
  - Return public fields only. Include public_contact_allowed flag (boolean). If contact allowed, do NOT return actual contact details.
- POST /api/v1/ventures/{id}/express_interest
  - Auth required. Validate message content length & sanitize. Enforce per-user and per-venture rate limits. Queue delivery (async), redact sender PII to the recipient where needed. Record an audit event.
- POST /api/v1/ventures/{id}/bookmark
  - Auth required. Idempotent implementation. Store minimal metadata; audit when bookmarks are deleted.

6) Infrastructure & deployment controls
- Network: DB in private subnet, application in private VPC with load balancer. Restrict DB access at SG level.
- Secrets: use Vault/KMS for DB credentials, JWT signing keys, third-party API keys.
- Backups: encrypted at rest, access audited, retention policy consistent with privacy policy.
- CI/CD: require PR scans; disallow merging on critical SAST findings.

7) Scalability bottlenecks that have security implications
- Search/indexing (Elasticsearch/OpenSearch)
  - Risk: open indices leaking data. Mitigation: private network access, auth proxy, and query rate limits. Consider storing minimal PII in search index.
- Asynchronous workflows (email/notifications)
  - Risk: queue poisoning or replay. Use signed messages, idempotency, and rate limits.
- Media CDN
  - Risk: exposing non-public pitch decks. Use signed URLs with short TTL for private assets.

8) Effort estimates (for backend feasibility doc) — small/medium/large
- Auth middleware (JWT with rotation + revocation): Medium
- RBAC and admin guardrails: Small
- Input validation & parameterized queries across endpoints: Small
- Field-level encryption for PII and KMS integration: Medium
- Secrets management (Vault/KMS integration + .env cleanup): Small
- Logging/audit pipeline (append-only logs, retention): Medium
- Rate limiting & WAF rules (including per-endpoint caps): Medium
- Malware scanning for uploads and secure media delivery (signed URLs + CDN): Medium
- SAST/DAST & CI pipeline integration (Bandit, Snyk, Trivy): Small
- Threat model & incident response playbook completion: Small
- GDPR flows (consent tracking, erase endpoint, backup retention): Medium
- Harden search platform (auth proxy, private indices): Medium

9) Acceptance criteria (security gate for feasibility doc)
- All HIGH risks either designed out or have a clear mitigation and owner.
- JWT & session design documented (expiry, rotation, revocation).
- PII classification table present (which fields are PII, storage/encryption decisions).
- Data flow diagram showing where PII leaves system (CDN, search, third-parties) and controls for each flow.
- CI pipeline runs SAST + dependency scans; failing builds for critical findings.

10) Deliverable checklist for Marcus to include in output/specs/venture_capital_backend_feasibility.md
- API spec with security annotations (auth required, rate limits)
- DB schema with PII markers and encryption approach
- Infra components and security controls (VPC, secrets, logging)
- Scalability bottlenecks + security mitigations
- Privacy blockers and GDPR remediation plan
- Per-feature effort estimates (use list in section 8)

Prepared by: Isabella (Security Engineer)
Date: 2026-03-06
