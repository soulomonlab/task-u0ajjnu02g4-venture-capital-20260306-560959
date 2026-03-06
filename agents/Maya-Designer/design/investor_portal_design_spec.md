# Investor Portal — Design Spec

Conclusion
- Deliverable: High-fidelity design spec with responsive wireframes, component specs, interaction notes, and implementation assets list.
- Location: output/design/investor_portal/investor_portal_design_spec.md

Overview
This document defines the UX and UI for the Investor / Venture Capital Engagement Portal feature: time-limited, permissioned VC links + read-only KPI/materials dashboard. It is scoped to web (desktop/tablet/mobile responsive). Implementation-ready decisions, component specs, and developer-facing notes are included.

Scope & Goals
- Enable founders to generate permissioned, time-limited VC links and configure access (view-only, download allowed, allowed email domains).
- Provide investors a read-only dashboard of KPIs and materials accessible via the VC link.
- Ensure the experience is clear, secure-feeling, and mobile-friendly.

Primary User Flows (MECE)
1) Create Engagement Link (Founder)
   - Start from Project > Share > Create VC Link
   - Configure: Link name, expiry (duration), permission level, allowed emails/domains, optional note
   - Review & Generate → show generated link + copy/share modal

2) Access Dashboard (Investor via link)
   - Click link → landing page with header branding + prominent trust indicator (expiry, permissions)
   - View KPIs (read-only cards), view/download materials per permission
   - If link expired/invalid → clear error + request access CTA

3) Manage Links (Founder)
   - List of active/past links, quick actions: copy, revoke, extend, view analytics (clicks, views)

User Personas
- Founder (primary): quick setup, control over access, expects clear permissions
- Investor (primary): quick access, trust indicators, uncluttered KPI view
- Admin (secondary): audit and revoke capabilities

Screen Inventory
- Creator screens: Create VC Link (form), Link Created (success modal), Manage Links (list)
- Shared screens: Link Landing (public read-only dashboard), Materials viewer (PDF/images), Permission denied / Expired

Responsive breakpoints
- Desktop: >= 1024px
- Tablet: 768px – 1023px
- Mobile: <= 767px

Design Decisions (high level)
- Card-based KPI layout for scannability and reflow on small screens.
- Single-column mobile stack to avoid horizontal scroll and to emphasize CTAs.
- Prominent trust strip under header on landing page showing expiry and permission badges.
- Minimal colors and strong contrast for KPI numbers (accessibility AA+).

Wireframes (ASCII)
- Desktop: Link Manage / Create

Header [Logo] [Project name]                           [User Avatar]
---------------------------------------------------------------
LeftNav | Main Area (Create VC Link form / Manage links)     | RightRail
        | -------------------------------------------------- |
        | Form: Link name [____]    Expiry [7 days v]        |
        | Permission: [View only]  Allowed emails [____]     |
        | CTA: Create Link (primary)                         |

- Desktop: Landing (Investor)
Header: [Logo]                       [Trust badge: Expires in 3d | View-only]

Main: KPI grid  (3 columns)
[Revenue] [Users] [MRR]
[Churn]   [CAC]   [Burn]
Materials: [PDF thumbnails row]  [Download if allowed]

- Mobile: Landing
Header: [Logo]  [hamburger]
Trust strip: Expires in 2d | View-only
KPI List (single column):
[Revenue card]
[Users card]
Materials (carousel)

Component Library (specs)
- Global tokens
  - Spacing: 4,8,12,16,24,32,40
  - Border radius: 6px
  - Breakpoints: mobile(0-767), tablet(768-1023), desktop(>=1024)
  - Typography: SF / Inter recommended
    - H1 28px/36px weight 600
    - H2 20px/28px weight 600
    - Body 16px/24px weight 400

- Header
  - Height: 64px (desktop), 56px (mobile)
  - Elements: Left logo, center project name, right user menu

- Trust strip (new)
  - Height: 36px, background: subtle-gray (#F5F7FA), left: expiry icon + text, right: permission badge
  - Use for shared landing only

- Link Card (used in Manage Links list)
  - Left: Link name + small note
  - Middle: expiry tag, permissions icons (eye/download/lock)
  - Right: Actions: Copy (icon), Revoke (danger), Extend (secondary)
  - States: active, expired (muted), revoked (red border)

- KPI Card
  - Container with title, primary metric (big), delta % with up/down color
  - Small sparkline placeholder (SVG) to right
  - Desktop: 3-col grid, Tablet: 2-col, Mobile: 1-col
  - Accessibility: metric text at least 18px and contrast ratio >= 4.5:1

- Materials Row
  - Thumbnail grid or carousel depending on breakpoint
  - Click opens viewer modal with download option depending on permission

- Permission Modal
  - Form controls: Radio (View only / View + Download), Expiry (preset buttons + custom datepicker), Allowed emails/domains (chips)
  - Danger action area: Revoke link with confirmation

Interactions & microcopy
- Copy link: show tooltip "Copied" for 2s. Provide a fallback copy link button for mobile.
- Link expiry: show countdown (e.g., "Expires in 3d 4h"). If less than 24h show red accent.
- Permission badge tooltip explains rights: "View-only — files cannot be downloaded."
- Error flows: Expired link → show clear messaging + request access CTA linking to founder email.
- Privacy: show minimal PII. When emails allowed, mask unrelated ones on landing.

Edge cases
- Link generated with restricted domain but opened by other domain: Landing page should show "Access restricted" + request access flow.
- If backend data is delayed: show skeleton loaders for KPIs (avoid blank screens).
- Very long KPI names: truncate with ellipsis and full name in tooltip.

Accessibility
- Keyboard focus states for all interactive elements
- Color contrast: text and KPIs meet AA standards
- Screen reader labels for link actions and permission badges

Assets to deliver
- SVG icon set: copy, revoke, download, permission, expiry clock, external link
- PNG/PNG-2x mockups for Desktop/Tablet/Mobile landing and Create flow
- Figma file: "InvestorPortal_Figma_v1" with pages: 1. Tokens, 2. Components, 3. Desktop/Tablet/Mobile screens

Developer handoff notes
- Provide exact tokens (colors/typography) and export SVG assets. Refer to component specs in this doc.
- Chart components: use provided KPI value + sparkline placeholder; engineering to wire to charting library (e.g., Recharts) using container styles provided.
- Backend flags needed: permissions (view/download), expiry timestamp, allowed_emails/domains, link_id, metrics API endpoint.

Open questions for Product/Backend (for Kevin/Marcus)
1) Do we expose download URLs directly or proxy through backend for permission checks? (Impacts UI for download button states)
2) Expected KPI card metric list — canonical set or configurable per project? (If configurable, we need rules for card ordering)

Design decisions log
- Card layout chosen for reflow and consistent spacing across breakpoints. Trade-off: uses vertical space on mobile but increases scanability.
- Trust strip added to reduce friction and increase investor confidence; reversible: can be hidden if legal constraints apply.

Acceptance criteria (for QA)
- Creator can configure link and see generated link UI per spec
- Investor landing shows trust strip, KPI cards, and materials with permission-respecting actions
- Responsive behavior validated at breakpoints
- Copy/link actions and expiry states behave as described

Files produced in this deliverable
- This spec: output/design/investor_portal/investor_portal_design_spec.md
- Asset list (placeholders to be delivered in Figma or as SVGs in implementation)

Next steps
- Handoff to Frontend for implementation of components and pages. I will be available for design clarifications and will review implementation in staging.

