# Product Decisions: Venture Capital Backend

**Author:** Alex (Product Owner)
**Purpose:** Record product-level decisions required by backend feasibility work (PII, search sizing, GH issue ownership, priorities).

## Situation
Marcus delivered the backend feasibility doc: output/specs/venture_capital_backend_feasibility.md (RLS multi-tenant, OpenSearch, PII scope & encryption, JWT/RBAC, observability, estimates = 26 dev-days). Marcus requested product confirmation on PII retention/deletion policy, expected search QPS, and whether he should create GitHub issues directly.

## Decisions (Product)
1. PII scope
   - PII to be considered: full name, email, phone number, government IDs (if collected), company affiliations, direct contact addresses, banking/financial account details, investment transaction details tied to individuals.
   - Non-PII: aggregated/derived analytics and anonymized identifiers.

2. PII retention & deletion policy
   - Default retention: retain PII for up to 7 years after a user's last account activity or account closure to satisfy potential legal/contractual requirements.
   - Deletion on user request: support user-initiated deletion (data subject request). Deletion flow:
     - Step 1 (Immediate): mark account as deleted (soft-delete) and disable access immediately.
     - Step 2 (Recovery window): keep encrypted backups & soft-deleted records for 90 days for accidental recovery and legal hold processing.
     - Step 3 (Permanent purge): after 90 days, permanently purge PII from primary DBs, backups, and search indexes unless a legal hold is active.
   - Legal holds / compliance exceptions: if legal/contractual obligations require longer retention, preserve relevant records and log the exception.
   - Data export: support data-export of PII in machine-readable format for compliance requests within 30 days.

3. PII protection requirements
   - Encryption: all PII encrypted at rest using KMS-managed keys. Field-level encryption for government IDs and financial details.
   - Access controls: strict RBAC; only authorized service accounts or roles may access raw PII. Use audit logging for all accesses.
   - Pseudonymization: where possible, store a pseudonymized identifier for search/analytics and keep mapping in an encrypted, access-restricted store.
   - Deletion propagation: deletion must remove PII from primary DB and from OpenSearch indexes (prefer tombstone + reindex pattern and immediate index document deletion where feasible).

4. Search QPS sizing (product expectation)
   - Target: MEDIUM baseline. Define ranges: Low <100 QPS, Medium 100–1000 QPS, High >1000 QPS.
   - MVP baseline target: 200 QPS sustained, with capacity to autoscale to 2,000 QPS during peak events.
   - Rationale: expected user base and search-heavy workflows justify Medium baseline to avoid early throttling; Marcus should design with autoscaling and circuit-breakers so we can adjust.

5. GH issue creation & ownership
   - Decision: Yes — Marcus should create the GitHub issues directly for each backend subtask described in the feasibility doc.
   - Requirements for each GH issue Marcus creates:
     - Must include the estimate (dev-days) from the feasibility doc.
     - Clear acceptance criteria (what success looks like) — follow the acceptance criteria template in the doc.
     - Label with appropriate priority (P0/P1) and backend label.
     - Flag any items that require legal review or vendor procurement (PII handling, KMS, OpenSearch infra costs).

6. Prioritization (product)
   - P0 (start immediately / blocking):
     - PII handling primitives: encryption at rest & field-level encryption, data deletion flow, and audit logging.
     - Auth & RBAC: JWT/RBAC implementation and integration points.
     - DB schema & migrations for user/PII tables (Marcus estimated 3 dev-days).
   - P1 (next):
     - OpenSearch provisioning & index design for search.
     - Observability & metrics.
   - P2: non-blocking features and performance tuning.

## Acceptance handoffs / Next steps for Backend
- Marcus to create GH issues for each backend subtask listed in the feasibility doc. Each issue must include estimate and AC.
- Marcus to start DB schema & migrations after creating GH issues (estimate 3 dev-days).
- Any task touching PII that has ambiguous legal implications must be flagged and routed to Legal (we will coordinate).

## Success criteria (product)
- GH issues created and triaged within 48 hours.
- DB schema PR opened within 5 business days.
- Search infra designed to handle 200 QPS baseline; load tests show autoscaling works up to 2,000 QPS before GA.
- Data subject deletion flow implemented and tested (end-to-end) with audit logs.

## References
- Backend feasibility doc: output/specs/venture_capital_backend_feasibility.md

