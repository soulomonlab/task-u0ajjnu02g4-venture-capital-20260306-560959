# Venture Capital Feature — Design Spec

## Situation
Alex created a discovery PRD for the venture capital product opportunity (see: output/specs/venture_capital_request_spec.md). Engineering needs feasibility and effort estimates before implementation.

## Purpose of this document
This design spec provides a clear user flow, wireframes, component specs and the UI-driven data/API contract required by backend to estimate feasibility and effort. It is intentionally implementation-friendly: each UI action maps to the minimal data the backend must provide.

---

## Target users & primary goals
- Founder (early-stage): discover VC funds, request intros, submit pitch decks
- Investor / Scout: browse deals, tag interest
- Internal Ops / Analyst: manage fund profiles, moderate submissions

Primary user goals
- Quickly discover relevant VCs by stage, sector, geography
- Learn fund details and partner bios
- Submit or request an intro in 1–2 flows

Assumptions
- Auth exists (OIDC/email) and we can surface user role
- Initial scope: web (desktop-first) + responsive mobile next

---

## Key flows (high level)
1. Fund discovery (search + filters) -> fund card list -> open fund detail
2. Fund detail -> view partners, portfolio, thesis -> Request intro / Save
3. Submit pitch -> Upload deck + answer 3 screening questions -> confirmation
4. Manage submissions (internal) -> review, change status, assign partner

---

## Wireframes (ASCII)

1) Discovery / Search results (desktop)

[Header: Search | Filters▾ | My Submissions]
---------------------------------------------------------------
| Left filters (vertical): Stage, Sector, AUM, Location, Check size |
|-------------------------------------------------------------|
| [Search results grid]                                         |
| -----------------------------------------------------------   |
| Card: [logo] Fund Name (Stage)                                  |
| Tagline / Thesis                                                |
| Key metrics: AUM • Avg check • HQ                                 |
| Buttons: [View] [Request Intro]                                  |
| --------------------------------------------------------------- |

2) Fund Detail (desktop)

[Fund name] [Follow] [Share]
-----------------------------------------------
| Hero: logo, one-liner, HQ, AUM, typical stage, website       |
| Tabs: Overview | Partners | Portfolio | Terms | Contact       |
| Overview: short thesis + 3 bullets (focus areas)              |
| Partners: list with photo, role, short bio, LinkedIn          |
| Request Intro CTA (prominent)                                |
| Recent investments (carousel)                                 |

3) Request Intro modal

[Modal]
Title: Request Intro to <Fund Name>
Form:
- Role (Founder / Scout) [auto-fill from profile]
- Stage / Ask (select)
- Short pitch (text, max 300 chars)
- Upload deck (optional, pdf/docx)
- Preferred intro target (dropdown of partner emails if visible)
Buttons: [Send request] [Cancel]

States: success banner with next steps; errors for missing pitch or upload too large.

---

## Component spec (desktop + responsive notes)

1. Fund Card
- Elements: logo (40x40), fund name (h3), one-line thesis (14px), metadata row (icons + text), CTA primary (View), CTA secondary (Request Intro)
- Interaction: clicking card or View opens Fund Detail; Request Intro opens modal
- Accessibility: buttons keyboard-focusable, alt text for logos

2. Filters panel
- Multi-select chips for sector/stage
- Range sliders for AUM / Check size
- Clear all button
- Performance: server-side filter & cursor pagination

3. Request Intro Modal
- Simple 4-field form, client-side validation, show upload progress
- Max upload 20MB, accept pdf/docx

4. Toasts / Error handling
- Success: green toast with short instructions
- Error: clear inline error messages under relevant fields

---

## UI → Backend data contract (minimal fields)
Note: These are design-driven requirements to help backend estimate. Provide these endpoints and fields; payloads intentionally minimal and reversible.

1) GET /api/v1/funds
- Query params: q, stage[], sector[], location[], min_aus, max_aus, page_cursor, limit
- Response: list of fund objects with: id, name, logo_url, one_liner, stage[], sectors[], aum_estimate, avg_check, hq_location, highlighted (bool)
- Pagination: cursor

2) GET /api/v1/funds/{id}
- Response: id, name, logo_url, one_liner, full_thesis, stage[], sectors[], aum_estimate, avg_check, hq_location, website, partners[], portfolio_sample[], menus: terms_url
- partners[]: [{id, name, role, photo_url, short_bio, linkedin_url, contact_visible (bool)}]

3) POST /api/v1/intro_requests
- Payload: {fund_id, user_id, role, stage, short_pitch, deck_file_id (optional), preferred_partner_id (optional)}
- Response: {request_id, status}
- Validations: short_pitch required (max 300 chars), deck_file size limit

4) POST /api/v1/uploads
- Multi-part upload flow returning file_id and signed_url or background processing

5) GET /api/v1/user/submissions
- List of submissions for dashboard: {request_id, fund_id, created_at, status, last_note}

6) Webhooks/Notifications (optional)
- On intro_request created -> notify internal ops queue (for assignment) and optionally notify partner if contact_visible

Privacy notes for these endpoints
- Never expose partner personal emails by default. contact_visible flag controls whether frontend shows partner choices; if false, show only "Partner request" without name.
- Uploaded decks may contain PII: require consent checkbox and store encrypted at rest. Back-end must provide retention policy and ability to purge.

---

## Non-functional / scalability considerations (design perspective)
- Discovery: expect paginated results; filters should hit server with debounce (300ms)
- Assets: logos and photos must be CDN-backed and optimized (webp) to keep page load <1s for hero
- Uploads: large files use chunked upload + background virus scan
- Realtime: not required for MVP; polling every 60s for submission status is acceptable

---

## Accessibility & Responsive
- Use semantic HTML headings; color contrast >= 4.5:1 for body text
- Keyboard-operable modals and focus trap
- Mobile: collapse filters into a slide-over; cards become full-width stacked

---

## Design decisions & trade-offs (one-liners)
- Card layout chosen for quick skimming vs list: better visual scan and place for logo and thesis.
- Modal for Request Intro keeps users on context; alternatively a full-screen flow would work for mobile—defer after analytics.
- We intentionally avoid real-time sync for submissions to reduce infra complexity early.

---

## Open questions for Engineering (for Marcus)
1. Do we have an existing file upload service or must backend implement signed URLs+storage?
2. Is there a partner email reveal policy (explicit consent/legal)?
3. Expected scale: how many funds and monthly queries should we design for? (design assumed 10k funds & 100k monthly searches)
4. Retention policy for uploaded decks—default 90 days? Legal to confirm.

---

## Next steps for backend (requested inputs from Marcus)
- Produce backend feasibility doc with: APIs, DB schema sketch (funds, partners, intro_requests, uploads), infra components, scalability bottlenecks, privacy blockers, and effort estimates.
- Use the UI→Backend data contract above as the minimal contract to scope work.

---

## Design effort estimate
- Hi-fidelity mockups (desktop + mobile) + assets export: 3–4 days
- Interaction prototypes (modal flows + upload progress): 1 day
- Handoff + component specs for frontend: 1 day

---

## Files produced
- This design spec: output/design/venture_capital_design_spec.md


Design decisions recorded. If you want, I can produce hi-fi screens next — prioritize which flows.
