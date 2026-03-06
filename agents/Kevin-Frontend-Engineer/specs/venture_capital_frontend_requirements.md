# Venture Capital — Frontend Requirements & API Contract (Kevin)

## Situation
Alex has created the discovery PRD for the "venture capital" feature. Engineering needs backend feasibility & effort estimates before design and implementation can begin. Frontend must specify what data and API shapes it needs so backend can estimate and design appropriately.

## Objective
Provide a clear, minimal, and actionable API contract and frontend acceptance criteria to enable Marcus to produce the backend feasibility doc (APIs, DB sketch, infra, scalability, privacy blockers, effort estimates).

## High-level UI surface (for alignment)
- List view: searchable, filterable, paginated list of venture profiles.
- Detail view: full profile with metrics, founder(s), fundraising history, documents/links.
- Action(s): Save/Bookmark, Express interest (contact request), Share.
- Admin/curation panel (future): flagging, edit metadata.

## Key data requirements (per venture)
- id (string)
- name (string)
- short_description (string, 140 chars)
- full_description (string, markdown/html optional)
- sectors (string[])
- stage (enum: pre-seed, seed, series_a, series_b, growth)
- location (string, country/state)
- headline_metrics: { metric_name: string, value: string | number }
- fundraising: { raised_amount: number, currency: string, last_round_date: ISO8601 }
- founders: [{ id, name, title, public_profile_url }]  // NO PII like email/phone exposed by default
- logo_url (string)
- website_url, pitch_deck_url, demo_url
- tags (string[])
- created_at, updated_at

## Required API endpoints (frontend needs these to implement flows)
1) GET /api/v1/ventures
- Query params: q (search), sectors[], stage[], location, tags[], sort (relevance|newest|raised), page_size (<=100), cursor (optional)
- Returns: { items: Venture[], next_cursor?: string, total_count?: number }
- Notes: Prefer cursor-based pagination for scalability; frontend can accept page-based if backend prefers.

2) GET /api/v1/ventures/{id}
- Returns: full Venture object (fields above). Include `public_contact_allowed: boolean` to indicate if contact info or express-interest flow is permitted.

3) POST /api/v1/ventures/{id}/express_interest
- Body: { user_id, message? }
- Returns: 202 Accepted or 200 with outcome
- Notes: This triggers backend workflows (email/notification); frontend shows success/failure states.

4) POST /api/v1/ventures/{id}/bookmark
- Body: { user_id }
- Returns: 200 / 201

5) GET /api/v1/ventures/stats
- Returns aggregated metrics for dashboard (optional for MVP)

## Response shape example (list)
{
  "items": [
    {
      "id": "vc_123",
      "name": "Acme Robotics",
      "short_description": "Autonomous warehouse robots",
      "logo_url": "https://...",
      "sectors": ["robotics","logistics"],
      "stage": "series_a",
      "headline_metrics": [{"metric_name":"ARR","value":"$2.1M"}],
      "created_at": "2025-09-01T12:00:00Z"
    }
  ],
  "next_cursor": "abc123",
  "total_count": 234
}

## Performance & SLAs (frontend expectations)
- List endpoint: p95 latency < 300ms for cached queries, < 1s for cold queries.
- Support page_size up to 50 for reasonable UX.
- Provide CDN-able logo_url and caching headers for media.

## Auth & Authorization
- Auth: JWT access token in Authorization header for user-specific actions (bookmark, express_interest).
- Public read-only list: allow unauthenticated read for discovery (depends on privacy). If not allowed, specify.
- Role-based flags: `is_admin`, `is_curator` for admin endpoints.

## Privacy & PII constraints (frontend decisions relying on backend)
- DO NOT return email/phone in public GET /ventures or /ventures/{id}.
- If contact flow is allowed, backend should mediate (send email, or provide masked contact) and return only allowed signals (e.g., contact_sent: true).
- GDPR: provide flags for consent/remove requests. Frontend needs endpoints to request deletion/soft-redaction.

## Caching & Scalability
- Backend should provide ETag/Last-Modified for venture detail for efficient caching.
- Cursor pagination recommended. Backend should support filtering indexes (sectors, stage) to keep list queries fast.

## Error states (frontend must handle)
- 4xx: 400 (bad filter), 401 (auth), 403 (access denied), 404 (not found)
- 429: rate-limited — frontend should show retry affordance
- 5xx: show friendly error and retry path

## Acceptance criteria for frontend (MVP)
- List view: displays first page of ventures, search and filtering works, pagination (infinite scroll or load more) implemented.
- Detail view: displays full profile, Express Interest button submits and shows success/error.
- Bookmark action persists per user.
- Loading, empty, and error states covered and accessible (keyboard + aria).
- Backend provides endpoints above and returns response shapes compatible with examples.

## Trade-offs / Decisions front-end prefers
- Cursor pagination for scalability (reversible if backend chooses offset)
- Minimal public data to protect PII; contact flows mediated by backend

## Next step for Backend (requested deliverable)
Marcus to produce: output/specs/venture_capital_backend_feasibility.md — include APIs (with param details), DB schema sketch, infra components, scalability bottlenecks, privacy blockers, and effort estimates (small/medium/large per piece).


Prepared by: Kevin (Frontend)
Date: 2026-03-06
