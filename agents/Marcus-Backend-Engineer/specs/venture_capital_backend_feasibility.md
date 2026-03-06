# Backend Feasibility — Venture Capital Product (finalized)

Status: Finalized by Marcus (Backend)

Overview
--------
This document finalizes technical decisions for the backend implementation of the Venture Capital product and provides a per-issue breakdown with refined effort estimates for Alex to use when creating GitHub issues (or link directly to the created issues listed below).

Key decisions (confirmed)
-------------------------
- Multi-tenancy model: Tenant-per-row with Postgres Row-Level Security (RLS).
  - Why: Strong security isolation for customers, simpler cost model vs fully separate DBs, supports tenant-scoped analytics and permissioning.
  - Implementation: Add tenant_id FK on primary tables + enable RLS policies at table level. Enforce tenant_id from JWT claims at application level.

- Search engine: External search (OpenSearch) for primary read/search surfaces; Postgres FTS only for small internal admin queries.
  - Why: Need relevance tuning, facets, aggregations, typo-tolerance, scalable indexing and query throughput. OpenSearch provides horizontal scaling and mature relevance features.
  - Sync strategy: Event-driven sync from DB -> Kafka (or Redis stream) -> indexing worker -> OpenSearch. Optionally initial bulk backfill via ETL.

- PII scope & handling
  - Fields classified as PII: person names (founders, LP contacts), emails, phone numbers, home addresses, SSN/national ID (if present), personal notes.
  - Handling: Encrypt PII at rest using application-level encryption for high-sensitivity fields; at minimum use PostgreSQL column-level encryption or pgcrypto. Access to decrypted PII gated by RBAC and audited.
  - Masking: API responses mask PII unless user has explicit permission.

- Authentication & RBAC
  - JWT-based auth: access tokens 15m, refresh 7d with rotation.
  - RBAC model: roles (admin, org_admin, analyst, read_only) + resource-level permissions. Use middleware to enforce scope.
  - Rate-limiting & idempotency keys for mutation endpoints to prevent duplicate ingestion.

- Observability
  - Distributed tracing (OpenTelemetry) enabled on all HTTP handlers and background workers.
  - Metrics exported to Prometheus. Alerts for error rate (>0.1%), p95 latency >100ms, DB slow queries.

- Performance & SLOs
  - API p95 < 100ms, p99 < 200ms for read endpoints under expected load.
  - DB query targets: <20ms for indexed lookups; add indexes when queries >50ms.
  - Caching via Redis for hot endpoints (TTL 5m default).

Architecture sketch
-------------------
- Components
  - FastAPI backend (APIs, auth, business logic)
  - PostgreSQL primary database with logical partitioning by tenant for large tenants
  - OpenSearch cluster for search
  - Redis (cache + rate limiter)
  - Celery workers (or equivalent) for background jobs and indexing
  - Kafka or Redis Streams for reliable event bus (optional at MVP; use Redis Streams if we need faster time-to-market)

Scalability bottlenecks & mitigations
------------------------------------
- Search throughput: offload to OpenSearch with autoscaling.
- Large tenant data volumes: support table partitioning and tenant-specific maintenance windows.
- Write amplification during bulk imports: use bulk index APIs and throttled background workers.

Privacy blockers & compliance
-----------------------------
- Need legal confirmation on retention policies for personal contact data and export/delete workflows (Right to be Forgotten).
- PII encryption must comply with company policy; if we expect SSN-like data we should treat that as a compliance P0.

Acceptance criteria (high-level)
--------------------------------
- Tenant isolation: Cannot access another tenant's rows via API.
- Search: Relevant company/fund/deal search with facets completes within p95 < 200ms for common queries.
- PII: Sensitive fields encrypted at rest and masked in API responses unless authorized.
- Observability: All endpoints traced; dashboards for error-rate and latency exist.

Refined per-issue breakdown (total: 26 dev-days)
-----------------------------------------------
1) DB schema design & Alembic migrations — 3 dev-days
   - Normalize entities: tenants, users, org_membership, companies, funds, deals, notes, tags.
   - Add tenant_id, indexes for common queries, foreign keys, and constraints.
   - Deliverable: SQLAlchemy models + Alembic migration.

2) Auth, RBAC & RLS enforcement — 4 dev-days
   - Middleware to extract tenant_id from JWT and set session variable.
   - Implement row-level security policies and role permission mapping.
   - Deliverable: middleware, sample RLS policies, integration tests.

3) Companies API (CRUD + listing + import endpoint) — 2 dev-days
   - Pagination, filtering, sorting, and minimal fields for listing.
   - Deliverable: FastAPI router + unit tests.

4) Funds & Deals API + relationships — 3 dev-days
   - CRUD and relational endpoints, referential integrity.
   - Deliverable: routers + tests.

5) Search: OpenSearch integration + indexing pipeline — 4 dev-days
   - Index schema, indexing worker, initial bulk backfill, search endpoints with facets and relevance config.
   - Deliverable: OpenSearch index mapping + indexing worker + search API.

6) Data ingestion & ETL (bulk import, dedupe) — 2 dev-days
   - CSV/JSON import handling, deduplication heuristics, idempotency.
   - Deliverable: ingestion worker + API endpoint.

7) PII classification, encryption & masking — 2 dev-days
   - Field-level encryption and masking logic, access gating and audit logging.
   - Deliverable: encryption util + policy enforcement + tests.

8) Redis caching & rate limiting — 1 dev-day
   - Implement per-tenant cache and token bucket rate limiter.
   - Deliverable: middleware + config.

9) Background workers (Celery) setup & job templates — 1 dev-day
   - Worker infra patterns for long-running tasks and retries.
   - Deliverable: task templates and deployment doc.

10) Observability & OpenTelemetry traces — 1 dev-day
   - Tracing on HTTP and worker spans, Prometheus metrics.
   - Deliverable: instrumentation + dashboards.

11) Performance & load testing (benchmarks) — 1 dev-day
   - Scripts and baseline results to validate SLOs.
   - Deliverable: load test scripts + report.

12) Tests & QA coverage (unit + integration) — 2 dev-days
   - Target >80% coverage for new code paths.
   - Deliverable: test suites and CI config for tests.

Dependencies & order
--------------------
- Start with DB schema and RLS (1 -> 2). Search integration requires schema (5 depends on 1).
- Observability and Celery can be done in parallel with APIs.

Open questions for Product / Security (to resolve before dev)
------------------------------------------------------------
- Confirm retention and deletion policy for PII.
- Confirm target query types and expected QPS for search (affects OpenSearch sizing).
- Confirm whether we must support data export formats and audit logs for compliance.

Appendix: Quick API surface (examples)
--------------------------------------
| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST   | /api/v1/companies | Create company | Bearer |
| GET    | /api/v1/companies | List companies (pagination & filters) | Bearer |
| GET    | /api/v1/companies/:id | Get company | Bearer |
| POST   | /api/v1/search | Search companies/funds/deals | Bearer |


Files created by Marcus
-----------------------
- This file: output/specs/venture_capital_backend_feasibility.md


Next steps
----------
- I created a per-issue breakdown and refined estimates (26 dev-days). I will now create GitHub issues for each backend task and hand off to Alex for prioritization and assignment.
