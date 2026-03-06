Title: Request for Backend Confirmation — express_interest API & PII handling

Context
- Source: frontend position + API contract requirements created by Kevin: output/specs/frontend_contact_flow_review.md
- Purpose: Provide a concise, actionable list of backend confirmations required for frontend implementation of the contact/express_interest flow (list, modal, queued state, polling/webhook).

Summary — what this doc requests
1) Privacy / PII handling confirmation (what data is permitted in public venture objects; acceptable identifiers)
2) express_interest API schema (request/response fields, status model)
3) Rate-limiting & idempotency (limits, retry semantics, idempotency keys)
4) Status update strategy (polling endpoint vs webhook events; recommended payloads)

Details & proposed defaults (frontend assumptions)
- Public Venture shape (frontend assumption): Public venture objects are PII-free and include only non-sensitive metadata.
  - Allowed fields: id (uuid), name, industry, headline, short_description, logo_url, public_website, location_region (non-granular), tags, created_at.
  - Disallowed fields (PII): founder names, personal emails, phone numbers, home addresses, birthdates, gov IDs.
  - Request: confirm that backend will guarantee no PII in public venture objects and provide the definitive public schema (JSON) we should use.

- express_interest API (frontend proposal)
  - Endpoint: POST /api/v1/ventures/{venture_id}/express_interest
  - Purpose: Record a user-driven expression of interest in a venture without including PII for the public venture object.
  - Request body (proposed):
    {
      "user_id": "<uuid>",              // internal user id (not exposed in public venture payload)
      "intent": "contact|follow|ask_question", // optional enum
      "message": "<optional short message>",   // optional, max 1000 chars, server will sanitize
      "idempotency_key": "<optional-uuid>"     // recommended for client retry
    }
  - Response (accepted immediate):
    HTTP 202 Accepted
    {
      "interest_id": "<uuid>",
      "venture_id": "<uuid>",
      "status": "queued",          // queued | processing | delivered | failed
      "received_at": "2024-01-01T00:00:00Z"
    }
  - Error responses: 400 (validation), 401 (auth), 403 (permission), 429 (rate limit), 500
  - Request: confirm the exact request/response schema and the recommended status enum values.

- Rate-limiting and idempotency (frontend needs clear contract)
  - Proposed default limits: 60 requests per minute per user for express_interest; burst allowance 120.
  - Idempotency: recommend honoring idempotency_key for 24 hours to prevent duplicate interests when retrying.
  - Retries: client should retry on 5xx with exponential backoff up to 3 times; on 429 follow Retry-After header.
  - Request: confirm rate limits and idempotency window, and indicate how the API signals duplicate submission (e.g., 409 with existing interest_id).

- Status updates: Polling vs webhook
  - Polling approach (frontend): GET /api/v1/express_interest/{interest_id}
    - Response example:
      {
        "interest_id": "<uuid>",
        "status": "queued|processing|delivered|failed",
        "updated_at": "2024-01-01T00:00:00Z",
        "detail": "optional human-readable reason for failed"
      }
  - Webhook approach (backend pushes to client-owned webhook):
    - Event: express_interest.status_changed
    - Payload: { interest_id, venture_id, status, updated_at }
    - Authentication: HMAC signature header recommended
  - Frontend ask: confirm which strategy backend will provide (polling endpoint, webhook, or both). If both, confirm recommended polling interval (suggest 5s for first 30s, then 30s intervals up to 2 minutes) and webhook payload format.

Acceptance criteria (what we need from Marcus/backend)
- Confirmed public venture schema (JSON) stating explicitly which fields are allowed/forbidden re: PII.
- Confirmed express_interest endpoint path, request body schema, response schema, and status enum values.
- Confirmed rate-limits and idempotency semantics (limits, retry behavior, response for duplicates).
- Confirmed status update strategy: polling endpoint and/or webhook; provide example responses and event payloads.
- Indicate any additional headers/authentication requirements and expected error codes with example bodies (at least for 400, 401, 403, 409, 429, 500).

Timeline & next steps
- Requesting confirmation within 48 hours to avoid blocking frontend implementation for the next sprint.
- If any of the proposed defaults are unacceptable, please provide the exact contract to use.

Contacts
- Frontend owner: Kevin — implementing list, modal, queued state, polling.
- Docs owner: Emma (this doc)

Files referenced
- output/specs/frontend_contact_flow_review.md (frontend proposal by Kevin)

