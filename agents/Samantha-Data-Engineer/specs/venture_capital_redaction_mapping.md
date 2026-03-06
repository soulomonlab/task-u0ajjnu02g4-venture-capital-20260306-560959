Redaction & Pseudonymization Mapping for Venture Capital dataset

Purpose
- Provide rules for redacting or pseudonymizing PII in the sample dataset used by ML and feature flows.

Fields and rules
1) contact_email
   - If consent_contact = false (no consent to be contacted): value = "<REDACTED_EMAIL>" in dataset used for discovery/embeddings.
   - If consent_contact = true: store synthetic but realistic email in sample dataset (e.g., alice.smith@example.com). In production, replace with pseudonymization: store sha256(salt || email) in sensitive_contact mapping table and only expose pseudonym/hash to downstream systems needing identity-preserving joins.

2) founder_text / founder names
   - In sample dataset: keep synthetic full names / bios to preserve text shape.
   - In production: pseudonymize real names in any public-facing embeddings: replace real name tokens with "[NAME]" or hashed tokens depending on embedding safety.

3) description / title
   - Keep verbatim if not containing direct PII. If direct PII (phone numbers, emails) appear, strip/replace with placeholders: PHONE_REDACTED, EMAIL_REDACTED.

4) consent flags
   - Keep as booleans: consent_contact (can we contact), consent_share (can we share profile externally).

Pseudonymization & mapping table
- sensitive_contact table (encrypted) stores: contact_id, venture_id, email_hash (sha256 + salt), email_enc (KMS-encrypted value), created_at.
- Mapping rules: salt is per-environment secret (not per-row). Hash only used for joins; encrypted email (email_enc) is the source-of-truth and decrypted only in secure contexts.

Notes
- Do NOT include raw real PII in any shared dataset. Use synthetic emails or redacted placeholders.
- For embeddings: remove or mask direct contact tokens before embedding to prevent leakage.

Generated sample approach
- The sample generator creates 3,000 rows of synthetic venture data.
- ~30% of rows have consent_contact = true and contain synthetic emails; remaining rows have contact_email="<REDACTED_EMAIL>".

Location of artifacts (this file was written as part of the deliverable): output/specs/venture_capital_redaction_mapping.md
