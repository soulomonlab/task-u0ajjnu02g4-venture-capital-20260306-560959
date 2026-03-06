Venture Capital Feature — ML & Data Privacy Considerations

Owner: Lisa (ML/AI Engineer)
Purpose: Provide actionable ML/data guidance for handling PII, search/embedding pipelines, and contact-mediation flows for the Venture Capital discovery + express_interest feature.

1) Situation
- Feature mixes public discovery (search/browse) with privacy-sensitive contact flows (express_interest → contact founders).
- Backend doc (Marcus) defines API shapes and privacy assumptions; ML/data pipeline must ensure no PII leaks into public search/index/embeddings.

2) Key Risk Areas (high-level)
- Embeddings/Vector Stores: if raw PII (emails, phone numbers, private notes) are embedded, vector DB can leak PII via nearest-neighbor queries or backups.
- Full-text Indexes / Logs: free-text founder bios and comments may contain contact info stored in search indices or logs.
- Model Training Data: training/fine-tuning on records containing PII creates persistence risk.
- Contact Flow: whether express_interest causes direct founder emails or internal mediation drastically changes storage & consent requirements.

3) Requirements (derived from product decision branches)
- If ventures are public by default: public API responses must contain no founder PII. Contact must be mediated or consented and stored encrypted.
- If express_interest sends direct emails: system must store founder contact info (email) and consent flags; access controls and encryption are mandatory.
- If express_interest routes to internal curation queue: store only internal pointers (no PII in public tables); contact info may live in a separate encrypted table with limited access.

4) Concrete ML/Data Safeguards (actionable)
A. Data ingestion / preprocessing
 - PII Detection: run automated PII detection (regex + named-entity models) on all incoming text fields. Tools: Presidio, spaCy + custom NER, or Google DLP.
 - Redaction Policy: remove/replace detected PII before creating embeddings or sending text to search indices. Replace with deterministic placeholders (e.g., <EMAIL_HASH:abcd1234>) when linking back is needed.
 - Hashing: for identifiers (emails), store salted hash (HMAC-SHA256 with service key) when you need dedupe/lookup without revealing email.
 - Consent Flags: require explicit consent boolean fields (consent_contact_public, consent_contact_direct). These flags flow with records and are indexed separately.

B. Embedding & Vector DB
 - Never index raw PII into embeddings. Remove or replace PII prior to embedding creation.
 - Store link → sensitive_contact_id instead of contact data in vector metadata. sensitive_contact_table is encrypted and access-restricted.
 - Rotate vector DB backups and ensure encryption at-rest and in-transit.

C. Storage & Access Control
 - Sensitive contact table: separate Postgres table with FK to venture_id. Columns: encrypted_email (envelope-encrypted or KMS), consent flags, contact_owner_id, created_at.
 - Use KMS (AWS KMS / GCP KMS / HashiCorp Vault) for envelope encryption keys. Restrict KMS decrypt to backend service role only.
 - Audit logging for any decrypt/access of contact table. Integrate with OpenTelemetry/Cloud Audit Logs.

D. Search & Logging
 - For Postgres/FTS and any search index (ES): ensure indexing pipeline redacts PII. Store redacted and original (encrypted) separately.
 - Do not log unredacted user-provided content to long-term logs. If ephemeral logs required, implement redaction in logging layer.

E. Model Training & Fine-tuning
 - Exclude PII-containing records from training datasets, or apply redaction before training.
 - When storing training artifacts, avoid embedding raw PII in model metadata.
 - Consider differential privacy (DP-SGD) only if models are trained on sensitive aggregated data and legal requires it—note DP impacts utility and training time.

F. Contact Flow Options (tradeoffs)
 - Direct Email (fast UX): store encrypted email, require founder opt-in, backend sends email via transactional provider (SES/Sendgrid). Requires consent management, unsubscribes, anti-abuse controls.
 - Mediated Queue (recommended for privacy-first): express_interest creates an internal task with venture_id + applicant metadata. Curator or founder-facing workflow handles outreach; public tables contain no PII.
 - Proxy Email (compromise): send an anonymized relay email (proxy@ourdomain) that forwards to founder if they opt-in. Requires infrastructure for reply handling and forwarding rules.

5) Operational & Monitoring Requirements
- Monitoring: instrument model & pipeline metrics (embedding creation count, PII redaction success rate, % of records with consent flags) in MLflow/Prometheus.
- Drift Detection: track distribution of redaction events & flagged PII types over time; alert if redaction rate jumps >X%.
- SLA/Latency: embedding pipeline should add <50ms overhead per record; batch embedding for ingestion to amortize cost.
- Retrain triggers: only run retrain pipelines on redacted datasets.

6) Acceptance Criteria (for ML/data)
- 0% of public API responses contain PII fields (emails/phones) in automated checks.
- Embedding store metadata contains no raw emails or phone numbers—only redacted placeholders or encrypted IDs.
- Sensitive contact table exists and is encrypted with KMS; access control policy applied and audited.
- Express_interest flow behavior implemented per product decision (direct vs mediated vs proxy) with consent checks.

7) Implementation Checklist (short actionable tasks)
- [S1] Implement PII detector + redaction step in ingestion. (tools: Presidio / spaCy)
- [S2] Modify embedding pipeline to accept redacted text and store only safe metadata.
- [S3] Create sensitive_contact table schema (encrypted fields) and KMS key policy.
- [S4] Add consent flags to venture record schema and propagate to downstream systems.
- [S5] Add unit/integration tests that assert no PII in public responses and in embeddings metadata.
- [S6] Instrument metrics for redaction coverage and consent rates.

8) Open Questions for Product/Backend (need answers to finalize design)
- Q1: Are ventures public by default? (yes/no)
- Q2: Which express_interest behavior should we implement? (direct_email | mediated_queue | proxy_email)
- Q3: Expected retention policy for contact data (30/90/365 days)? This affects encryption key rotation & access policies.
- Q4: Is there a legal requirement (e.g., GDPR data subject rights) we must support now (delete/export)?

9) Quick Decision Recommendations (if no time to deliberate)
- Default: Assume ventures are public and use mediated_queue for express_interest. This minimizes PII exposure while preserving UX for discovery.
- Store contact info in separate encrypted table; require explicit founder consent for direct emails.

10) Next steps & Owners
- Samantha (#ai-data): build ingestion redaction pipeline, provide sample sanitized dataset and current schema for contact fields. (See Next Steps below.)
- Marcus (#ai-backend): confirm contact-flow API behavior and where encrypted sensitive_contact table will live.
- Lisa (me): implement embedding pipeline changes and monitoring once redaction pipeline and sample data are provided.

Next Steps for Samantha (#ai-data) — required for me to start work:
1) Provide sample exported dataset (3–5K records) with the following columns: venture_id, title, description, founder_text, contact_email (if present), consent flags. If real PII cannot be shared, provide a realistic redacted/sampled version and note how PII is currently identified in source systems.
2) Share current Postgres table schemas for ventures and founders and any existing ETL code (or DVC pipelines) used for ingestion.
3) Confirm where encrypted sensitive_contact table should be hosted (same Postgres cluster or separate). Indicate KMS provider available.

Acceptance Criteria (for Samantha handoff)
- Redacted sample dataset provided to me in secure location (S3 or internal share). 
- Schema for contact & venture tables documented.

References & Tools
- PII Detection: Microsoft Presidio, spaCy NER, Google DLP
- Encryption: AWS KMS / GCP KMS / HashiCorp Vault
- Vector DB: Pinecone, Weaviate, or FAISS (ensure metadata does not include PII)
- Monitoring: MLflow, Prometheus, OpenTelemetry

-- End of document
