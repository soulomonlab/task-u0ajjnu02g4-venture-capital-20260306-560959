# Venture Capital Feature — Contact-Flow Privacy Review

## Overview
This document summarizes the backend privacy assumptions from the Venture Capital backend feasibility doc and lists the specific frontend policy decisions required to finalize backend storage, consent, and encryption requirements.

Reference: output/specs/venture_capital_backend_feasibility.md (Marcus)

## Background / Context
- The feature mixes public discovery (venture profiles) with privacy-sensitive contact flows (expressing interest in founders).
- Backend recommendation in feasibility doc: keep PII out of public responses, use backend-mediated contact flows, cursor pagination, and Postgres FTS for v1.
- Two frontend policy decisions will determine whether founder contact fields are stored and what consent/encryption controls are required.

## Questions for Frontend (Action items for Kevin / frontend team)
Please answer the two questions below and provide representative UI flows/copy where asked.

1) Are ventures public by default? (yes / no)
   - If yes: confirm whether any founder contact fields (email, phone, LinkedIn) should appear on public venture pages. If any contact is shown, specify which fields and whether they are shown only to logged-in users.
   - If no: specify the default visibility level (private / discoverable-with-approval / invite-only) and whether discovery listings will show anonymized placeholders.

2) For the express_interest flow, which behavior do you want?
   - Option A — Direct email: express_interest triggers an automated email to the founder with the request details.
     - If chosen: confirm that founder email will be stored and whether founders must opt in to receive direct requests. Provide required UI consent wording.
   - Option B — Internal curation queue: express_interest creates an interest record routed to an internal team for review and mediation; the internal team decides whether to share requester details with founders.
     - If chosen: confirm which team(s) will handle curation and what SLA is acceptable (e.g., 48 hours).

## Implications (What backend needs based on each answer)
- Ventures public = true
  - No founder PII should be included in public API responses by default.
  - If any contact field is to be visible, backend must store founder contact fields encrypted at rest and only reveal via authenticated endpoints.
  - Consent flags required: founder_contact_public (bool), contact_sharing_consent (enum: none/anonymous/identifiable).

- Express_interest → Direct email
  - Backend must store founder email (encrypted) and implement a mailer integration.
  - Founders must have an explicit opt-in (consent) to receive direct requests. Store consent timestamp and IP.
  - Audit trail required: record of interest events, sender id, timestamp.

- Express_interest → Internal curation queue
  - Backend stores interest records without founder PII. Interest record schema: {interest_id, venture_id, requester_id (nullable for anonymous), request_message, status, created_at}.
  - Internal UI / admin queue required; SLA monitoring and notification hooks.
  - Lower regulatory risk; no founder email storage required.

## Recommended Defaults and Rationale (writer recommendation)
- Recommend Option B (Internal curation queue) as default for v1 to minimize PII exposure and simplify compliance. This is reversible: backend can add direct-email flow later once consent UX and legal review are complete.
- Recommend ventures default to "public discovery" but with no founder PII in public responses. Founder contact fields should be stored encrypted and only surfaced after explicit consent / mediated request.

Reasoning: reduces legal/privacy blocker risk raised in the feasibility doc and speeds time-to-market for discovery while preserving the ability to enable direct contact later.

## Required API/Schema Notes (for backend once frontend decisions are made)
- express_interest endpoint payload additions:
  - requester_id (UUID / nullable)
  - request_message (string)
  - contact_method (enum: "direct_email", "curation_queue")
  - consent_flag (boolean) — if direct email flow chosen

- Founder contact storage:
  - Store emails/phones encrypted with KMS-managed keys, access-scoped via backend service account.
  - Consent table: {founder_id, consent_type, decision, timestamp, ip_address}

## UI Copy suggestions (quick-start text to use)
- For express_interest button: "Express interest" → opens modal
- Modal header (curation queue default): "Send an introduction request"
  - Body: "We will review your request and may share it with the founder. The founder's contact info is not public."
  - Consent checkbox (if direct email): "I consent to share my contact details with the founder for the purpose of an introduction." (required)

## Acceptance Criteria
- Frontend provides answers to the two questions above with sample user flows and proposed UI copy.
- Backend (Marcus) will confirm any additional required fields after frontend choices.

## Next Steps (what I need from frontend)
1) Kevin (Frontend) — Answer the two questions and paste sample modal mockups or copy here.
2) Once you answer, Chris (Support) will coordinate with Marcus to confirm backend schema and with product for legal/consent language.

Estimated time to finalize after answers: 1–2 dev days for backend adjustments (depending on direct email vs curation queue).
