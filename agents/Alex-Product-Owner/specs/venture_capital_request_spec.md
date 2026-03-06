# Feature: Venture Capital (Discovery)
**Goal:** Clarify what the user means by “venture capital” and produce a prioritized, scorable set of product opportunities and acceptance criteria so engineering and design can start implementation.

**North Star Impact:** Increase product-market fit by enabling an offering that drives adoption among founders and investors; target: >60% adoption among engaged users for the chosen feature within Q1 after launch.

**Users:**
- Founders raising capital (persona: early-stage founders, use case: find investors & manage fundraising)
- Investors/VCs (persona: angel/VC associates, use case: discover dealflow & manage LP pipelines)
- Platform admins (internal ops, use case: moderate listings, ensure compliance)

**Candidate Opportunities (MECE):**
1) Investor Directory & Matchmaking
   - Description: searchable investor profiles, tags (stage, sector, check size), and matching/recommendations for founders.
   - Reach estimate: 2,000 active founders / quarter
   - Impact: 1.5 (high) — reduces time-to-intro
   - Confidence: 60%
   - Effort: 4w
   - RICE ≈ (2000×1.5×0.6)/4 = 450
   - Kano: Performance

2) Fundraising Workflow (Pitch deck hosting, intro requests, one-click intro flow)
   - Description: structured fundraising flow: create rounds, share decks, request intros, track investor responses.
   - Reach: 1,200 founders / quarter
   - Impact: 2 (very high) — core revenue driver
   - Confidence: 55%
   - Effort: 8w
   - RICE ≈ (1200×2×0.55)/8 = 165
   - Kano: Must-have for marketplace

3) Dealflow Analytics & Signals for Investors (scoring, alerts, cohort analytics)
   - Description: analytics dashboard for investors to surface promising startups and monitor portfolio metrics.
   - Reach: 500 investors / quarter
   - Impact: 1 (medium)
   - Confidence: 50%
   - Effort: 6w
   - RICE ≈ (500×1×0.5)/6 ≈ 42
   - Kano: Delighter (for advanced users)

**Preliminary Recommendation (so what):**
- Prioritize: Investor Directory & Matchmaking (highest RICE; quicker to deliver; unlocks network effects).
- Next: Fundraising Workflow (requires more infra; high impact but higher effort).
- Defer: Dealflow Analytics (needs data volume and user base).

**Acceptance Criteria (for discovery artifact):**
- [ ] Clear decision: which product opportunity to pursue (from the 3 candidates) with rationale.
- [ ] Technical feasibility note: for chosen option, list required APIs, DB objects, scalability constraints.
- [ ] Design hooks: 3 initial screens/wireframes requested (landing, search, profile).
- [ ] Compliance/gating: list regulatory or privacy blockers (e.g., investor accreditation data handling).

**Out of Scope:**
- Full implementation work (this is discovery + spec + initial prioritization).
- Creating investor onboarding legal flows and payments.

**Success Metrics (post-launch):**
- Adoption: % of active founders using the feature > 60% in first 90 days
- Engagement: average sessions per user for feature > 3/week
- Conversion: % of introductions that lead to investor response > 25%

**Next steps:**
1. Technical feasibility assessment (backend) — estimate effort & list infra gaps.
2. Quick design exploration (3 wireframes) to validate UX assumptions.
3. Run 5 user interviews (founders/angels) to validate demand & refine acceptance criteria.

**GitHub Issue:** TBD (will create issue and attach here)
