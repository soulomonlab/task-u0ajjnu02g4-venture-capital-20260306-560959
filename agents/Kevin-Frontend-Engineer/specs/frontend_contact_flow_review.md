Frontend contact-flow & privacy review

Summary decisions (frontend position):
1) Are ventures public by default? — YES, ventures should be public by default, but public responses must contain NO PII. Public fields are limited to: id, name, tagline, industry_tags, location (city, region only), logo_url, short_bio, and public_metrics (raise_amount, stage). Do NOT include founder contact fields (email, phone, personal linkedin) in any public API response.

2) Should express_interest send direct emails to founders or route to an internal curation queue? — ROUTE TO AN INTERNAL CURATION QUEUE (backend-mediated). Do NOT send direct emails from a public API call.

Rationale (short):
- UX: Making ventures discoverable by default improves discovery and conversion. Designers can show a rich public card without exposing sensitive data.
- Privacy & Safety: Founder contact is PII and a high-abuse target. Public direct-emailing invites scraping, spam, and legal/consent issues.
- Product Control: Backend mediation allows rate-limits, spam detection, consent verification, and manual curation for high-value introductions.
- Reversibility: Start backend-mediated now (safer). If later we enable direct email for vetted ventures, add an explicit opt-in and encrypted storage + audit trail.

Frontend implications (requirements for backend API & data shape):
- Public venture shape (no PII):
  interface VenturePublic {
    id: string;
    name: string;
    tagline?: string;
    industry_tags: string[];
    location?: { city?: string; region?: string };
    logo_url?: string;
    short_bio?: string;
    public_metrics?: { raised_usd?: number; stage?: string };
    created_at: string;
  }

- Private contact fields stored server-side only. Public endpoints MUST NOT return founder_contact or founder_email.

- Express interest API (backend-mediated) suggestion:
  POST /api/v1/ventures/:id/express_interest
  Body: { message?: string; user_id?: string; captcha_token?: string }
  Response: { status: 'queued' | 'rejected' | 'blocked', interest_id: string, moderation_eta?: string }

  GET /api/v1/ventures/:id/interest_status?interest_id=...
  Response: { interest_id, status: 'queued' | 'approved' | 'rejected', contact_mediation?: { method: 'email' | 'internal', eta?: string } }

- If backend later supports direct contact: require fields on venture record: contact_consent: boolean, contact_encrypted_blob: string (encrypted at rest, not returned in any public response), contact_last_verified: timestamp.

Frontend behavior and UX flows (high level):
- Venture list / search: show VenturePublic cards with CTA "Express interest".
- Express interest flow: clicking CTA opens modal with optional message input, privacy/consent copy, checkbox to allow sharing user email with founders (if backend supports sharing later), and submit.
- After submit: show queued state + eta. Do not show founder contact information until mediation approves and backend returns a safe channel (e.g., anonymized thread or approved email). Show clear copy about what "queued" means.
- Error & rate-limit handling: show descriptive errors for blocked (abuse), captcha required, network errors, and 429 rate-limits. Provide retry affordance and contact support link.

Security, privacy, and product guardrails (must-haves):
- No PII in venture listing or search responses.
- Express_interest must be rate-limited per user and per IP. Consider CAPTCHA after threshold.
- Audit log for each express_interest with actor id, timestamp, message, IP, and moderation decisions.
- Backend must provide a tokenized/mediated contact channel instead of raw emails (e.g., anonymized messaging or a queued introduction email sent by backend after checks).
- Consent flags and encryption for any contact data stored. Frontend should never receive raw contact data.

API contract / acceptance criteria for frontend integration (what I need from Marcus):
1) Confirm public venture fields and that founder contact will NOT be returned by the public endpoints. If any contact field is required for the UI, it must be returned as a boolean (contact_available: true) with no contact data.
2) Provide exact express_interest endpoint (URL, request and response JSON schema) and rate-limit rules (requests per minute/hour/day) and expected response codes (200/202/4xx/429/5xx).
3) Provide mechanism to poll interest status or a webhook/notification flow when mediation completes.
4) If you plan to support direct emails for approved ventures: provide the schema for consent flags (contact_consent boolean) and the secure retrieval path for contact data (backend-only endpoints with RBAC). Also indicate required encryption/rotation expectations.

Frontend acceptance tests (to be implemented by #ai-qa):
- Express interest happy path: open modal, submit message, receives queued response, UI shows queued state.
- Express interest denied path: submit and receive blocked/rejected, UI shows correct message and prevents retry for configured cool-down.
- Rate-limit: exceed threshold and receive 429; UI shows retry after header or custom message.
- No PII leakage: public API responses do not contain email/phone fields.
- Accessibility: modal is keyboard-focus trapped, labels present, aria-live used for status updates.

Recommendation (one-line):
- Ventures public by default (non-PII only). Express_interest must route to an internal/mediated queue — do not send direct emails from the public flow.

Next steps for backend (what I need from Marcus):
- Confirm the 4 API points under "API contract / acceptance criteria" and share OpenAPI snippets or example payloads.
- If you decide to allow direct contact for vetted ventures, produce the consent & encryption spec so frontend can render the correct UI.
