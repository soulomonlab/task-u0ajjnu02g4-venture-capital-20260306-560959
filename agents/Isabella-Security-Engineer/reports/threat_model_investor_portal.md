Title: Threat Model — Investor / Venture Capital Engagement Portal
Filename: output/reports/threat_model_investor_portal.md

Scope
- Feature: Time-limited, permissioned VC links + read-only KPI/materials dashboard
- Actors: Founder (owner), Investor (viewer), Admin, Unauthenticated third-party, Attacker
- Assets:
  - VC links (tokens/URLs)
  - Dashboard data (KPIs, PII, financials)
  - Uploaded materials (PDFs, pitch decks)
  - User accounts & session tokens
  - Audit logs
  - Backend API and DB
  - CDN / file storage

Method: STRIDE applied per asset

Top Threats (prioritized)
1) Information Disclosure (HIGH)
   - Threat: Token leakage via Referer headers, logs, shared screenshots, open redirects.
   - Impact: Unauthorized access to dashboards or materials containing PII/financials.
   - Likelihood: High if links are carried in URLs and shared.
   - Mitigations:
     - Avoid placing long-lived secrets in query strings. Prefer short opaque IDs + server-side permission check.
     - If tokens in URLs are required, make them single-use or very short-lived (<24h) and store only hashed token server-side (SHA-256/HMAC).
     - Use Referrer-Policy: no-referrer or strict-origin-when-cross-origin on pages that render sensitive content.
     - Apply Content-Security-Policy (CSP) and disable browser caching (Cache-Control: no-store) for pages with PII.
     - Watermark documents with viewer info and timestamp to deter sharing.

2) Broken Access Control / Elevation of Privilege (HIGH)
   - Threat: URL tampering or missing/incorrect authorization checks allowing access to other founders' dashboards.
   - Impact: Data breach, regulatory exposure (GDPR), reputational damage.
   - Mitigations:
     - Enforce server-side authorization checks on every request (resource + action). Do not rely on front-end checks.
     - Use least-privilege RBAC (roles: owner, investor_viewer, admin) and attribute-based checks for link-scoped permissions.
     - Include link-scoped metadata in DB (owner_id, allowed_emails, expiry, one_time_use flag).
     - Add automated tests for IDOR (insecure direct object reference).

3) Tampering / Insecure Uploads (MED-HIGH)
   - Threat: Malicious files uploaded and served to investors (XSS via SVG, JS in docs), or malware distribution.
   - Impact: Client compromise, legal exposure.
   - Mitigations:
     - Sanitize and validate uploads; disallow executable content types.
     - Serve files from separate domain/subdomain or signed URLs with Content-Disposition: attachment to force download.
     - Scan uploads with antivirus/Trivy/Sniffers in CI before making available.
     - Restrict accepted file types and strip active content from documents (e.g., remove macros in Office files).

4) Spoofing / Token Forgery (MED)
   - Threat: Predictable or weak token generation allowing attackers to guess valid links.
   - Impact: Unauthorized access.
   - Mitigations:
     - Use cryptographically secure random tokens (>=256 bits entropy) encoded URL-safe.
     - Store only hashed token server-side (HMAC-SHA256) and compare in constant time.
     - Rate-limit token-lookup endpoints and block suspicious IPs.

5) DoS / Resource Exhaustion (MED)
   - Threat: API or storage abuse by crawling many links or uploading large files.
   - Impact: Availability degradation, increased costs.
   - Mitigations:
     - Rate-limit per-IP and per-user, use WAF rules for suspicious patterns.
     - Enforce file size limits, upload quotas, and background processing queues for heavy work.

Auditability & Detect
- Log every access to a VC link and dashboard view: user (if authenticated), originating IP, user-agent, timestamp, resource id.
- Store logs immutable for at least 90 days; alert on anomalous access patterns (multiple different IPs for same link in short time).

Privacy / Compliance (GDPR)
- Minimize PII displayed. Provide data retention policy for uploaded materials.
- Support owner-initiated revocation & deletion (Right to be Forgotten). Ensure audit logs do not leak PII or are redacted.
- Maintain breach notification process and contact details.

Risk Acceptance & Residuals
- Acceptable if: server-side auth is enforced, tokens are ephemeral/hashed, uploads sanitized, and audit logging is in place.
- Residual risk: social engineering (screenshot sharing) — mitigated with watermarking and short expiry but not eliminable.

Deliverables / Next actions
- Convert mitigations into actionable requirements for API, DB, and frontend teams (see security_requirements file).
- Security review of final design and Figma assets for leaking sensitive info.
