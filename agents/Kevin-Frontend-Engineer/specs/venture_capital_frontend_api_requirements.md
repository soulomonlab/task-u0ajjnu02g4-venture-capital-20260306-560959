# Venture Capital PRD — Frontend API requirements (Kevin)

Core ask
- Review backend API surface and confirm required fields, pagination params, response/error formats, and UX-driven requirements so backend can produce OpenAPI + mocks.

Decision summary (top-line)
- Pagination: cursor-based pagination for lists used in infinite-scroll (param: cursor, limit). Default limit=20, max=100. Provide `totalCount` only when cheap; otherwise provide `approxTotal` or omit.
- Field casing: Prefer camelCase in JSON responses to minimize client mapping. If backend returns snake_case, provide a consistent mapping contract.
- Error format: Standard error envelope: { error: { code: string, message: string, fields?: Record<string,string> } } and use appropriate HTTP status codes (400,401,403,404,429,500).
- Time formats: ISO 8601 UTC strings (e.g. 2025-03-01T12:00:00Z).
- Authentication: Bearer token in Authorization header; endpoints return 401/403 as appropriate.

API endpoints (confirmed / requested fields)
1) GET /api/v1/companies
- Purpose: list companies (feed / search results / discovery).
- Query params:
  - limit: integer (default 20, max 100)
  - cursor: string (opaque cursor token; absent => first page)
  - search: string (full-text search across name, shortDescription)
  - sortBy: string (createdAt, updatedAt, amountRaised)
  - sortOrder: string (asc|desc)
  - sectors: comma-separated strings
  - stage: string (seed, series_a, series_b, etc.)
  - minAmount / maxAmount: integer (cents)
  - location: string
- Response (200):
  {
    data: [ { id, name, slug, shortDescription, logoUrl, stage, sectors[], amountRaisedCents, currency, foundedAt, createdAt, updatedAt } ],
    meta: { nextCursor?: string, approxTotal?: number }
  }
- Notes: `nextCursor` opaque token for subsequent calls. `approxTotal` optional (avoid exact counts for large tables).

2) GET /api/v1/companies/{companyId}
- Purpose: single company detail page.
- Response fields (200):
  {
    id, name, slug, description, logoUrl, headerImageUrl?, websiteUrl?, stage, sectors[], founders: [ { id, name, role, profileUrl? } ], amountRaisedCents, currency, fundingRounds[], createdAt, updatedAt
  }
- PII: founders' personal email or phone must only be returned if user has proper consent / permissions. If returned, mark fields as encrypted at rest.

3) POST /api/v1/favorites
- Purpose: bookmark/favorite a company (optimistic UI action)
- Body: { resourceType: "company", resourceId: string }
- Response: 201 { id, resourceType, resourceId, createdAt }
- Notes: Support idempotency: repeated calls should not error (return existing favorite).

4) GET /api/v1/search/autocomplete
- Purpose: incremental search suggestions.
- Query params: q (string), limit (default 10)
- Response: { suggestions: [ { id, type: 'company'|'investor', text, slug } ] }
- UX: debounce 300ms on client; cancel in-flight requests when q changes.

5) POST /api/v1/exports
- Purpose: request CSV/JSON export of current filtered view (async).
- Body: { resource: 'companies', filters: { ... }, format: 'csv'|'json' }
- Response 202 { jobId }
- Poll GET /api/v1/jobs/{jobId} → { status, resultUrl? } When done, resultUrl is a pre-signed S3 URL.

Common field types (frontend expectations)
- id: UUID (string)
- dates: ISO8601 UTC (string)
- amounts: integer in cents (avoid floats). Provide currency ISO code (e.g., USD).
- urls: absolute HTTPS URLs or null
- arrays: empty array instead of null
- optional fields: omitted or null — prefer null for explicitness

Response envelope & error handling
- Success wrapper (list/item): { data: ..., meta?: ... }
- Error wrapper: HTTP status + body:
  {
    error: { code: string, message: string, fields?: { <field>: "message" } }
  }
- 429 responses must include Retry-After header (seconds). Client should display a friendly message and retry after delay.

Pagination trade-offs & recommendation
- Cursor-based + limit: best for infinite scroll and stable lists. Backend should emit opaque cursor tokens (base64 of cursor state) and avoid exposing DB offsets.
- Provide `approxTotal` only if counting is expensive. If an exact total is required for UX (page numbers), backend should support offset pagination for those endpoints.

UX-driven requirements (frontend behavior driven by API design)
- Search debounce: 300ms.
- Optimistic updates: for favorites/bookmarks and follow/unfollow actions. Backend must support idempotency and return a canonical representation.
- Loading states: provide skeleton variants for list and detail views. API should return light preview fields for list to avoid overfetching.
- Client caching: cache list pages for 60s; provide ETag/Last-Modified for detail endpoints to support conditional requests.
- Image handling: backend should return image URLs with width/height or support query params for size. If not possible, frontend must handle layout shifts.
- Accessibility: error messages delivered via aria-live regions; interactive elements must be reachable by keyboard and have aria-labels.

Performance & pragmatic notes for backend (so frontend can be performant)
- Provide small preview DTO for list endpoints (avoid sending full `description`).
- Offer separate endpoints for large rich-media fields (e.g., /companies/{id}/media) or include a `contentSize` hint.
- Provide rate-limit headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset.

Client-side type expectations (TypeScript)
- Backend should document types in OpenAPI with camelCase property names (id: string, name: string, foundedAt?: string, amountRaisedCents?: number).

Acceptance criteria for OpenAPI + mocks (what I need from backend)
1. OpenAPI v3 (JSON or YAML) that matches the shapes above and declares camelCase properties.
2. Sample responses for success and error cases (200,201,400,401,404,429,500).
3. Cursor pagination implementation detail (what the cursor encodes) and an example cursor value.
4. Job/export flow endpoints with example pre-signed URLs.
5. Rate-limit headers and Retry-After behavior documented.
6. PII fields (founder email/phone) flagged with required consent/auth checks.

Questions / open decisions for backend
- Are we able to return camelCase JSON directly, or will responses be snake_case? I prefer camelCase.
- Can the backend include `approxTotal` or `totalCount` for lists, or must we avoid counts for performance?
- For image URLs: will the backend support size query params or separate CDN endpoints?

References
- Time format: ISO8601 UTC
- Amounts: integer cents

Next step (frontend)
- I reviewed & produced this confirmation doc. Backend should produce OpenAPI + API mocks implementing the items in "Acceptance criteria".

