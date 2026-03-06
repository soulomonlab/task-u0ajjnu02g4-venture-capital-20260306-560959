Title: PII Retention & Search UX — Design Implications

Purpose
- Summarize UX requirements and design decisions resulting from product's PII retention/deletion policy and search QPS sizing (as provided by Product).
- Provide concrete UI components, user flows, and backend data/contracts needed for implementation.

Scope
- User-facing flows impacted: Data Export (User Data Request), Delete / Forget Me (Account Deletion & Data Retention), Consent & Retention Notices, Admin tools for data lifecycle.
- Search UX changes required to handle expected QPS and autoscale behavior.

Assumptions
- Product decisions (retention windows, encryption, RBAC, search QPS baseline/scale) are available in output/specs/venture_capital_product_decisions.md.
- Backend will provide endpoints to request exports, request deletion, check status, and indicate retention expiration.

Key UX Requirements (high level)
1. Explicit, discoverable paths for users to request their data export and deletion.
2. Clear communication of retention timelines and what "delete" means (soft-delete vs. permanent removal timing).
3. Feedback/status UI for asynchronous operations (export generation, deletion scheduling).
4. Admin UI controls for legal/vendor reviews and manual overrides.
5. Search UI resilient to throttling/partial results: debounced search, progressive loading, and clear error states.

User Flows (step-by-step)
1) Data Export (User-initiated)
- Entry points: Account Settings > Privacy → "Request data export"; Support chat; Legal request link.
- Flow:
  a. User clicks "Request data export" → show modal explaining what will be included, estimated time (e.g., 24–72 hrs), and retention of exported file.
  b. User confirms → frontend POST /users/:id/export
  c. Show status widget in Privacy page: states = Pending, Processing, Ready, Failed. Poll GET /users/:id/export/status or subscribe to websocket/event.
  d. When Ready → provide downloadable link (signed URL, expires), log audit entry.

2) Delete / Forget Me
- Entry points: Account Settings > Privacy → "Delete account / Delete my data".
- Flow:
  a. Click shows clear explanation of retention policy (e.g., data retained until X date, backup windows, legal holds) and the irreversible consequences.
  b. Require explicit confirmation: type account name or checkboxes for consequences. Optionally allow temporary deactivation.
  c. On confirm → POST /users/:id/delete-request (records deletion_request_at). Show scheduled deletion date if soft-delete window exists (e.g., 30 days).
  d. Status widget shows: Requested, In Review (if legal), Scheduled (countdown), Completed.
  e. If legal/vendor review or manual step required, show contact link and expected timeline.

3) Consent & Retention Notices
- Place short retention summary in Privacy page and during onboarding where PII collected.
- Components: small inline badge "Data retained until [date]" on profile fields when applicable.

4) Admin UX (for data lifecycle)
- Admin panel list of deletion/export requests with filters: pending/processing/failed, legal_hold flag.
- Allow manual override: escalate, cancel, or mark as completed.

Component Specifications
- Privacy Settings Page (Account Settings)
  - Sections: Data Export, Delete Account, Data Retention Summary, Consent History
  - Components:
    * CTA Button: Request Data Export (primary)
    * CTA Button: Delete Account (danger)
    * Status Card: shows latest export & deletion requests with timestamp and action links
    * Modal: Export Confirmation (body text, estimated time, Cancel/Confirm)
    * Modal: Delete Confirmation (type-to-confirm, list of consequences)

- Export/Deletion Status Widget
  - Visual states: Pending (gray), Processing (spinning), Ready (green + download), Failed (red + retry/help)
  - Accessibility: ARIA-live region updates for status changes

- Search Input (global)
  - Debounce input: 300ms
  - Minimum characters before server call: 2
  - Show spinner while searching, show partial/streaming results if backend returns incremental results
  - Limit live autocomplete to 50 items; provide "View all results" for paginated page
  - Error state: show friendly message ("Search temporarily unavailable — try again") and fallback suggestions

Wireframes (ASCII)
Account Settings — Privacy (desktop)

[Account Settings]
- Privacy -------------------------------
| Data Export                  | [Request Data Export] |
| Last Export: 2026-02-28      | Status: Ready (Download)
|-------------------------------|----------------------|
| Delete Account               | [Delete Account] (danger)
| Deletion Status: Scheduled: 2026-03-10 (7 days)
|-------------------------------|----------------------|
| Data Retention: We retain profile PII until 90 days after deletion. [Learn more]

Export Modal
[Title: Request your data export]
- Includes: bullets of what's included, est. time: 24–72 hrs
- Buttons: Cancel | Confirm (primary)

Search (global)
[Search ▾] [ input ________________ ] [🔍]
- Results dropdown: streaming list up to 50 items
- Footer: View all results → /search?q=...

Decisions & Trade-offs (one-line each)
- Soft-delete with scheduled permanent deletion vs immediate hard delete: Chosen = soft-delete (enables undo & legal hold). Reason: reduces accidental loss; reversible within retention window. Backend must store deletion_request_at and retention_expires_at.
- Export generation async: Chosen = async background job producing signed URL. Reason: large data bundles and compliance.
- Search UI: Client-side debounce + server-side throttling/backpressure. Reason: reduces QPS peaks and improves perceived performance.

Backend Contracts & Data Requirements (for DB schema & API)
- Users table: add columns
  - pii_deleted_at (nullable timestamp) — when permanent deletion happened
  - deletion_requested_at (nullable timestamp) — when user requested deletion
  - retention_expires_at (nullable timestamp) — calculated deletion time per policy
  - retention_policy_version (string) — to track policy at time of request
- Exports table
  - id, user_id, requested_at, status (pending/processing/ready/failed), completed_at, file_url (signed), file_size, checksum, expires_at
- Consent / Audit table
  - id, user_id, consent_type, given_at, revoked_at, source, version
- LegalHold table (optional)
  - id, user_id, reason, placed_at, released_at

Required API endpoints (UX needs)
- POST /users/:id/export -> 202 Accepted (returns export_id)
- GET /users/:id/export/:export_id/status -> 200 with status + signed URL when ready
- POST /users/:id/delete-request -> 202 Accepted (returns scheduled_deletion_date)
- GET /users/:id/deletion-status -> 200 with current state
- Admin endpoints to list/manage requests
- Webhook or Event subscription: push export_ready / deletion_completed events to frontend OR use polling

Acceptance Criteria (for backend tasks to close)
- DB schema contains fields above and migrations have tests
- Export endpoint returns export_id quickly; background job generates file and sets URLs with expiry
- Deletion request records retention_expires_at and does not permanently remove PII before that point
- Endpoints return sufficient info for UI states (timestamps, status, reason for failure)

Design Notes / Accessibility
- All confirmation modals require keyboard focus trap and clear ARIA labels
- Status updates must use ARIA-live to inform screen reader users of asynchronous state changes

Implementation Notes for Frontend
- Polling interval for status: 10s with exponential backoff; allow websocket if available
- Debounce 300ms for search input; client-side caching of recent queries

Open Questions for Product/Backend (need answers before finalizing UX)
1. Exact retention window (days) and whether admin can override per-user — impacts UI copy & scheduled dates
2. Whether deletion is reversible within the retention window (undo flow) and if so how the UI should allow it
3. Legal hold workflow: will legal place holds via backend API or manually in admin UI?

Deliverable
- This spec outlines UX requirements and the backend contracts needed to implement the flows. It is intended to be used by Backend (Marcus) to create GH tasks and by Frontend (Kevin) to implement UI.

Design owner: Maya (UX)
File: output/design/pii_retention_and_search_ux_implications.md
