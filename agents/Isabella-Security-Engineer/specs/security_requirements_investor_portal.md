Title: Security Requirements — Investor / Venture Capital Engagement Portal
Filename: output/specs/security_requirements_investor_portal.md

Scope
- Feature: Time-limited, permissioned VC links + read-only KPI/materials dashboard

Authentication & Session
- Require authenticated founder users for portal creation. Investors may access via permissioned link or optional invited account.
- Sessions: if authenticated, use secure HttpOnly SameSite=strict cookies for session tokens.
- JWT if used: short-lived access token (15 min), refresh token rotation with refresh expiry 7 days. Store refresh tokens server-side (hashed).

Link Tokens
- Tokens must be cryptographically random with >=256 bits entropy, URL-safe base64.
- Store only token hash (HMAC-SHA256 with server-side secret) in DB.
- Token metadata: owner_id, allowed_emails (optional), expiry timestamp, single_use boolean, revoked boolean.
- Expiry: default 24 hours; allow founders to set shorter (min 1 hour, max 7 days with business sign-off).
- Token validation: constant-time comparison; check owner and resource access.

Authorization
- Enforce server-side authorization for every resource. Use RBAC + attribute-based access control for link-scoped permissions.
- Deny-by-default: explicit allow rules only.
- API endpoints must perform both authentication and authorization checks.

Uploads & Storage
- Validate file types and reject executables. Accept whitelist: pdf, png, jpg, pptx (with content scanning pipeline).
- Strip active content from office documents; convert uploaded docs to safe PDF for viewing.
- Store files in private object storage (S3) and serve via signed URLs with short TTL (minutes).
- Set Content-Disposition: attachment to force download when necessary.
- Scan uploads in CI using antivirus/Trivy; quarantine failures.

Transport & Caching
- Enforce TLS 1.2+ with strong cipher suites. HSTS header set for secure domains.
- Set Cache-Control: no-store on pages that display PII or sensitive financial info; use no-cache for API responses with sensitive data.
- Set Referrer-Policy: no-referrer or strict-origin-when-cross-origin on sensitive pages.

Frontend Controls
- Implement CSP to mitigate XSS (restrict sources, disallow inline scripts/styles where possible).
- Sanitize any user-controlled content rendered on pages.
- Watermark documents with viewer email and timestamp for audit deterrence.

Logging & Monitoring
- Log access to link tokens and dashboards with user (or anonymous token id), IP, UA, timestamp.
- Retain logs for 90 days; ensure logs are immutable/write-once where possible.
- Alert on anomalous access patterns (multiple IPs, high frequency for same token).

Secrets & Key Management
- Use Vault or cloud KMS for secrets (HMAC keys, DB credentials). Do not store secrets in repo or .env in production.
- Rotate HMAC and encryption keys at least every 90 days. Maintain key IDs in DB for re-hashing if needed.

Testing & CI
- Add automated tests for IDOR, token expiry, and permission elevation.
- Run SAST (Bandit, Semgrep), dependency checks (Snyk/Dependabot), and container scanning (Trivy) in CI.

Operational
- Provide founder controls to revoke links immediately and to view access logs for their links.
- Rate-limit token lookup and dashboard endpoints per IP and per owner.
- Implement account lockout for suspicious auth behavior.

GDPR & Privacy
- Minimize PII exposure on dashboards; mask fields where possible.
- Provide data retention policy and deletion process for uploaded materials and logs.

Acceptance Criteria (Security)
- No HIGH issues open in security review before release.
- Automated tests cover token misuse scenarios.
- Secrets are stored in Vault/KMS in production.

Next Steps
- #ai-design — Review design artifacts for leaks of sensitive info (watermark, caching, screenshots) and apply mitigations in Figma.
- #ai-backend — Implement token hashing, expiry, and server-side authorization checks. See output/code/security for middleware.

