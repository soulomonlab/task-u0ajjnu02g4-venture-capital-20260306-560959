# Venture Capital — API Review & Frontend Confirmation

Overview
- Purpose: Provide a concise review document for frontend (Kevin) to confirm API surface, required fields, pagination, response/error formats, and UX-driven needs so backend (Marcus) can generate the OpenAPI spec and API mocks.
- Source: backend feasibility doc: output/specs/venture_capital_backend_feasibility.md (Marcus)

Quick context
- Marcus produced a backend feasibility doc with API surface, Postgres sketch, infra, privacy blockers, and ~14 backend days effort estimate.
- This document highlights questions and examples needed from the frontend to finalize the API contract and build mocks.

What I need from Kevin (frontend) — checklist (answer each item)
1) Endpoint confirmation
   - Confirm the list of endpoints we will use (add/remove). If an endpoint differs from Marcus's proposal, describe the change.
   - Example expected endpoints (please confirm or edit):
     - GET /api/v1/ventures — list ventures (explore/browse)
     - GET /api/v1/ventures/{id} — venture detail
     - POST /api/v1/ventures — create venture (internal/admin)
     - GET /api/v1/portfolio — user's portfolio / saved ventures
     - POST /api/v1/ventures/{id}/notes — add note/comment
     - GET /api/v1/search — search ventures (filters)

2) Required fields & shapes
   - For each resource (venture, portfolio item, note), confirm required fields and example values. For example, Venture summary:
     - id: uuid
     - name: string (required)
     - short_description: string (required)
     - stage: enum (seed, series_a, series_b, growth)
     - industries: [string]
     - location: {city, country, timezone?}
     - founded_at: date
     - metrics: {revenue_mrr, employees}
   - Indicate which fields are optional, which are admin-only, and which contain PII that must be redacted/encrypted.

3) Pagination & list behavior
   - Choose pagination style: offset (page, limit) or cursor-based (next_cursor). Recommend cursor for scalability; confirm which you want.
   - Default page size and max page size.
   - Sorting: default sort (e.g., relevance, newest, trending). Which sort keys are required?
   - Response list envelope: do you want {data: [...], meta: {...}} (recommended)?

4) Filtering & search requirements
   - Which filters do you need on list/search endpoints (stage, industry, location, min_employees, raised_min, tags)?
   - Faceting requirements (counts by industry/stage)?
   - Search behavior: full-text on name+description? fuzzy matching? spell-correction?

5) Response & error format
   - Standard response envelope (confirm):
     - Success: 200/201 with body {data: ..., meta?: ...}
     - Errors: follow RFC7807 or app-specific {error: {code, message, fields?: {...}}}
   - Which error codes and messages should be surfaced to users vs. internal logs?
   - Timezone format for timestamps (ISO 8601 UTC recommended).

6) Authentication & authorization
   - Auth type: Bearer token (JWT) or session cookie? (Marcus assumed Bearer/JWT.)
   - Granular permissions: which endpoints require admin vs authenticated user vs public access?

7) UX-driven concerns
   - Real-time updates: do you need websockets or polling for live updates (e.g., portfolio changes)?
   - Bulk actions: will frontend need endpoints for bulk-import/export or batch update?
   - Rate limits you expect for normal users vs power users.

8) Mock data needs
   - Provide 3 example ventures (minimal fields + full fields) for building UI mocks.
   - Any edge-case examples: very long descriptions, missing fields, non-ASCII characters, very large arrays.

9) Accessibility & localization
   - Supported locales and which fields need translation.
   - Any client-side formatting expectations (dates, numbers, currency).

Acceptance criteria
- Kevin provides a filled checklist (can be inline replies) that confirms:
  - Endpoint list and required fields for each resource
  - Pagination style + defaults
  - Response envelope + error format
  - Any additional UX-driven endpoints or behavior
- Once confirmed, Marcus will produce an OpenAPI spec and API mocks.

Next steps timeline
- Kevin review: 2 business days preferred
- Marcus OpenAPI spec & mocks: follow-on (Marcus estimated ~14 backend days for implementation)

Document author: Emma (Technical Writer)
Date: 2026-03-06

