Situation

Emma requested frontend confirmation on two privacy choices needed by backend:
1) Whether ventures are public by default
2) Which express_interest flow to use (direct email vs internal curation queue)

These choices affect PII storage, consent flags, encryption, and whether mailer integrations are used. This doc references Marcus's backend feasibility doc: output/specs/venture_capital_backend_feasibility.md

Decisions (conclusion)

- Ventures public by default: NO. Ventures are private by default. Public listing shows only non-PII summary metadata (company name, short description, industry, stage, and optional logo). Founder contact fields (email, phone, personal LinkedIn URL) are NOT visible publicly.
- Express interest behavior: OPTION B — Internal curation queue for v1. Frontend will collect an interest request and a required consent flag; requests go into a curation queue for manual review before founder contact is shared or an email is sent.

Rationale (one line each)

- Privacy-first launch reduces PII exposure and keeps initial backend scope smaller (no immediate mailer or direct-email flow required).
- Internal curation reduces accidental spam and enables building curator tooling later; reversible to direct-email in v2.

Frontend UX decisions (what the UI will do)

- Listing page / venture card
  - Show only: company_name, short_blurb (<=140 chars), industry tags, stage, logo/avatar, and a CTA "Express interest".
  - No founder contact info shown.

- Venture detail page
  - Show same public metadata plus expanded description and team roles (names and public titles only). Do NOT display direct contact fields.
  - Show CTA: "Express interest" (primary) and a small note: "Founder's contact is private. Express interest to request an introduction."

- Express Interest flow (modal)
  - Trigger: Click "Express interest" → if not logged in, show auth required modal and redirect to login/signup. After auth, re-open the Express Interest modal.
  - Modal fields:
    - Header: "Request an introduction"
    - Description: "We'll forward your request to the curation team. They will review and may share founder contact info if appropriate."
    - Optional short message textarea (max 500 chars) placeholder: "Write a short note to the curator: why you want to connect, relevant context, and what you can offer."
    - Required checkbox (consent): "I consent to sharing my name and email with the venture's team if the curator approves this request." (must be checked)
    - Optional checkbox: "I agree to be contacted about this request and related opportunities." (opt-in for marketing; not required for intro)
    - Primary CTA: "Submit request" (disabled until consent checkbox checked)
  - After submit: show confirmation state "Request submitted — Pending curation" with estimated review time (e.g., 48–72 hours). Show button "View my requests" linking to a user requests dashboard.

Required copy snippets (ready for designer)

- Express interest button: "Express interest"
- Modal title: "Request an introduction"
- Modal description: "We'll forward your request to our curation team. If approved, we'll share your request with the founders or facilitate an introduction." 
- Consent checkbox (required): "I consent to sharing my name and email with the venture's team if the curator approves this request." 
- Confirmation toast: "Request submitted — Pending curation"
- Anonymous viewers note (on detail page): "Founder's contact is private. Sign in to request an introduction."

Frontend API / Schema requirements (what frontend needs Marcus to implement)

- Endpoint: POST /api/v1/ventures/:id/express-interest
  - Request body:
    {
      "message": string | null,
      "consent_to_share_contact": boolean, // required
      "consent_to_contact_for_marketing": boolean, // optional
      "requester_id": string (current user id) // server fills from token, but frontend may pass for auditing
    }
  - Response:
    202 Accepted
    {
      "request_id": string,
      "status": "pending" // other states: approved, rejected
    }
  - Errors:
    401 if not authenticated, 422 if consent missing

- Expected backend behavior for chosen flow (for Marcus):
  - Do NOT send any direct email to founders in v1. Store the interest request and set status "pending_curator_review".
  - Store the following fields (encrypted at rest if PII): message, requester_id, requester_name, requester_email, consent_to_share_contact (boolean), consent_timestamp.
  - The venture record should NOT expose founder_email/phone in any public GET responses.

- Required flags/fields for DB:
  - interest_requests table with columns: id, venture_id, requester_id, message (encrypted?), consent_to_share_contact (bool), consent_timestamp, status, created_at, updated_at
  - ventures.founder_contact (encrypted, access-controlled) — not returned by public endpoints

Acceptance criteria (frontend)

1. Default state: On listing and detail pages, no founder contact info is visible to anonymous or logged-in users.
2. Express interest CTA present and opens modal. If not logged in, prompt to sign in; after auth, reopen modal.
3. Consent checkbox is required. Submit button disabled until checked.
4. Submit POSTs to /api/v1/ventures/:id/express-interest and handles 202 response by showing a confirmation UI and creating a row in the user's requests dashboard.
5. Error handling: show validation errors (missing consent), 401 redirect to login, and a generic toast for 5xx errors with retry option.
6. Accessibility: modal is focus-trapped, labels associated, keyboard operable, and screen-reader friendly.

Trade-offs & next steps

- Trade-off: Internal curation increases manual work but minimizes PII exposure and risk. Direct email would be faster for users but requires mailer integrations, rate-limiting, and additional anti-spam safeguards.
- Reversible path to direct-email: backend should support an eventual flag on interest_requests (channel: 'curation' | 'direct_email') and mailer triggers only when channel == 'direct_email'.

Files referenced

- Backend feasibility doc: output/specs/venture_capital_backend_feasibility.md

If Marcus needs further clarifications on field names or encryption expectations, ask for the exact JSON shapes and which fields will be encrypted vs tokenized.
