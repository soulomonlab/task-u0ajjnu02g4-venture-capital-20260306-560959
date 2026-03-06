# Investor Portal — Component List

Purpose
- Define UI components to be implemented by frontend with design tokens and interaction states.

Global tokens (examples)
- Primary color: #2B6CB0 (blue-600)
- Accent / Success: #38A169 (green-500)
- Neutral text: #1A202C
- Muted text: #4A5568
- Border radius: 8px
- Spacing scale: 4,8,12,16,24,32
- Typography: H1 28/32, H2 22/28, Body 16/24, Small 12/16

Core components
1) Header
   - Elements: Logo, Global Search, Notifications, User Menu
   - States: collapsed, sticky

2) Left Navigation
   - Items: Feed, My Connections, Requests, Meetings, Settings
   - Behavior: collapsible on mobile

3) Investor Card
   - Elements: Photo (48px), Name, Firm, Tags, Follow button, Save
   - Variants: compact (mobile), detailed (desktop)
   - States: default, hover, selected

4) Profile Header
   - Elements: large photo (120px), name, firm, location, CTA row
   - CTA: Follow (secondary), Request Intro (primary), Schedule (primary)

5) Tabs / Accordion
   - Desktop: horizontal tabs
   - Mobile: accordion

6) Pitch Deck Viewer (Modal)
   - Carousel controls, slide thumbnails, download button, request follow-up

7) Request Intro Modal
   - Fields: intro message (textarea), reason (select), referer (optional file)
   - Limit: 300 characters
   - Actions: Send, Cancel

8) Scheduler Component
   - Elements: date picker, time slots, timezone selector, confirm button
   - Integrations: calendar invite generation

9) Activity Feed Item
   - Elements: actor, action verb, timestamp, CTA (view details)

10) Notification Toast
    - Types: success, error, info

Event emission points (high level)
- search.submitted
- investor.viewed
- investor.followed
- intro.requested
- meeting.scheduled
- pitch.deck_opened
- pitch.downloaded

Implementation notes
- Buttons use role=button and ARIA labels for accessibility.
- Keyboard navigation support for modals and carousels.

Next: map components to instrumentation events in interaction_event_mapping.md
