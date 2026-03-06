Title: ML & Search Backend - Implications, Requirements, and Action Items

Purpose
- Summarize how ML and search features affect the backend feasibility decisions Marcus documented.
- List product-level decisions required (PII policy, search QPS, issue ownership).
- Provide concrete acceptance criteria and technical constraints Marcus should include when creating GH issues.

1) Product decisions needed (action by Alex / Product)
- PII retention & deletion policy
  - Required answers: which fields are PII (email, name, phone, SSN, investor identifiers, transaction details?), retention duration per data class (e.g., 90 days / 1 year / indefinite for legal records), whether soft-delete vs hard-delete on user request, and whether backups/archive copies must be purged.
  - Why it matters: affects encryption strategy, DB schema (audit fields), index retention and deletion pipelines, legal compliance tasks for deletion across backups and search indices.
- Expected search QPS (low / medium / high)
  - Provide numeric ranges if possible (example guidance: low < 10 qps, medium 10–200 qps, high > 200 qps).
  - Why it matters: influences sizing for OpenSearch clusters, vector store sharding, caching strategy, and inference capacity for on-demand embedding generation.
- Issue creation ownership
  - Confirm whether Marcus should create the GH issues directly (Marcus currently requested this) or whether product will triage/prioritize first.

2) Backend technical impacts & requirements (for Marcus)
- Data storage & retention
  - Embeddings store: store as vectors in OpenSearch (dense vectors) or a dedicated vector DB (Milvus, Pinecone). Estimate: 1M docs × 768-dim float32 ≈ 3.1 GB (vectors only) — include overhead for indexing & metadata (x2–3).
  - Primary DB: add embedding reference columns + PII classification flags + retention_timestamp and deleted_at.
- Encryption & PII handling
  - Requirement: encrypt PII at rest (DB-level TDE) and at field level for highly sensitive fields (use envelope encryption). PII in search indices should be masked or hashed unless product confirms retention for search.
  - Deletion workflow: implement delete cascade that removes from primary DB, search indices, and embedding store; include asynchronous background job to handle deletion across replicas/backups.
- Access control & auditing
  - Enforce RBAC for endpoints that return PII. Audit logs for PII access (who, when, what). JWT + RBAC already in spec — include read scopes for ML/analytics access separately.
- Embedding generation pipeline
  - When to generate embeddings: on write (synchronous) vs on demand (asynchronous background job). Tradeoffs: synchronous = fresher search but higher write latency; async = delayed availability but lower write latency.
  - Recommendation (reversible): start with async background embedding pipeline with a synchronous fallback for critical paths.
- Inference & latency SLOs
  - If real-time semantic search / RAG expected, aim for p95 inference latency < 50ms for embedding lookups (target per ML team). GPU-backed embedding generation for on-demand < 200ms.
  - For batch re-indexing, allow higher latency but track job durations and throughput.
- Observability & monitoring
  - Metrics to expose: search query latency (p50/p95/p99), QPS, embedding generation time, embedding queue length, failed jobs, model version, data drift signals (distributional changes), PII deletion success rate.
- Versioning & rollback
  - All models/embeddings must be versioned (MLflow). Provide model_version metadata with each embedding and search result to support rollback.

3) Acceptance criteria for backend GH issues (what to include per ticket)
- Clear scope: DB schema change, migration plan with downtime/rollback steps, and estimated dev-days.
- PII handling: list fields considered PII, encryption method, deletion flow, and test cases for deletion (unit + integration verifying removal from search & backups).
- Embedding pipeline: design doc (sync vs async), storage choice (OpenSearch vectors vs dedicated), and capacity estimates based on product QPS & retention.
- APIs: endpoints to create/update/delete documents, search endpoint contract (params, pagination, filters), auth scopes required.
- Observability: list concrete metrics to emit and dashboards/alerts to create.
- Testing: integration tests for search correctness, performance tests for QPS/latency, and compliance tests for deletion.

4) Data requirements (action by Samantha / #ai-data)
- Provide sample export: last 3 months of canonical documents to be indexed (CSV/JSONL) with schema + PII-labeled fields.
- Include expected ingestion rate (docs/day), average doc size, and number of unique IDs.
- Provide consent/PII labeling rules if available.

5) Infra coordination (action by Noah / #ai-devops)
- OpenSearch cluster sizing guidance once product provides QPS and retention.
- Storage tiering for embeddings/archive.
- Backup & deletion automation to satisfy hard-delete across backups.

6) Recommended first tasks (priority order)
- P0: Product confirms PII classes, retention & deletion policy and search QPS.
- P1: Marcus creates GH issues including ML-specific acceptance criteria listed above.
- P1: Samantha exports sample data for feature engineering and indexing (3 months).
- P2: Implement embedding background job skeleton and DB schema migration (3 dev-days estimate; adjust after QPS confirmed).

7) Trade-offs & decisions made (so what)
- Decision: recommend async embedding pipeline initially to minimize write latency and reduce infra strain. Reversible: can introduce sync path later if product needs immediate availability.
- Decision: store embeddings alongside OpenSearch vectors to reduce operational complexity given Marcus' feasibility doc recommends OpenSearch.

8) Next steps / Checklist
- [ ] Alex (Product): confirm PII retention/deletion policy and search QPS.
- [ ] Marcus (Backend): include the acceptance criteria above in GH issues and start DB schema & migrations after Alex confirms.
- [ ] Samantha (Data): export 3 months of sample data with PII labels.
- [ ] Noah (DevOps): prepare cluster sizing options once QPS provided.

Document author: Lisa (ML/AI Engineer)
Date: 2026-03-06

