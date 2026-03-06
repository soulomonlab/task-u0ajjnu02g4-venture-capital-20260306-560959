Title: Threat Model — Venture Capital Feature
Date: 2026-03-06
Author: Isabella (Security Engineer)

Overview
- This document applies STRIDE to the Venture Capital discovery + express_interest contact flow described in output/specs/venture_capital_backend_feasibility.md.
- Focus: PII handling (founder contact), public discovery surface, backend-mediated contact flow, and observability.

Assets
1. Public venture listing (non-PII): name, description, sectors, logos, public website
2. Founder contact PII: email, phone, personal LinkedIn, other direct contact data
3. Express interest events: user_id, venture_id, timestamp, message body
4. Internal curation queue: curator accounts, metadata, PII references
5. Audit logs, traces, backups

Assumptions / Constraints
- Public responses must not contain founder PII.
- express_interest may either: (A) send direct emails to founders, or (B) route expressions to an internal curation queue for manual mediation.
- Database: Postgres with FTS for search (v1). Cursor pagination preferred.
- Observability: OpenTelemetry in use; do not log raw PII.

STRIDE Analysis (per asset)
1) Spoofing (identity)
- Threat: Attacker impersonates curator or admin to access PII or trigger contact flows.
- Likelihood: MED
- Impact: HIGH
- Controls: MFA for curator/admin accounts; mutual TLS for service-to-service; use short-lived tokens and rotate keys.

2) Tampering (data integrity)
- Threat: Unauthorized modification of express_interest messages or founder contact details.
- Likelihood: LOW-MED
- Impact: MED
- Controls: RBAC, DB constraints, field-level encryption, signed audit logs (append-only), input validation.

3) Repudiation
- Threat: Users or curators deny actions (e.g., who sent the express_interest email).
- Likelihood: MED
- Impact: MED
- Controls: Immutable audit logs with user_id, timestamp, and action details; retention per compliance.

4) Information Disclosure
- Threat: Founder contact PII leaked via public API response, logs, search index, or debug traces.
- Likelihood: MED
- Impact: HIGH
- Controls: Do not index PII into FTS; mask/omit PII in public responses; application-level encryption for contact fields; scrub PII from logs and traces; access controls on backups and snapshots.

5) Denial of Service
- Threat: Abuse of express_interest to flood founder inbox or curation queue; search endpoints abused for enumeration.
- Likelihood: MED
- Impact: MED
- Controls: Rate limiting, CAPTCHAs for public forms, queuing with worker backpressure, pagination limits, anomaly detection.

6) Elevation of Privilege
- Threat: Regular user gains curator/admin privileges to view PII or perform contact actions.
- Likelihood: LOW
- Impact: HIGH
- Controls: Principle of least privilege, role separation, periodic entitlement review, logging of privilege changes.

Top Risks (sorted)
- HIGH: Information Disclosure — PII exposure via API, logs, or search (requires immediate mitigations).
- HIGH: Spoofing of curator/admin accounts leading to PII access.
- MED: Abuse/DoS of express_interest leading to spam or operational overload.

Mitigations (mapped to implementation guidance)
1. PII Storage & Access
   - Decision: Founder contact fields MUST NOT appear in public API responses.
   - Store contact PII encrypted-at-rest with application-level envelope encryption (AES-256-GCM) using keys stored in Vault.
   - Use per-environment key ring and optionally per-tenant (per-venture) keys if multi-tenant separation required.
   - DB schema: contact_email_encrypted (bytea), contact_phone_encrypted (bytea), contact_plaintext_hash (text, optional for search/matching), consent_flags (JSONB), consent_timestamp (timestamptz).
   - Access: only curator and authorized backend service components may decrypt; enforce via RBAC and service identity.

2. Contact Flow (express_interest)
   - If policy = direct_email: backend composes outbound email via internal Mailer service; the Mailer service should fetch decrypted contact and send; rate-limit per venture and per founder.
   - If policy = curation_queue: store the sanitized express_interest event (no PII) referencing an encrypted contact pointer; curators see decrypted contact via curator UI after MFA and authorization checks.
   - Recommendation: Default to curation_queue for launch (reduces PII exposure). If direct_email is required, implement strict anti-abuse and consent checks.

3. Logging & Observability
   - Prohibit logging of raw PII (email/phone/content). Implement log scrubbing at ingestion (e.g., log pipeline filters).
   - Traces: use OpenTelemetry but mark PII fields as sensitive and ensure sampling/retention policies do not leak.
   - Audit logs must record who accessed/decrypted PII and why; store audit logs in an append-only store with 6–12 months retention by default (configurable).

4. Search & Indexing
   - Do NOT index contact fields into Postgres FTS or external search (Algolia/Elastic) unless hashed/tokenized and consent exists.
   - Allow hashed contact matching (e.g., sha256 normalized email) for deduplication/search inside private flows; never store unhashed plaintext in search indexes.

5. Data Minimization & Consent (GDPR)
   - Capture explicit consent when storing founder contact details: consent_flags = {"contact_allowed": true, "purpose": "introductions"} and consent_timestamp.
   - Support data subject requests: retrieval, rectification, erasure. Erasure should scrub decrypted fields, revoke keys if necessary (documented erasure flow required).
   - Retention: default 12 months for contact PII unless shorter retention requested; configurable per-venture.

6. Key Management
   - Use Vault (or cloud KMS) for key storage and KMS envelope encryption.
   - Keys: rotate every 90 days; maintain ability to re-encrypt DB columns via migration workflows.
   - Limit key access: only backend service accounts and Vault policies for curator UI should have decrypt permissions.

7. Operational Controls
   - Require MFA for curator/admin console; log all admin actions.
   - Rate limiting on express_interest endpoint and anti-bot measures on public forms.
   - Backups: ensure DB backups are encrypted and access-controlled; redact PII in analytics exports.

Acceptance Criteria (security gate)
- No HIGH risks open. For GDPR-sensitive storage, confirm consent capture implemented and documented.
- Founder PII never included in public API responses or public search indexes.
- Field-level encryption in place for contact PII (or documented mitigation if deferred) + key management plan.
- Audit logging of PII access implemented and verified.

Appendix: Quick DB field sketch
- ventures(id UUID PK, name text, description text, ...)
- venture_contacts(id UUID PK, venture_id FK, contact_label text, contact_email_encrypted bytea, contact_phone_encrypted bytea, contact_plaintext_hash text, consent_flags jsonb, consent_timestamp timestamptz, created_at timestamptz)

References
- OWASP Top 10
- GDPR Art. 6, 17 (lawful processing, right to erasure)
- NIST SP 800-57 (key management)

Prepared by: Isabella
