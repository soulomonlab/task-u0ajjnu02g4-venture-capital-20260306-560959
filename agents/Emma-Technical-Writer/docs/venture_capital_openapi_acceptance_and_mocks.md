# Venture Capital API — OpenAPI Acceptance & Mocking Checklist

Overview
- Purpose: Provide a precise OpenAPI v3 acceptance checklist and example request/response shapes so backend can deliver an OpenAPI spec and mock server that exactly match frontend expectations.
- Audience: Marcus (Backend), Kevin (Frontend), Chris (Customer Success), Emma (Docs).

What we need from Backend (deliverables)
1. OpenAPI v3 document (YAML or JSON) implementing the endpoints and shapes below.
2. Mock server (e.g., via Prism, mockoon, or generated Swagger mock) that returns the example success/error responses exactly as specified.
3. Example opaque cursor value(s) used in pagination responses and list requests.
4. Example pre-signed URLs for export/job flow (PUT for upload & GET for download) with sample response bodies.
5. Confirmation on casing convention (camelCase vs snake_case) and whether approxTotal (approximate total count) is available in list responses.

Key constraints (from frontend requirements)
- Cursor-based pagination: query params: cursor, limit. Defaults: limit=20. Max limit=100.
- Casing: frontend expects camelCase (confirm with backend). All request/response fields MUST use agreed casing.
- Error envelope: consistent envelope with HTTP status code + JSON body {error: {code, message, details?}}.
- Autocomplete debounce: 300ms (frontend will debounce); backend should support idempotent, fast queries.
- Optimistic UI: some endpoints will be updated optimistically by frontend — API should return stable ids and eventual state.
- PII handling: any fields containing PII must be marked and documented; endpoints returning PII must require proper auth and audit logging.

Endpoint templates & examples

1) List Ventures (cursor-based pagination)
- HTTP: GET /api/v1/ventures
- Query params: cursor (opaque string), limit (integer)
- Default: limit=20. Max: 100.
- Success response (200):
{
  "data": [
    {
      "id": "vc_01F...",
      "name": "Acme Ventures",
      "industry": "SaaS",
      "foundedAt": "2018-07-12",
      "hq": "San Francisco, CA"
    }
  ],
  "paging": {
    "nextCursor": "eyJjdXJzb3IiOiJhYmNk...", // opaque cursor string
    "limit": 20,
    "approxTotal": 1023 // OPTIONAL: include only if available — confirm with backend
  }
}

Notes:
- The cursor value must be opaque (not a visible page number). Provide at least one sample opaque cursor value in mocks.
- If there is no next page, paging.nextCursor must be null or omitted (pick one and document; frontend expects null when no next page).

2) Get Venture (detail)
- HTTP: GET /api/v1/ventures/{id}
- Path param: id (venture id string)
- Success response (200):
{
  "data": {
    "id": "vc_01F...",
    "name": "Acme Ventures",
    "industry": "SaaS",
    "description": "Early-stage VC focusing on developer tools.",
    "foundedAt": "2018-07-12",
    "hq": "San Francisco, CA",
    "contactEmail": "contact@acme.vc" // PII: mark this field in spec
  }
}

3) Autocomplete (debounced)
- HTTP: GET /api/v1/ventures/autocomplete?q=term
- Frontend will debounce 300ms. Backend must return fast, and support cancel/retry semantics.
- Success response (200):
{
  "data": [
    {"id": "vc_01F...", "name": "Acme Ventures"}
  ]
}

4) Export / Job Flow (pre-signed URLs)
- POST /api/v1/exports
  - Request: {"type": "ventures_csv", "filter": {...}}
  - Success (202 Accepted):
{
  "data": {
    "jobId": "job_123",
    "status": "pending"
  }
}
- GET /api/v1/exports/{jobId}
  - Success when ready (200):
{
  "data": {
    "jobId": "job_123",
    "status": "completed",
    "result": {
      "downloadUrl": "https://storage.example.com/abc?signature=...",
      "expiresAt": "2026-03-15T12:34:56Z"
    }
  }
}
- Presigned PUT example (if frontend needs to upload):
{
  "data": {
    "uploadUrl": "https://storage.example.com/upload/abc?signature=...",
    "fields": { /* if POST form uploads are used */ }
  }
}

Error envelope (always JSON)
- HTTP status codes should be meaningful (400, 401, 403, 404, 429, 500).
- Body shape (example):
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "`q` must be at least 2 characters",
    "details": [
      {"field": "q", "reason": "too_short"}
    ]
  }
}

Notes:
- Include standardized error codes (string enums) in the OpenAPI spec.
- For rate limit (429) include Retry-After header in seconds.

Casing & Field Naming
- Frontend expects camelCase. Backend to confirm and return fields in camelCase in the OpenAPI doc and mocks.
- If backend prefers snake_case internally, ensure the API contract uses camelCase or provide a clear migration plan.

PII & Security
- Mark which fields are PII in the schema (e.g., contactEmail). Indicate which endpoints return PII and require elevated scopes.
- Document required auth scopes per endpoint in OpenAPI (e.g., scope: ventures.read, ventures.export).

Mocks & Examples Requirements
- Mocks must return the exact JSON field names, types, and envelope shapes above.
- Provide at least one sample opaque cursor string and demonstrate:
  - list with nextCursor present
  - list with nextCursor null (end)
- Provide example error responses for common error cases (400 validation, 401 unauthorized, 403 forbidden, 404 not found, 429 rate limit, 500 server error).
- Provide example presigned URL responses for both upload and download flows.

OpenAPI-specific requirements
- Use OpenAPI v3.0+.
- Include schema components for shared objects (e.g., Venture, PagingEnvelope, ErrorEnvelope).
- Provide example objects for each response and error code in the spec (examples field).
- Indicate which fields are readOnly/writeOnly where applicable.
- Add securitySchemes (Bearer auth + scopes).

Acceptance criteria (what QA/Frontend will validate)
- [ ] OpenAPI v3 file delivered and parses with a standard linter (spectral/openapi-generator).
- [ ] Mock server (URL or instructions) available and returns the example responses.
- [ ] Cursor pagination behavior matches: limit default 20, max 100; nextCursor opaque; no nextCursor -> null.
- [ ] Error envelopes and HTTP codes match examples.
- [ ] Presigned URL examples provided for upload/download flows.
- [ ] All fields use confirmed casing (camelCase) in spec and mocks.
- [ ] PII fields are documented with required scopes and marked in schema.
- [ ] Backend confirms whether approxTotal is available; if yes, include in paging. If no, remove approxTotal from examples.

Questions for backend (must be answered in the OpenAPI PR)
1. Confirm response casing: camelCase vs snake_case. (Frontend expects camelCase.)
2. Is approxTotal available or computable cheaply? If yes, include as integer in paging; if no, omit.
3. For paging.nextCursor when no next page: prefer null or omitted? Frontend expects null. Please adopt null.
4. Which auth scopes map to which endpoints? Provide in securitySchemes.
5. Provide at least one sample opaque cursor string and examples of how it changes between pages.

How to deliver
- Push OpenAPI file to the backend repo (e.g., openapi/venture_capital_api.yaml).
- Provide a running mock server URL (staging) or instructions to run locally (docker-compose or npm script).
- Add a short README in the OpenAPI PR describing how to run the mock server and where examples are located.

Review & Sign-off
- Once OpenAPI + mocks are available, backend must notify Docs (Emma) and Frontend (Kevin). Docs will run a quick compliance check against the acceptance criteria and mark items done.

---
Generated by Emma (Technical Writer) — output/docs/venture_capital_openapi_acceptance_and_mocks.md
