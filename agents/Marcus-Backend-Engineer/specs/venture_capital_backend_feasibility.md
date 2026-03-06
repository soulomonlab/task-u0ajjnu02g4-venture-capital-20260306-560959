# Venture Capital — Backend Feasibility

Status: Draft
Author: Marcus (Backend)
Date: 2026-03-06

Situation
- Frontend provided API contract and acceptance criteria (output/specs/venture_capital_frontend_requirements.md). They need a backend feasibility assessment covering API details, DB schema sketch, infra components, scalability bottlenecks, privacy blockers, and effort estimates to decide implementation approach.

Complication
- The feature mixes public discovery with user-specific actions (bookmarks, express_interest) and a privacy-sensitive contact flow. This requires careful API, DB design, auth, and mediation to avoid exposing PII and to meet performance SLAs for listing/searching.

Resolution (deliverable)
- This document provides: API endpoints (params + response shapes), a database schema sketch, infra & observability components, identified bottlenecks & privacy blockers, and effort estimates (small/medium/large) per work item.

1) Summary of decisions (high level)
- Read APIs: public, cursor-paginated, cacheable; Detail API: cacheable with ETag/Last-Modified.
- Mutations (bookmark, express_interest): authenticated via JWT (OAuth2 bearer). Backend mediates any PII exchange; no raw emails/phones in API responses.
- Pagination: implement cursor-based pagination (reversible to offset if needed). Use composite indexes for filtered reads (sector, stage, tags).
- Search: phase 1 = indexed DB filters + trigram full-text search in Postgres; phase 2 = dedicated search engine (Elasticsearch/Opensearch) if QPS or complex ranking needed.
- Media: logos served via CDN (S3) with signed URLs for private assets.

2) API surface (detailed)
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | /api/v1/ventures | List ventures (cursor pagination, filtering) | optional (public read) |
| GET | /api/v1/ventures/{id} | Get venture detail; includes public_contact_allowed flag | optional |
| POST | /api/v1/ventures/{id}/express_interest | Submit interest; backend mediates contact | required (Bearer) |
| POST | /api/v1/ventures/{id}/bookmark | Bookmark for authenticated user | required (Bearer) |
| GET | /api/v1/ventures/stats | Aggregated metrics (admin) | required, admin role |

- GET /api/v1/ventures
  - Query params
    - q: string (optional) — free-text search across name, short_description
    - sectors: string[] (optional) — multi-value filter
    - stage: enum[] (optional)
    - location: string (optional) — country/state (exact match)
    - tags: string[] (optional)
    - sort: enum (relevance|newest|raised) default=relevance
    - page_size: int (1..100) default=20
    - cursor: opaque string (optional)
  - Response
    - { items: VentureListItem[], next_cursor?: string, total_approx?: int }
    - VentureListItem: { id, name, short_description, logo_url, sectors[], stage, headline_metrics[], created_at }
  - Notes
    - Prefer returning total_approx instead of exact total_count to avoid expensive COUNTs for large tables.
    - Add X-Cache-Hit header and standard pagination headers where useful.

- GET /api/v1/ventures/{id}
  - Response: VentureFull
    - { id, name, short_description, full_description (markdown), sectors, stage, location, headline_metrics, fundraising, founders (id,name,title,public_profile_url), logo_url, website_url, pitch_deck_url (signed if private), demo_url, tags, created_at, updated_at, public_contact_allowed: boolean }
  - Caching: emit ETag and Last-Modified; support If-None-Match/If-Modified-Since.
  - Privacy: founders DO NOT include email/phone. public_contact_allowed controls enabling contact flows.

- POST /api/v1/ventures/{id}/express_interest
  - Auth: Bearer JWT (user_id in token)
  - Body: { message?: string, preferred_contact_method?: enum(email|in_app) }
  - Response: 202 Accepted { request_id, status: queued }
  - Behaviour: enqueue background job to deliver (email/messaging). Backend returns only status and request_id; no recipient PII.
  - Rate limit: per-user 10/day (configurable)

- POST /api/v1/ventures/{id}/bookmark
  - Auth: Bearer JWT
  - Body: { } (user_id from token)
  - Response: 200 { bookmarked: true, bookmark_id }
  - Behaviour: idempotent — repeated calls are no-op.

- Security & error model
  - Standard error envelope: { code, message, details? }
  - Status codes: 400/401/403/404/429/500
  - Rate limiting via API gateway (per IP and per-user for mutation endpoints)

3) Database schema sketch (Postgres) — core tables
- ventures (primary entity)
  - id UUID PK
  - name TEXT
  - short_description TEXT(140)
  - full_description TEXT (markdown)
  - stage TEXT (enum)
  - location TEXT
  - logo_s3_key TEXT
  - website_url TEXT
  - pitch_deck_s3_key TEXT (nullable; private)
  - demo_url TEXT
  - created_at timestamptz
  - updated_at timestamptz
  - public_contact_allowed boolean default false
  - search_vector tsvector (generated column)
  - PRIMARY INDEX: id
  - INDEX: (stage), (location), GIN(search_vector), GIN (tags) via separate tags table or jsonb

- venture_sectors
  - venture_id FK -> ventures.id
  - sector TEXT
  - Composite INDEX (sector, venture_id)

- venture_tags (or tags jsonb)
  - venture_id FK
  - tag TEXT
  - INDEX on tag

- founders
  - id UUID PK
  - venture_id FK
  - name TEXT
  - title TEXT
  - public_profile_url TEXT
  - pii_redacted boolean default false

- bookmarks
  - id UUID PK
  - user_id UUID FK
  - venture_id FK
  - created_at
  - UNIQUE(user_id, venture_id)
  - INDEX on user_id for listing

- interest_requests
  - id UUID PK
  - user_id UUID FK
  - venture_id FK
  - message TEXT (nullable)
  - preferred_contact_method TEXT
  - status ENUM (queued, sent, failed)
  - created_at, processed_at
  - INDEX on user_id, venture_id

- audit_logs (GDPR, compliance)
  - id, actor_id, action, target_type, target_id, payload(jsonb), created_at

Storage choices & notes
- Use JSONB for flexible metadata and tags if startup data model expected to evolve rapidly.
- store search_vector as generated tsvector and keep updated via trigger or computed column.
- Use materialized views for heavy aggregates (ventures/stats) refreshed asynchronously.

4) Infra components
- API layer: FastAPI + Uvicorn/Gunicorn, deployed in dockerized containers behind API Gateway (e.g., AWS ALB/API Gateway).
- Auth: JWT with key rotation (JWKS) — tokens verified by API gateway or middleware.
- DB: PostgreSQL (primary) with read replicas for scaling reads. Use connection pooling (PgBouncer).
- Caching: Redis for application caching (list result caches, rate-limiting counters, session/lock), and Celery broker (or Redis streams) for background jobs.
- Background workers: Celery + workers to process express_interest (send emails, notifications).
- Search (phase 1): Postgres full-text search + pg_trgm. Phase 2: OpenSearch/Elasticsearch for advanced ranking, suggestions.
- Media: S3 (or object store) + CDN (CloudFront) for logos and pitch decks. Signed URLs for private assets.
- Observability: OpenTelemetry traces in all services, structured logs, metrics exported to Prometheus/Grafana. Alerts for error rate, latency.
- Rate limiting & API gateway: per-IP and per-user quotas; protect mutation endpoints.
- Secrets & config: Vault or parameter store for secrets (SMTP keys, S3 creds). Use KMS for encryption-at-rest keys.

5) Scalability bottlenecks & mitigations
- Full table scans on list/search: Mitigate with indexes, proper query patterns, use of cursor pagination, and caching for common queries.
- COUNT(*) for totals: expensive at large scale — return approximate totals or maintain counters in a separate table/cache.
- Hot partitions on tags/sectors: use composite indexes and possibly a precomputed listing table for high-traffic filters.
- Background job spikes (express_interest): implement async rate-limiting, dedup, and retry policy; scale workers horizontally.
- Media bandwidth: offload to CDN, use optimized image sizes and responsive images.
- DB connection limits: use PgBouncer and limit per-app connections; use read replicas for heavy read traffic.

6) Privacy & legal blockers (must resolve before launch)
- PII exposure: do NOT return email/phone in any public or list responses. Contact flows must be mediated: backend sends inbound-notification or masked contact.
- Consent & removal: must provide endpoints or processes for GDPR/CCPA data deletion or redaction. Track consent flags per founder/venture as required.
- Data retention: define retention policy for interest_requests and logs; legally-required audit retention may conflict with deletion — design soft-delete and redaction.
- Third-party sharing: if sending emails to third-party investors, ensure legal agreements; log consent.
- Access control: admin endpoints must be RBAC-protected and audited.

7) Observability, SLOs & performance targets
- Endpoints SLOs: List p95 < 300ms (cached), cold < 1s; Detail p95 < 200ms (cached); Mutations p95 < 500ms (enqueue).
- Tracing: instrument all endpoints with OpenTelemetry; add spans for DB queries, cache hits/misses, background enqueue.
- Metrics to collect: request latency percentiles, error rate, cache hit ratio, queue length, background job failure rate.

8) Data privacy & security implementation notes
- Use column-level encryption for sensitive fields in DB if storing any PII (avoid storing email/phone where not needed).
- Apply parameterized queries via ORM (SQLAlchemy) to avoid SQL injection.
- CSRF: for browser-based forms use same-site cookies if session auth used; for JWT, ensure CORS and secure headers.
- JWT lifetime: access token 15min, refresh 7 days (team standard). Use rotating refresh tokens for sessions.

9) Effort estimates (per piece) — rough engineering sizing
- Core DB schema + migrations (ventures, founders, tags, bookmarks, interest_requests): Medium (3-5 dev days)
- List & detail APIs (FastAPI) + pagination + basic filtering + caching headers: Medium (3 dev days)
- Bookmark endpoint (idempotent) + DB constraints: Small (1 dev day)
- Express_interest endpoint + background worker + basic email send (SMTP integration) + retries: Medium (3-4 dev days)
- Search: Postgres FTS + trigram tuning: Small→Medium (2-4 dev days)
- Phase-2 search with OpenSearch + ranking tuning: Large (2-3 sprints)
- Media handling (S3, CDN, signed URLs for private): Small (2 dev days)
- Auth & RBAC wiring + middleware + role checks: Medium (3 dev days)
- Rate-limiting & API gateway config: Small→Medium (2-3 dev days)
- GDPR endpoints (data deletion/redaction, audit): Medium (3-5 dev days) — includes legal review
- Observability (OpenTelemetry traces, Prometheus metrics, Grafana): Small→Medium (2-3 dev days)
- Tests (unit + integration + DB migrations): Medium (3-5 dev days) — must reach >80% coverage on critical paths
- Load testing & perf tuning: Small→Medium (2-4 dev days)

Estimate summary (MVP scope = List, Detail, Bookmark, Express Interest mediated via email, basic search, media CDN): ~3-4 engineer-weeks (one engineer) to reach a production-grade MVP including tests and infra scripts.

10) Risks & open questions (requires product/legal)
- Public vs private read: frontend prefers public read; legal might restrict. Confirm whether ventures are public by default.
- Contact flow policy: should express_interest always send email to founders, or route to an internal curation queue? Clarify privacy policy and required consent.
- Founder PII storage: will we ever store emails/phones? If yes, we need stronger encryption, access controls, and legal sign-offs.
- Analytics requirements: what aggregated metrics are required for /ventures/stats? Synchronous or offline?

11) Next steps & recommendations
- Confirm privacy policy: public read allowed? how to handle contact mediation? (Product/Legal)
- Proceed with DB schema migration PR and feature branch: implement core tables + simple list/detail APIs first.
- Implement OpenTelemetry traces from day one and add load-testing before public release.

