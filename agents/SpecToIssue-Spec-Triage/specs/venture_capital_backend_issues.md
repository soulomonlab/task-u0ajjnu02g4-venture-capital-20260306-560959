Spec-to-Issue: Venture Capital Product — Backend Implementation Plan

Summary
- Purpose: Turn the draft backend feasibility doc (output/specs/venture_capital_backend_feasibility.md) into a prioritized set of small, shippable GitHub issues for engineering.
- Output: 14 GH issues created (backend, frontend, QA) covering schema, APIs, search, ingestion, infra, security, CI, and tests.
- Next step: Marcus to review, confirm RLS/multi-tenant choice, confirm search choice (Postgres FTS vs external), and refine any estimates.

Issue list (titles, owners, short descriptions)
1) Design normalized Postgres schema for core entities — Owner: Marcus — backend, P0
   - Acceptance criteria: ER diagram + SQL CREATE TABLE statements (users, tenants, funds, startups, investors, deals, events, attachments). Normalized to 3NF where practical. RLS policies drafted for tenant isolation. Estimated: 3 dev-days.

2) Implement DB migrations & seed data — Owner: Marcus — backend, P1
   - Acceptance criteria: Flyway/Knex/Migrate scripts that create schema; seed scripts with representative test data. Local dev and CI migration tested. Estimated: 2 dev-days.

3) Implement Auth + Multi-tenant model (RLS) — Owner: Marcus — backend, P0
   - Acceptance criteria: JWT-based auth or OAuth flow documented; tenant model implemented; Postgres RLS policies enforce tenant isolation; integration tests verifying cross-tenant access is blocked. Estimated: 3 dev-days.

4) CRUD API for core entities (v1) — Owner: Marcus — backend, P1
   - Acceptance criteria: REST endpoints for funds, startups, investors, deals: list, get, create, update, delete. Pagination, filter by tenant, input validation, API docs (OpenAPI) included. Estimated: 4 dev-days.

5) Search evaluation: Postgres FTS vs external search — Owner: Marcus — backend, P1
   - Acceptance criteria: Short report comparing Postgres FTS, Elasticsearch/OpenSearch, Algolia, Meili: cost, latency, relevancy, infra ops, security/PII implications. Recommendation and prototype (one sample query) included. Estimated: 2 dev-days.

6) Implement chosen search integration — Owner: Marcus — backend, P1
   - Acceptance criteria: Search index pipeline (sync from Postgres), search API endpoints, basic ranking, and integration tests. If external service chosen, IaC for service provisioning included. Estimated: 3 dev-days.

7) Data ingestion pipeline (ETL) — Owner: Marcus — backend, P1
   - Acceptance criteria: Ingestion worker or Lambda that accepts CSV/JSON imports, validates, normalizes, deduplicates, writes canonical records to Postgres. Idempotency and retry behavior documented. Estimated: 3 dev-days.

8) Background jobs & worker infra — Owner: Marcus — backend, P2
   - Acceptance criteria: Queue (Redis/RabbitMQ) + worker (e.g., Celery/Sidekiq) implemented for ingestion, search sync, and long-running tasks. Retry rules and dead-letter handling defined. Estimated: 2 dev-days.

9) PII classification & masking policy + implementation plan — Owner: Marcus — backend, P0
   - Acceptance criteria: Catalog of PII fields, masking rules at rest/in transit, DB encryption scope, access logging, deletion/retention policy. Prototype masking on one endpoint. Estimated: 2 dev-days.

10) Caching & rate-limiting design + basic implementation — Owner: Marcus — backend, P2
   - Acceptance criteria: Redis cache for hot endpoints, TTL rules, cache invalidation approach; rate-limiting middleware to protect search and ingest endpoints. Smoke tests included. Estimated: 1.5 dev-days.

11) Infra provisioning checklist & IaC for core services — Owner: Marcus — backend (coordinate with DevOps) — P1
   - Acceptance criteria: Terraform/CloudFormation modules for RDS, Redis, S3, search service, and worker autoscaling. Runbook to deploy staging. Estimated: 3 dev-days.

12) CI/CD: migrations, schema checks, and integration tests — Owner: Marcus — backend, P2
   - Acceptance criteria: CI pipeline stages for lint, unit tests, migrations (preview/dry-run), and integration tests against a transient DB. Estimated: 1.5 dev-days.

13) Frontend: Search UI & integration — Owner: Kevin — frontend, P1
   - Acceptance criteria: React components for search box, results list, filters; integration with search API; client-side debounce and loading states. Acceptance test with sample queries. Estimated: 3 dev-days.

14) QA: Backend acceptance test plan & SLO verification — Owner: Dana — QA, P1
   - Acceptance criteria: Test cases covering auth, tenant isolation, CRUD APIs, ingestion, search, PII masking, and SLO checks. Automation smoke tests created. Estimated: 2 dev-days.

Notes & decisions to confirm
- Tenant model: RLS vs application-level tenant enforcement — requires Marcus decision before implementing schema and APIs.
- Search choice: start with Postgres FTS as fallback, but external search recommended if advanced relevance and scaling required.
- PII: scope needs to match legal / product PRD — confirm list in feasibility doc.

File references
- Draft feasibility doc: output/specs/venture_capital_backend_feasibility.md (review this first)
- This plan: output/specs/venture_capital_backend_issues.md

Next steps
- I will create the 14 GH issues now and then hand off to Marcus to review and finalize.
