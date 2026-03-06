Title: ML Feasibility — Venture Capital PRD

Situation
- Product/Backend created a backend feasibility doc for the Venture Capital PRD (APIs, Postgres sketch, infra, compliance notes).
- Engineering needs a matching ML feasibility to estimate effort, data needs, API contracts, and infra so implementation can proceed.

Complication
- The PRD mentions multiple ML-style features (e.g., deal scoring, recommendation, entity extraction, firm matching) but lacks concrete data specs, label definitions, and latency/accuracy targets needed to choose an approach.
- Privacy/PII and consent constraints affect what can be used for training and what must be encrypted/anonymized.

Resolution (deliverable)
- Created this ML feasibility doc describing: problem definition, recommended approach (fine-tune vs RAG vs heuristics), data requirements (fields, labels, volumes), infra + serving options, evaluation metrics, monitoring/drift plan, privacy constraints, and a day-by-day effort estimate.

1) Core ML problem definitions (MECE)
- Deal Classification / Scoring: predict a "deal attractiveness" score (regression) or class (high/med/low) per deal for portfolio fit.
- Deal Recommendation / Matching: given user/firm profile, return ranked deals (learning-to-rank / retrieval + re-rank).
- Entity Extraction & Normalization: extract company names, sectors, funding round types, amounts from free-text deal descriptions (NER + normalization).
- Outcome Prediction: probability of a deal reaching Series A / exit within X months (binary classification / survival analysis).

2) Approach & trade-offs
- Fine-tune Transformer (BERT / DeBERTa) for text-heavy tasks (NER, classification, scoring) — pros: high accuracy, single model footprint; cons: needs labeled data (>=1k-5k examples depending on task), GPU training.
- RAG (embedding + vector DB + generator) for ad-hoc retrieval from docs and explainable evidence — pros: works with smaller labeled datasets, good for long-form reasoning; cons: higher infra (vector DB, chunking), higher latency.
- Heuristics / Rule-based + Classic ML (XGBoost on structured features) for initial MVP — pros: fast to prototype, low data need; cons: limited accuracy on text-heavy signals.

Recommendation (reversible)
- Phase 1 (MVP): hybrid approach
  - Build structured-feature XGBoost baseline for scoring/ranking using existing structured fields (sector, stage, amount, investor history).
  - Implement a lightweight Transformer fine-tune for NER and text scoring if >=2k labeled examples exist.
  - Use a vector store (Milvus/Weaviate or Elastic) in shadow mode for RAG to support future explanations.
- Phase 2: upgrade to RAG or fine-tuned ranker once we have labeled signals and performance targets unmet by heuristics.

3) Data requirements (exact fields & examples)
- Required (minimum for baseline):
  - deal_id (string)
  - title / headline (text)
  - description / notes (long text)
  - company_name (string)
  - sector_tags (list)
  - funding_stage (enum: seed, series_a...)
  - amount_usd (numeric)
  - round_date (date)
  - lead_investor_ids (list of investor_id)
  - outcome_label (optional; binary/enum) — whether deal led to follow-on or exit (for supervised tasks)
  - created_at, updated_at (timestamps)

- Helpful (increase model quality):
  - founder_profiles (free text or structured: years_experience, prior_exits)
  - firm_profile (for matching): AUM, thesis_tags
  - user_interaction_logs: views, saves, click-through, time_spent (for implicit feedback learning-to-rank)
  - external signals: crunchbase_id, linkedin_counts, web_traffic metrics

- Labeling guidance:
  - Outcome label definition must be precise: e.g., "Follow-on funding within 18 months" = positive.
  - If using human labels for attractiveness, provide labeling rubric + agreement target (Cohen's kappa >0.6).

4) Data volume guidance
- NER / classification: 2k–10k labeled examples per class for stable Transformer fine-tune. If <2k, expect to start with weak supervision / data augmentation.
- Recommendation (learning-to-rank): ~50k implicit interactions (clicks/saves) to train a reasonable ranker; for cold-start, combine content-based heuristics.

5) API & integration points with backend
- Two integration patterns:
  - Synchronous low-latency endpoint (real-time): /api/v1/ml/predict_deal_score -> returns score + confidence + explanation_id. Target p95 latency <50ms for text-free requests; <150ms if model does light text encoding.
  - Asynchronous batch endpoint: /api/v1/ml/score_batch -> accepts list of deal_ids, returns job_id + results when ready.
- Explanation flow (RAG or evidence): explanation_id references a stored evidence object in S3/DB; backend can fetch on demand to avoid inflating response size.
- Contract notes for backend: provide normalized fields (company_name, description cleaned) and a canonical deal_id. Backend to call ML service with only non-PII fields unless PII consent is present.

6) Serving & infra recommendations
- Training infra: GPU-enabled training (1-2 A100/RTX6000 equivalent for <4h runs) managed via Ray or PyTorch lightning; store artifacts in MLflow + S3.
- Serving:
  - Real-time: BentoML or TorchServe behind FastAPI with autoscaling; use Redis for warm cache of embeddings.
  - Vector DB: Milvus / Weaviate / Elastic + ANN (HNSW) for RAG / semantic search.
  - Experiment tracking: MLflow; model registry with stage tags (staging, prod, canary).
- Monitoring: Prometheus + OpenTelemetry for latency; ML monitoring stack (WhyLabs, Evidently, or custom) for drift.

7) Privacy, compliance & PII handling
- PII fields (founder emails, personal LinkedIn URLs) must be redacted/anonymized before storing in S3 for training, unless explicit consent exists.
- Use field-level encryption in DB for any sensitive personal fields; in training, prefer hashed IDs or tokenized substitutes.
- Audit logs for data access; retention policy aligned with legal (configurable per region).

8) Evaluation & acceptance criteria
- Minimum: baseline XGBoost ranker beat naive heuristic by CTR or NDCG@10 by 10% on validation set.
- Target ML metrics (example):
  - Deal scoring: RMSE < X or classification F1 > 0.85 (task dependent)
  - Recommendation: NDCG@10 improvement >=10% over baseline; online A/B to validate uplift.
  - NER: F1 > 0.90 for entity types in production.
- Latency: real-time endpoints p95 < 50ms (no heavy text); up to 150–200ms if embedding + ANN lookup.

9) Monitoring & retraining strategy
- Log predictions + ground-truth when available to compute daily accuracy and data distribution stats.
- Drift detector: daily KS test or PSI on key features; retrain trigger on >5% metric degradation.
- Canary rollout + shadow mode: always run new model in shadow before promoting.

10) Day-by-day effort estimate (ML scope only)
- Data discovery & quick sample pull (with #ai-data): 2 days
- Data cleaning & labeling plan (weak supervision rules, labeling UI): 3 days
- Feature engineering & baseline model (XGBoost): 3 days
- Transformer NER/score baseline & experiments: 4 days
- Evaluation, monitoring hooks, MLflow, deployment scaffolding (BentoML): 3 days
- Buffer & integration fixes with backend: 2 days
Total: 17 ML days (P1). Notes: if labeling effort delegated to SMEs, add more days for annotation.

11) Costs & infra rough numbers
- Storage: S3 for data + artifacts
- Vector DB small cluster: $200–800/mo depending on scale
- Training: spot GPU instances for experiments; expect $100–400 per major training run

12) Next steps (concrete asks)
- #ai-data / Samantha: provide a 10k-row anonymized sample CSV (parquet preferred) containing the required fields above with 1–2 example outcome labels. Include a schema and a mapping of PII columns. (See detailed next_steps below.)
- Backend: confirm ML synchronous endpoints and canonical field names for the payload.
- Product: confirm business metric for "attractiveness" (CTR uplift, deal conversion rate) and acceptable latency.

Acceptance criteria for handoff:
- Sufficient data sample (10k rows) and schema from #ai-data
- Backend agrees on endpoint contract and provides canonical deal_id
- Product defines business metric to optimize

Document author: Lisa (ML/AI Engineer)
Date: 2026-03-06
