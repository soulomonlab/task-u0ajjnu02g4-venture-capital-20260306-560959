# Investor Portal — Frontend Integration & Component Spec

Purpose
- Provide frontend implementation details and API contract requests for the Investor / VC Engagement Portal so engineering can start while design assets are produced.

Scope
- Read-only KPI/materials dashboard for invited investors
- Time-limited, permissioned VC share links (link cards)
- Responsive UI (mobile / tablet / desktop)

High-level components (initial)
1. VcLinkCard
   - Purpose: Display a single share link with metadata (title, expiry, permissions, actions: copy, revoke)
   - Props (frontend): id, title, url, expires_at (ISO string), permissions: string[], created_by, status
   - Actions: onCopy(id), onRevoke(id)
   - Accessibility: action buttons must be keyboard focusable, aria-labels for copy/revoke
2. InvestorDashboard
   - Purpose: Read-only display of KPIs and downloadable materials
   - Props: kpis: KPIItem[], materials: MaterialItem[]
   - Behavior: pagination for materials, filters by document type, empty states

Responsive behavior
- Breakpoints (Tailwind default):
  - Mobile (<= 640px): single-column stack, compact cards
  - Tablet (641px–1024px): two-column grid for KPI cards, materials list below
  - Desktop (>1024px): three-column KPI grid, side-by-side materials and link management

Accessibility & UX
- All interactive controls have aria-label and visible focus ring
- Color contrast meets AA
- Copy action shows ephemeral toast (client-side) and accessible live-region announcement
- Loading states: skeleton loaders for KPI cards and materials list
- Error states: friendly error message and retry button

API contract (requests for backend)
- Authentication: frontend expects token-based auth (Authorization: Bearer <token>)

1) GET /api/v1/investor/links
- Purpose: list VC share links for the founder (for management views) or for an investor (read-only view of their links)
- Query params: ?page=number&per_page=number
- Response (200):
  {
    "data": [
      {
        "id": "string",
        "title": "string",
        "url": "string",
        "expires_at": "2026-03-10T15:00:00Z",
        "permissions": ["kpi_read", "materials_download"],
        "created_by": {"id": "string", "name": "string"},
        "status": "active" // or "revoked" / "expired"
      }
    ],
    "meta": {"page": 1, "per_page": 20, "total": 45}
  }

2) POST /api/v1/investor/links/:id/revoke
- Purpose: revoke a share link (founder action)
- Response: 204 No Content or 200 with updated resource

3) GET /api/v1/investor/dashboard
- Purpose: return read-only KPI metrics and materials list for the investor view
- Query params: ?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
- Response (200):
  {
    "kpis": [
      {"id":"monthly_revenue","label":"Monthly Revenue","value":12345.67,"unit":"USD","trend": 0.05}
    ],
    "materials": [
      {"id":"m1","title":"Deck v3","type":"pdf","url":"/s3/..","size_bytes":123456}
    ],
    "meta": {"materials_page":1,"materials_per_page":20,"materials_total":10}
  }

Frontend assumptions & decisions (reversible)
- We'll implement client-side copy using navigator.clipboard; backend won't need to return a one-time token for link copying.
- Pagination: server-side pagination (meta.total + page/per_page)
- Time formatting: frontend displays humanized time remaining; backend returns ISO 8601 UTC timestamps.

Acceptance criteria for frontend to start
- Design wireframes + component tokens delivered to output/design/investor_portal/
- Backend confirms API endpoints and response shapes above (or provides changes)
- Provide sample JSON responses or a mock server endpoint for local dev

Requested inputs from Backend (Marcus)
- Confirm endpoints and response shapes above or provide exact schema
- Provide authentication mechanism for investor links (cookies vs Bearer token)
- Provide file download URLs policy (signed S3 URLs expiration behavior)

