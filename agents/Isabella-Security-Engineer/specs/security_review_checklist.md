Security Review Checklist — Investor Portal
Filename: output/specs/security_review_checklist.md

Purpose
- Baseline checklist for design & implementation reviews against OWASP Top 10, GDPR, and internal security requirements.

Design Phase Checks
- [ ] No sensitive tokens in visible URLs or query strings in wireframes
- [ ] Screens that show PII have watermark and explicit no-export hints
- [ ] Export/Download flows show Content-Disposition and warning about sharing
- [ ] Design shows age/expiry of links and a visible revoke button
- [ ] Session/Logout UX described for shared device scenarios

Frontend Implementation
- [ ] CSP defined in design tokens
- [ ] Referrer-Policy set to no-referrer or strict-origin-when-cross-origin
- [ ] Cache-Control: no-store on sensitive pages
- [ ] Inputs are validated and escaped where rendered

Backend/API
- [ ] Tokens stored only as hashed values
- [ ] Token metadata (expiry, owner_id, allowed_emails) implemented
- [ ] Authorization checks exist on every endpoint (no security by obscurity)
- [ ] File uploads scanned and stored privately; served via signed URLs
- [ ] Rate-limiting and WAF rules defined

CI/CD & DevOps
- [ ] Secrets stored in Vault/KMS; .env not used in production
- [ ] SAST & dependency scanning in CI
- [ ] Container images scanned (Trivy) and minimized

Operational
- [ ] Access logs tracked and retained 90 days
- [ ] Alerting on anomalous access patterns
- [ ] Playbook for revocation and breach notification

Acceptance
- [ ] All HIGH issues addressed before release
- [ ] Tests for IDOR and token misuse

