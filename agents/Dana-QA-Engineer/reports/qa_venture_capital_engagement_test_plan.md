QA Test Plan — Investor / Venture Capital Engagement Portal

Overview
- Objective: Validate that founders can create time-limited, permissioned investor links and that VCs can view a read-only KPI/materials dashboard with auditability, revocation, and acceptable performance.
- Quality gates: >90% automated test coverage for API surface; P0/P1 defects block sign-off; performance for KPI endpoints <200ms (API) and dashboard <1.5s (page load) under normal load.

Scope (measured against spec acceptance criteria)
- Create investor-access link (time-limited, permissioned)
- Read-only dashboard content and downloads
- Audit logging for accesses and downloads
- Immediate revocation of links
- Mobile and desktop responsiveness (core flows)
- Performance: KPI endpoints and dashboard load times

Test Strategy
1. API Integration Tests (automated):
   - Positive flows: create link, access dashboard, download material, revoke link, verify audit log
   - Negative flows: expired token, revoked token, malformed token, permission escalation attempts
   - Security edge cases: token brute-forcing attempt (rate limiting), link enumeration attempts
   - Performance assertions: measure API latency for KPI endpoints

2. End-to-End UI Tests (automation recommended):
   - Dashboard renders on desktop and mobile breakpoints
   - Ensure UI is read-only: no form fields that persist changes, buttons for download only
   - Accessibility smoke: keyboard nav to key elements, presence of ARIA labels on key components

3. Unit Tests (automated):
   - Token generation & expiry logic
   - Permissions enforcement for resources
   - Audit log entry creation and schema validation

4. Manual Exploratory Tests:
   - UX corner cases (slow network, intermittent load)
   - Role confusion (founder vs guest) and error messaging

Test Cases (high priority)
- TC-API-001 CreateLink: POST /api/investor_links -> 201, response contains token, expiry
- TC-API-002 DashboardReadOnly: GET /dashboard?token=... -> 200, JSON contains KPIs+materials, POST/PUT => 4xx
- TC-API-003 RevokeLink: DELETE /api/investor_links/{id} -> 204; subsequent GET dashboard -> 401/404
- TC-API-004 AuditLog: After access, GET /api/audit_logs?link_id=... -> entry with timestamp, actor, action
- TC-API-005 Expiry: After expiry period, GET dashboard -> 401/403
- TC-API-006 PerformanceKPI: GET /api/kpis -> latency < 200ms (normal load)
- TC-UI-001 Responsive: Dashboard renders and core flows work at 360x800 and 1280x800

Risk Assessment
- High: Token handling (expiry / revocation) — security and correctness critical.
- High: Audit log completeness — regulatory/forensics risk if missing fields.
- Medium: Performance under load — KPI endpoints must stay <200ms; caching may be required.
- Medium: File download security — ensure signed URLs or scoped access.

Automation Plan & Deliverables
- Deliver automated API tests: output/tests/test_investor_portal_api.py
- Deliver QA test plan & checklist: output/reports/qa_venture_capital_engagement_test_plan.md (this file)
- Provide test run reports under output/reports/ after CI runs

Acceptance Criteria for QA Sign-off
- All automated tests pass in CI
- Test coverage for the feature >= 90%
- No P1/P0 defects found
- Performance gate: KPI endpoints meet latency targets in staging

Notes / Next actions for engineering
- Provide a staging base URL (INVESTOR_PORTAL_URL) and API contract (request/response schemas) so integration tests can run in CI.
- Provide authentication for test fixtures (service account or test tokens) and a teardown endpoint to clean test artifacts.

Prepared by: Dana (QA)
Date: 2026-03-06
