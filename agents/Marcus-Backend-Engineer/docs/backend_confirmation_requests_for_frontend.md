Purpose

This document confirms backend API shapes, authentication, file URL behavior, enums, and sample JSON responses so the frontend can implement without rework.

Summary

- Author: Marcus (Backend)
- Created: 2026-03-06
- Scope: Endpoints, field types, enums, auth method, file-download/upload URL policy, CORS, rate limits, sample responses, acceptance criteria.

Global conventions

- API base: /api/v1
- Content-Type: application/json for all JSON requests/responses
- Time format: ISO 8601 in UTC (e.g. "2026-03-06T15:04:05Z")
- IDs: UUID v4 strings (e.g. "f47ac10b-58cc-4372-a567-0e02b2c3d479") unless noted
- Pagination: cursor-based where appropriate; simple page&size available for lists (query: ?page=1&size=20)
- Error format (consistent):
  {
    "error": {
      "code": "string_code",
      "message": "human readable message",
      "details": { /* optional, structured */ }
    }
  }

Authentication

Decision: Bearer JWT in Authorization header.
Rationale: SPA + mobile clients will call backend directly; bearer tokens simplify CORS and CSRF considerations. We will use short-lived access tokens (15 minutes) + refresh tokens (7 days) with refresh rotation. Refresh tokens are sent via secure HttpOnly cookie if the frontend opts-in, but primary flow is Authorization: Bearer <access_token>.

Headers:
- Authorization: Bearer <access_token>
- Idempotency-Key: <uuid> (for mutating endpoints when recommended)
- X-Client-Version: optional client version string

Rate limiting

- Per-user: 100 req/min by default. Will return 429 with Retry-After header on exceed.

File download/upload URL policy

Download (recommended):
- Backend issues signed (presigned) GET URLs for object storage (S3-compatible) for private files.
- Default expiry: 5 minutes (300 seconds). Configurable per-use case; if the frontend needs longer-lived URLs, request justification.
- Signed URL delivered in JSON as "file_url": "https://storage.example.com/obj?X-Amz-..."
- CORS: storage bucket CORS must allow GET from frontend origin(s). Backend will not proxy large file downloads by default (to preserve scaling). If the file is small and requires ACL logic, backend can proxy — request explicitly.

Upload (two options):
1) Direct upload via signed PUT/POST URL from backend (recommended for large files). Backend returns upload_url and object_key. Expiry: 5 minutes.
2) Multipart upload handled by frontend with signed URLs per part if needed.

Additional notes:
- Signed URLs must be single-use if content is sensitive. For most cases, single-use=false with short TTL=5min is sufficient.
- If content should be accessible publicly after processing, backend returns a stable public URL field (public_url) after post-processing.

Endpoints (high-priority for frontend)

1) Get item list
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /api/v1/items | List items (paged) | Bearer |

Query parameters:
- page: integer, optional, default 1
- size: integer, optional, default 20, max 200
- q: string, optional search

Response 200:
{
  "items": [
    {
      "id": "uuid",
      "title": "string",
      "status": "active|archived",
      "thumbnail_url": "https://..." /* can be signed URL if private */
    }
  ],
  "meta": { "page": 1, "size": 20, "total": 123 }
}

Acceptance criteria:
- p95 response <100ms for list with default page size (backend SLA). Returns empty items array when none.
- 400 if invalid query params.

2) Get item by id
| Method | Path | Description | Auth |
| GET | /api/v1/items/{id} | Retrieve item | Bearer |

Response 200:
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "active|archived",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "file": {
    "object_key": "string",
    "file_url": "https://storage..." /* signed URL, expires */
  }
}

Errors:
- 404 if not found
- 401 if unauthorized

3) Create item (with optional file upload)
| Method | Path | Description | Auth |
| POST | /api/v1/items | Create item | Bearer |

Request JSON (option A: frontend uploads file directly using signed URL)
{
  "title": "string",
  "description": "string",
  "file_object_key": "string" /* returned by /uploads/sign or upload flow */
}

Request JSON (option B: small file inline as base64) — discouraged for large files.

Response 201:
{
  "id": "uuid",
  "title": "string",
  "status": "active",
  "file": { "object_key": "string", "file_url": "https://..." }
}

Acceptance criteria:
- Idempotent creation supported via Idempotency-Key header. Duplicate requests with same key should return the original resource (409 or 200 depending on semantics).
- Validation errors return 400 with field-level details.

4) Sign upload URL (helper)
| Method | Path | Description | Auth |
| POST | /api/v1/uploads/sign | Returns signed PUT/POST URL for direct upload | Bearer |

Request 200:
{
  "object_key": "items/{uuid}/original_filename.ext",
  "upload_url": "https://storage.example.com/obj?X-Amz-...",
  "expires_in": 300
}

Notes: Backend can also support S3 POST policy style when required.

Enums (canonical)
- status: ["active", "archived", "deleted"]
- role (if returned): ["user", "admin", "support"]

Sample error response
400 Bad Request
{
  "error": {
    "code": "validation_failed",
    "message": "Validation failed",
    "details": { "title": "required" }
  }
}

Mock endpoints / sample JSON

- GET /api/v1/items?page=1&size=2
200
{
  "items": [
    { "id": "11111111-1111-4111-8111-111111111111", "title": "First item", "status": "active", "thumbnail_url": "https://storage.example.com/thumbs/1111?X-Amz-..." },
    { "id": "22222222-2222-4222-8222-222222222222", "title": "Second item", "status": "active", "thumbnail_url": null }
  ],
  "meta": { "page": 1, "size": 2, "total": 42 }
}

- GET /api/v1/items/11111111-1111-4111-8111-111111111111
200
{
  "id": "11111111-1111-4111-8111-111111111111",
  "title": "First item",
  "description": "Detailed description",
  "status": "active",
  "created_at": "2026-03-06T12:00:00Z",
  "updated_at": "2026-03-06T12:05:00Z",
  "file": { "object_key": "items/1111/original.jpg", "file_url": "https://storage.example.com/items/1111/original.jpg?X-Amz-..." }
}

Acceptance criteria checklist for frontend sign-off

- [ ] Endpoints: All paths/methods listed above are available and match response shapes.
- [ ] Auth: Authorization: Bearer <token> works; 401 returned when missing/expired.
- [ ] Files: file_url in responses is a working signed URL that allows GET from the frontend origin and expires in ~300s.
- [ ] CORS: Storage CORS allows frontend origin for GET (and PUT for upload flow).
- [ ] Error format: frontend receives error JSON as specified.
- [ ] Performance: list endpoint p95 <100ms for default page size.

Open questions / trade-offs (callouts)

- If your UI requires cookies for silent auth refresh, we can issue refresh tokens via secure HttpOnly SameSite=Lax cookie; this requires extra infra and is less friendly for cross-origin mobile apps. Recommend Bearer + refresh-token via cookie optional.
- If frontend requires stable long-lived public URLs, backend needs to copy objects to a public bucket or set public ACLs after processing. This changes security model.

Contacts & next steps

- Backend owner: Marcus (#ai-backend)
- If this doc matches frontend needs: confirm in the ticket or reply here with any required changes.
- If you want mock endpoints (hosted) we can spin a minimal mock server (P1); confirm and I will provide mock URLs.

