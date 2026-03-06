# Feature: Investor / Venture Capital Engagement Portal
**Goal:** Provide a secure, investor-facing portal and starter materials so our founders can efficiently engage VCs and VCs can evaluate the company with curated, up-to-date metrics.

**North Star Impact:** Reduces time-to-term by improving investor access to reliable metrics and materials; expected to increase successful intro→term conversion rate.

**Users:**
- VCs (evaluators) — need fast, credible access to metrics and materials.
- Founders / Investor Relations — need a frictionless way to share live metrics and materials.

**RICE Score:** Reach=50 × Impact=2 × Confidence=70% / Effort=4w = 17.5 (≈18)

**Kano Category:** Performance

**Acceptance Criteria:**
- [ ] Founders can create an investor-access link that is time-limited and permission-scoped.
- [ ] VCs visiting the link see a read-only dashboard with latest KPIs (MAU, revenue, growth, churn) and downloadable materials (pitch, cap table snapshot).
- [ ] Dashboard loads under 1.5s for typical payload; API response <200ms for KPI endpoints under normal load.
- [ ] Audit log created for each access (who, when, what files downloaded).
- [ ] Access revocation works immediately and invalidates existing links.
- [ ] Mobile and desktop responsive (core flows usable on mobile).

**Out of Scope:**
- Full CRM integration / rich investor relationship management (will iterate in a later epic).
- Automated investor matching / marketplace.

**Success Metrics:**
- # of investor links created per quarter.
- Median time from first investor access to signed term sheet (tracked manually initially).
- Investor satisfaction score (post-access survey) ≥ 4/5.

**GitHub Issue:** TBD
