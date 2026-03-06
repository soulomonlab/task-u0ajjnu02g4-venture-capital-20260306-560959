Investor Portal — Component Specs

Files: output/design/investor_portal/component_spec.md

1) Global tokens
- Colors
  - Primary: #1F6FEB
  - Accent (success): #16A34A
  - Danger: #DC2626
  - Gray-100: #F5F7FA (trust strip bg)
  - Text Primary: #0F172A
  - Text Secondary: #334155
- Spacing scale: 4,8,12,16,24,32,40
- Border radius: 6px
- Elevation: subtle card shadow: 0 1px 3px rgba(2,6,23,0.08)

2) Header
- Height desktop: 64px, mobile: 56px
- Elements: left aligned logo 40px, center project name H2, right user avatar 36px
- Responsive behavior: project name collapses to short form on mobile

3) Trust Strip
- Height: 36px; full width below header; background: Gray-100
- Left: clock icon + text (Expires in 2d 3h)
- Right: permission badge (View-only / Download allowed)
- Behavior: if link invalid/expired, strip turns Danger background with white text and shows "Expired"

4) KPI Card
- Width: responsive; Padding: 16px
- Title: H3 14px, Metric: 28px bold, Delta: 12px
- Sparkline area: 56x24 px right aligned
- Hover: elevate shadow + subtle border

5) Link Card (Manage Links)
- Padding: 12px; layout: 3 columns (info | tags | actions)
- Actions: icon buttons with 44px touch target
- States: expired: opacity 0.6 + expired tag

6) Material Thumbnail
- Size: desktop 120x80, mobile 160x90 (carousel)
- Overlay: if download disallowed, show lock icon

7) Modals
- Centered, max-width 720px, close with ESC and overlay click
- Confirm revoke modal: red-danger CTA

8) Forms
- Inputs: 44px height, 12px padding
- Chips for allowed emails. Suggestion autocomplete for project collaborators

Accessibility notes
- All icons have aria-label
- Keyboard focus visible with 2px outline in Accent color

Developer tokens to export
- All colors as CSS variables: --vc-primary, --vc-text-primary, etc.
- Spacing variables and typography classes

Integration notes
- KPI card to accept props: title, metric, delta, sparklineData, ariaLabel
- Link card: linkId, name, expiryDate, permissions, onCopy, onRevoke, onExtend

