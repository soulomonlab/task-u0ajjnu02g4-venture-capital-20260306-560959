# Venture Capital Backend API for Frontend

Summary (conclusion)
- Deliverables: OpenAPI spec + human-readable API contract with exact fields/enums, auth flow, file access policy, sample responses and dev tokens.
- Files created: output/specs/venture_capital_backend_api_for_frontend.md and output/specs/openapi_venture_capital.yaml

Context / Complication
- Frontend needs exact field names/types, auth behavior, and file download semantics to begin component and integration work. File/URL policy is highest risk for UX/security.

Resolution (details you can use immediately)
1) Authentication
- Method: Bearer access tokens (Authorization: Bearer <token>) for SPA. Refresh tokens supported via a secure httpOnly SameSite=Lax cookie and a refresh endpoint.
- Token lifetimes (decision: reversible, short-lived access tokens):
  - Access token TTL: 15 minutes
  - Refresh token TTL: 7 days (rotating refresh tokens; server issues new refresh token on use and invalidates previous)
- Scopes/permissions (string scopes included in token or returned by /me):
  - view_engagements
  - view_materials
  - download_files
  - upload_files
  - manage_engagements (admin)
- CSRF: Since refresh token is in cookie, require anti-CSRF token on refresh endpoint (x-csrf-token header). SPA should use Authorization header for API calls (no cookies). If later switching to cookie auth, require SameSite=Strict or Lax and server-side CSRF token verification.
- Auth endpoints (examples):
  - POST /api/auth/login -> returns { access_token, token_type=bearer, expires_in }
  - POST /api/auth/refresh -> uses refresh cookie + x-csrf-token -> returns new access_token
  - GET /api/auth/me -> user profile + scopes

2) Endpoints (confirmed paths, methods)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /api/engagements | List engagements (cursor-based paging) | Bearer |
| GET | /api/engagements/{engagement_id} | Get single engagement detail | Bearer |
| GET | /api/engagements/{engagement_id}/materials | List materials for engagement | Bearer |
| POST | /api/files/presign | Request an upload presign (S3 v4) | Bearer, scope: upload_files |
| GET | /api/files/{file_id}/download | Return presigned GET URL for download (or metadata if proxied) | Bearer, scope: download_files |
| GET | /api/files/{file_id}/stream | Proxy-download endpoint (optional flow) supporting Range | Bearer, scope: download_files |
| GET | /api/auth/me | Get current user and scopes | Bearer |
| POST | /api/auth/refresh | Rotate refresh token (cookie + csrf) | Cookie + x-csrf-token |

3) Request / Response schemas (fields, types, enums)
- Datetime format: RFC3339 / ISO8601 (UTC, e.g. 2026-02-10T12:34:56Z)

Engagement (engagement object)
{
  "id": "eng_123",            // string, required
  "name": "Series A - ACME", // string, required
  "description": "...",      // string, optional
  "owner": {                  // object
    "id": "u_1",            // string
    "name": "Jane VC"       // string
  },
  "created_at": "2026-02-10T12:34:56Z", // string, required
  "status": "active"        // enum: active | archived | draft
}

Material (file metadata)
{
  "id": "file_01",           // string
  "name": "Q1_report.pdf",   // string
  "mime": "application/pdf", // string
  "size": 12345,              // integer (bytes)
  "uploaded_at": "2026-02-10T12:34:56Z",
  "sensitivity": "standard", // enum: standard | sensitive
  "download_url": "https://...", // optional: returned for presign flow
  "expires_in": 600           // seconds (if download_url present)
}

List engagements response (cursor-based pagination)
{
  "data": [ <Engagement> ],
  "meta": { "cursor": "abc", "has_more": true }
}

Engagement detail response
{
  "id":"eng_123",
  "name":"Series A - ACME",
  "description":"KPI dashboard for ACME",
  "permissions": { "can_view": true, "can_download": false },
  "materials":[ { "id":"file_01","name":"Q1_report.pdf","size":12345,"mime":"application/pdf","download_url":"https://...","sensitivity":"standard" } ]
}

Presign upload request/response
POST /api/files/presign
Request: { "filename": "data.csv", "content_type": "text/csv", "size": 12345 }
Response: { "upload_url": "https://s3...", "fields": { ... }, "file_id": "file_123", "expires_in": 300 }

Download URL response
GET /api/files/{file_id}/download
Response: { "download_url": "https://s3-presigned-url", "expires_in": 600 }

4) Error response format
- Standard envelope
HTTP/1.1 401 Unauthorized
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid or expired token",
    "details": null
  }
}

Common error codes (code strings): unauthorized, forbidden, not_found, invalid_request, rate_limited, internal_error

Auth-failure / permission denied
- 401 + error.code = "unauthorized" when missing/invalid token
- 403 + error.code = "forbidden" when token valid but lacks scope

5) Paging / sorting / filtering rules
- Paging: cursor-based. Query params: ?cursor=<opaque>&limit=25 (limit default 25, max 100)
- Sorting: ?sort=created_at.desc or created_at.asc
- Filters: combine as query params, e.g. ?status=active&owner_id=u_1
- Response meta: { cursor: "next-cursor", has_more: true }

6) CORS
- Allow origins for dev/staging:
  - http://localhost:3000
  - http://localhost:5173
  - https://staging.vcapp.example.com
- Allow headers: Authorization, Content-Type, X-CSRF-Token, X-Requested-With
- Expose headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Traceparent

7) Headers (request / response)
- Request: Authorization: Bearer <token>, X-CSRF-Token (for refresh), Idempotency-Key (for safe retries on mutating ops)
- Response: X-Request-ID, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Traceparent

8) File (asset) access policy — recommended default
- Default flow: server issues presigned GET URLs for downloads after permission check.
  - Signed GET URL (S3 v4). TTL: 10 minutes (recommended range 300–900s)
  - The server MUST perform a permission check before creating presigned URL. Tokens/scopes required: download_files
  - Reuse: presigned URLs are single-signature but can be reused until expiry (no per-use single-use enforced by default). For higher security, generate single-use tokens mapped server-side to S3 object and track usage (optional).
  - CORS: storage must allow browser Origin or we proxy. Recommend adding Referer constraints if storage supports it.

- Sensitive-file flow: for materials flagged sensitivity = sensitive
  - Backend proxy: use /api/files/{file_id}/stream which streams content from storage after auth check (supports Range and HEAD). This avoids exposing storage URLs.
  - Range requests: supported for stream endpoint (Content-Range handling). Useful for large video files.

- Content headers
  - Respect original MIME type in Content-Type
  - For downloads set Content-Disposition: attachment; filename="<name>"
  - Cache-Control: private, max-age=300 for presigned URL responses; actual storage can have longer TTL but presigned link governs access.

- Uploads
  - Provide POST presign for browser direct-to-S3 (S3 POST policy) or PUT presign. Response returns upload_url + fields for POST.
  - After upload, client calls POST /api/files/verify or server processes S3 event to register metadata. We recommend a verification endpoint: POST /api/files/{file_id}/confirm (or server-side S3 event + webhook) which performs virus scan and finalizes metadata.

9) Mocking / sample responses
- OpenAPI spec provided (YAML): output/specs/openapi_venture_capital.yaml
- Dev test credentials (for local/dev only):
  - Test access token (expires 15m):
    - Token: "eyJhbGciOiJI...dev_access_token"
    - Scopes: ["view_engagements","view_materials","download_files","upload_files"]
  - Refresh token: cookie named "refresh_token" value "dev_refresh_token" (httpOnly; for local mocks this is simulated)
- Mock endpoints: simple static JSON under /mock/api/... should mirror examples above. Frontend can use openapi -> mock server tools (e.g., Prism / Swagger-UI) from the YAML.
- CORS for mock: allow http://localhost:3000

10) Security & operational recommendations (short)
- Prefer bearer + PKCE or bearer + refresh cookie rotation. Keep access token short.
- Presign only after permission check. Use backend proxy for highly sensitive files.
- Add rate-limiting per-user; return X-RateLimit-* headers.
- Instrument all endpoints with OpenTelemetry. Trace upload/download flows.

11) Risks & priorities
- Highest: finalize file access pattern (presign vs proxy). If you accept presign + sensitive-media proxy hybrid we can proceed with frontend.

Acceptance
- Primary deliverable: OpenAPI YAML + dev tokens are created in repo. Use output/specs/openapi_venture_capital.yaml to generate mocks.

