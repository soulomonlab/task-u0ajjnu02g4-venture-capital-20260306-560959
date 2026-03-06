# Frontend requirements & API questions — Venture Capital Product

Status: Draft
Owner: Kevin (Frontend)
Related product decisions: output/specs/venture_capital_product_decisions.md
Related backend feasibility: output/specs/venture_capital_backend_feasibility.md

Situation
- Product has finalized PII retention/deletion policy and search QPS sizing (MEDIUM: 200 QPS baseline, autoscale to 2,000 QPS).
- Backend work (PII handling, DB schema, search) is planned by Marcus and is blocking frontend implementation for search and PII-sensitive views.

Purpose
- Document frontend requirements, acceptance criteria, and concrete API contract questions we need Marcus/backend to confirm before frontend implementation begins.

Key assumptions
- Auth uses JWT (frontend will store in memory + secure cookie for refresh). Confirm token shape and expiry.
- RBAC will be provided by backend via roles/permissions on user payload or separate endpoint.
- Backend will indicate which fields are PII and what redaction state they are in (raw | redacted | deleted).

Required API endpoints (frontend expectations)
1. GET /api/v1/search
   - Query params: q (string), page (number) OR cursor (string), per_page (number)
   - Response: { results: SearchResult[], total_count?: number, next_cursor?: string }
   - Must include rate-limit headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
   - Questions: prefer page/limit or cursor? Is total_count provided for pagination UI?

2. GET /api/v1/users/:id
   - Returns user profile including PII metadata fields: { id, name, email?, pii_status: { email: 'raw'|'redacted'|'deleted' }, ... }
   - Questions: which fields are considered PII and how is pii_status represented?

3. POST /api/v1/pii/deletion-requests
   - Payload: { resource_type, resource_id, requester_id }
   - Response: { request_id, status }
   - Questions: workflow for deletion requests? webhook/callback on completion?

4. RBAC & auth
   - Endpoint or claim that exposes roles/permissions for current user. If roles affect which PII is visible, frontend needs role names and allowed actions.

5. Search tuning & autoscaling
   - Given QPS sizing, will backend return HTTP 429 on throttling? Any retry recommendations or backoff headers?

6. Error contract
   - All endpoints must return structured errors: { code: string, message: string, details?: object }

TypeScript interfaces (frontend stubs)
- SearchResult
  interface SearchResult {
    id: string;
    type: string;
    title: string;
    snippet?: string;
    pii_meta?: { [field: string]: 'raw' | 'redacted' | 'deleted' };
  }

- APIError
  interface APIError { code: string; message: string; details?: Record<string, any> }

Acceptance criteria (for frontend integration)
- Search UI displays results with clear PII indicators and a tooltip explaining redaction/deletion state.
- Pagination works with either page-based or cursor-based approach confirmed by backend.
- If PII is deleted, the UI must show a non-reversible notice and disable actions that would expose deleted data.
- Error states: network error, 429 rate limit, 500 server error — all must show accessible error UI and retry option where appropriate.
- Unit tests + integration tests (React Testing Library) for SearchList and PII display logic.

Mock responses (examples)
- Search (page-based)
  {
    "results": [
      { "id": "u_123", "type": "user", "title": "Jane Doe", "pii_meta": { "email": "redacted" } }
    ],
    "total_count": 123
  }

- User profile
  {
    "id": "u_123",
    "name": "Jane Doe",
    "email": null,
    "pii_meta": { "email": "deleted", "phone": "raw" }
  }

Questions for Marcus / backend (items requiring confirmation)
1. Pagination: page/limit OR cursor + do you provide total_count? (UI needs to know for 'showing results x-y of N')
2. Exact search endpoint path and query param names.
3. Concrete JSON schema for search results and user profile (list of PII fields and pii_meta representation).
4. RBAC: endpoint or JWT claim name for roles; canonical role strings.
5. Error and rate-limit headers and behavior on throttling (429). Recommended client retry/backoff policy.
6. Webhook or async completion signal for long-running deletion operations?
7. CORS, auth header name, and whether refresh tokens use httpOnly cookie.

Planned frontend deliverables (after backend confirms)
- components/SearchBar.tsx
- components/SearchList.tsx
- components/PIIStatus.tsx
- hooks/useSearch.ts (with debounce 300ms, cancellation, typing-safe responses)
- types/api.ts (TypeScript interfaces)
- tests/Search.integration.test.tsx

Estimated frontend dev effort (dependent on API stability)
- Implementation: 3 dev-days (search UI + PII handling)
- Tests & polish: 1 dev-day

Next steps for backend (what frontend needs from Marcus)
- Confirm the questions above and provide example JSON payloads for each endpoint.
- Create GH issues for the API endpoints with contracts or link to the issues so frontend can track.
- Provide ETA for when the endpoints will be available in a dev environment.

