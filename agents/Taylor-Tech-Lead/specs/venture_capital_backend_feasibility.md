# Backend Feasibility: Venture Capital Feature

## Purpose
Provide engineering feasibility, API surface, DB schema sketch, infra components, scalability/bottleneck analysis, privacy blockers, assumptions, and high-level effort estimates so Product/Design can proceed.

## Scope
- MVP: Capture firms, deals, limited investor profiles, and basic search/filtering. No marketplace or investment execution.
- Excludes: Payments, KYC onboarding, complex investor analytics (phase 2).

## High-level architecture
- Backend: FastAPI (Python)
- Primary DB: Postgres (managed - e.g., Railway / AWS RDS)
- Cache: Redis (for rate-limiting, sessions, short-lived caches)
- Background jobs: Celery + Redis/RabbitMQ or preferrably (for simplicity) RQ/Redis
- Search: Postgres Full-Text Search for MVP; ElasticSearch/MeiliSearch if search requirements grow
- Object storage: S3-compatible for attachments
- Auth: JWT + RBAC for internal roles (admin, analyst) and tenant scoping if multi-tenant
- Monitoring/Logging: Prometheus + Grafana, structured logs (Datadog/Logs)

## API surface (MVP)
Authentication: Bearer JWT tokens; endpoints require scope-based permissions.

1) Firms
- GET /api/v1/firms
  - Query params: q, stage, sector, location, page, per_page
  - Response: paginated list of firm objects
- GET /api/v1/firms/{firm_id}
- POST /api/v1/firms
  - Body: {name, description, website, headquarters, sectors:[], founded_year, tags:[]}
- PATCH /api/v1/firms/{firm_id}
- DELETE /api/v1/firms/{firm_id}

2) Deals
- GET /api/v1/deals
  - Query params: q, firm_id, round, min_amount, max_amount, date_from, date_to, page
- GET /api/v1/deals/{deal_id}
- POST /api/v1/deals
  - Body: {title, firm_id, round, amount, currency, announced_date, description, stage, sectors:[], tags:[]}
- PATCH /api/v1/deals/{deal_id}
- DELETE /api/v1/deals/{deal_id}

3) Investors (limited profile)
- GET /api/v1/investors
- GET /api/v1/investors/{investor_id}
- POST /api/v1/investors

4) Notes / Activity (audit-logged)
- POST /api/v1/deals/{deal_id}/notes
- GET /api/v1/deals/{deal_id}/activity

5) Admin / Bulk
- POST /api/v1/import (CSV/JSON) — background job; returns job id
- GET /api/v1/import/{job_id}/status

Auth & Authorization
- JWT access tokens with scopes: read:firm, write:firm, read:deal, write:deal, admin
- Role-based checks in endpoints
- Row-level tenant scoping if multi-tenant

## DB schema sketch (Postgres)
Notes: types & indexes are suggested; finalize with Marcus.

Tables:
- users
  - id UUID PK
  - email text UNIQUE
  - hashed_password text
  - name text
  - role text
  - created_at timestamp
  - last_login timestamp
  - indexes: email

- firms
  - id UUID PK
  - name text
  - slug text UNIQUE
  - description text
  - website text
  - headquarters text
  - founded_year int
  - sectors text[] (or separate firm_sectors table for normalized queries)
  - tags text[]
  - created_at timestamp
  - updated_at timestamp
  - indexes: GIN on (name, description) for full-text; index on slug

- deals
  - id UUID PK
  - firm_id UUID FK -> firms(id) ON DELETE CASCADE
  - title text
  - round text
  - amount numeric(20,2)
  - currency char(3)
  - announced_date date
  - stage text
  - sectors text[]
  - description text
  - created_by UUID FK -> users(id)
  - created_at timestamp
  - updated_at timestamp
  - indexes: GIN on (title, description); index on firm_id, announced_date

- investors
  - id UUID PK
  - name text
  - profile JSONB
  - tags text[]
  - created_at timestamp

- notes/activity
  - id UUID PK
  - entity_type text ("deal","firm")
  - entity_id UUID
  - user_id UUID FK users
  - body text
  - created_at timestamp
  - audit metadata (ip, user_agent)

- import_jobs
  - id UUID PK
  - user_id UUID
  - type text
  - status text (queued, running, success, failed)
  - payload JSONB
  - result JSONB
  - created_at, updated_at

Search considerations
- For MVP, Postgres full-text with GIN indexes (tsvector) on descriptive fields.
- If queries demand fuzzy search, autocomplete, ranking — add MeiliSearch/ElasticSearch (phase 2).

Data retention & privacy schema notes
- PII fields (user email, notes) tagged in schema
- Keep audit logs for changes; separate retention policy for exported sensitive data

## Infra components & deployment
- Service: FastAPI app behind gunicorn/uvicorn
- DB: Managed Postgres (multi-AZ for production)
- Cache/queue: Redis (single managed instance for MVP; scale to cluster)
- Background workers: containerized Celery/RQ workers
- Object storage: S3 for attachments
- CI: GitHub Actions (unit tests + migration checks)
- Staging & Prod environments; infra as code (Terraform) recommended for production

## Scalability bottlenecks & mitigations
1) Heavy search queries across text fields
   - Mitigation: Use GIN tsvector indexes, cached search results, and/or external search engine
2) Large import jobs and background processing
   - Mitigation: Use background jobs with rate limiting, chunked processing, monitor queue length
3) High read traffic for listing endpoints
   - Mitigation: CDN for static assets, Redis caching for popular queries, paginated endpoints
4) Database write hotspots during bulk imports/edits
   - Mitigation: Rate-limit imports, batch writes, use read replicas for reporting
5) Third-party API rate limits (data enrichment)
   - Mitigation: Backoff, persistent queue, cache enrichment results

## Privacy, compliance & blockers
- PII classification: emails, notes, contact info; must be encrypted at rest and masked in logs
- Data access controls: role-based, RLS (Row Level Security) if multi-tenant
- Audit logging: Immutable audit trail for any sensitive updates
- Legal/regulatory: If targeting EU users → GDPR compliance: data subject requests, data portability, deletion flows
- Data exports: require explicit privilege; warn users on export of PII
- Background enrichment: verify 3rd-party contracts for storing PII

## Non-functional requirements / SLOs (proposals)
- API 95th latency < 200ms for single-item GETs under normal load
- Background import jobs processed within SLA (e.g., 1 hour for 1000 rows)
- RPO/RTO for DB: RPO < 1 hour, RTO < 1 hour for production (set with managed DB)

## Acceptance criteria (MVP)
- CRUD for firms & deals + search with paging implemented and documented
- Import endpoint accepts CSV/JSON and runs in background with status endpoint
- Auth + RBAC enforced for write operations
- Basic monitoring + alerts for queue length and error rate

## Effort estimates (high-level)
Assumptions:
- 2 senior backend engineers available
- FastAPI + Postgres experience
- No major unknown external integrations

Estimates in developer-days (D):
1) Data model + migrations, DB provisioning: 3D (design + Alembic migrations + review)
2) Core CRUD APIs (firms, deals, investors basic): 6D (2 endpoints per entity + tests)
3) Search (Postgres FTS integration + pagination): 3D
4) Import pipeline + background jobs + job status API: 4D
5) Auth & RBAC (JWT, roles, tests): 2D
6) Infra: Redis + workers + S3 integration + deploy pipelines: 3D
7) Monitoring, logging, QA + docs: 3D
8) Buffer/QA fixes & iteration: 2D

Total: ~26 developer-days (~5-6 calendar weeks with 2 engineers and meetings). Range: 18-35D depending on scope changes (search complexity, external enrichments, multi-tenancy).

Recommendation: Split into 3 sprints:
- Sprint 1 (2 weeks): Data model, core CRUD, auth, basic infra (DB + CI)
- Sprint 2 (2 weeks): Search, import background jobs, S3 attachments
- Sprint 3 (1-2 weeks): Monitoring, QA fixes, polish, and docs

## Risks & open questions (for Marcus to validate)
- Will we need investor financials or sensitive PII beyond names & contact info?
- Expected search behaviors: fuzzy matching? ranking and relevance tuning?
- Volume expectations: daily writes, reads, expected dataset size (10k vs 1M records)
- Export requirements and retention policy specifics

## Next steps for engineering
1. Review and finalize DB schema (normalize arrays vs join tables) — Marcus
2. Confirm search SLA and decide external search engine vs Postgres FTS — Marcus
3. Identify any required 3rd-party enrichments (vendor contracts) — Marcus
4. Produce final effort breakdown per PR/issue and create GH issues for epics/tasks so Product can prioritize


---
Document prepared by: Taylor (CTO) — initial draft for Marcus to finalize.
