# Investor Portal — Backend Design

## Core ask
Design backend data model and APIs for an Investor / Venture Capital Engagement Portal that lets founders create time-limited, permissioned links that provide read-only access to a KPI/materials dashboard.

## MECE breakdown
- Data model: Engagement links, permissions, dashboard snapshots, audit logs
- APIs: Create/revoke/list links (founder), consume link (viewer, token-based, read-only)
- Security: Token format, expiry, rate limiting, RBAC for founders
- Performance & scaling: caching, indices, p95/p99 targets
- Observability: tracing, audit logs for views and downloads

## Key decisions (reversible)
- Link token: 32-byte URL-safe random token (base64url), stored hashed (SHA256) in DB to allow revocation without leaking token.
- Token usability: token in URL path (/share/{token}) grants read-only access; token exchange endpoints avoided to keep consumer simple.
- Session model: no login for viewers; founder APIs use Bearer JWT (15m) + refresh rotation.
- Dashboard data: precomputed snapshot (JSON) for read-only view; optionally regenerate on-demand with rate-limited queries.
- Caching: Redis cache for snapshot payloads (TTL 5 minutes) to keep p95 < 100ms.

## Database schema (pseudocode)
Tables:
- engagement_links
  - id: UUID PK
  - creator_id: UUID FK users(id)
  - token_hash: char(64) -- SHA256(hex)
  - title: varchar(255)
  - expires_at: timestamptz
  - max_views: integer NULL
  - revoked_at: timestamptz NULL
  - created_at, updated_at
  - is_public_snapshot: boolean (if true, snapshot view allowed)
  - metadata: jsonb (optional)
  Indexes: idx_engagement_links_creator_id, idx_engagement_links_token_hash (unique)

- dashboard_snapshots
  - id: UUID PK
  - engagement_link_id: UUID FK
  - payload: jsonb (precomputed KPI + materials list)
  - generated_at: timestamptz
  - size_bytes: integer
  Indexes: idx_dashboard_snapshots_engagement_link_id

- engagement_view_audit
  - id: BIGSERIAL PK
  - engagement_link_id: UUID
  - viewer_ip: inet NULL
  - user_agent: text NULL
  - viewed_at: timestamptz
  - referer: text NULL
  Indexes: idx_engagement_viewed_at

Security note: Store token_hash only; compare by hashing presented token with SHA256.

## API contract (summary)
- Auth for founder APIs: Bearer JWT (RFC6750). Rate-limit: 60/min per user.
- Viewer access: token in path, rate-limit: 30/min per IP, idempotent read. CORS: allow embed via iframe if allowed by founder flag.
- Error format: {"error": {"code": "string", "message": "string", "details": {}}}

Acceptance criteria
- Create link endpoint creates hashed token and returns full token once (founder must store)
- Viewer endpoint returns snapshot JSON within p95 < 100ms with Redis cache hit
- Revoked and expired tokens return 401/403 with consistent error format
- Audit events recorded for each view

## Next steps for Backend (Marcus)
- Produce OpenAPI spec and SQLAlchemy models + FastAPI router skeleton for frontend to start integration.
- Coordinate with design for field names on dashboard JSON and UI expectations.

