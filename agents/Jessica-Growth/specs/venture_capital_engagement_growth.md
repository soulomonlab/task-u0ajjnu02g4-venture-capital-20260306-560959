Title: Venture Capital Engagement Portal — Growth & Instrumentation Spec

Owner: Jessica (Growth & Growth Engineer)
Related spec: output/specs/venture_capital_engagement.md
Link: GitHub Issue #123

Purpose
- Provide clear KPIs, event taxonomy, funnel definitions, and experiment ideas to guide design and engineering for the VC Engagement Portal.
- Specify the tracking and backend requirements needed to measure product success and run growth experiments.

Core ask (the real ask)
- Measure and improve investor engagement with time-limited, permissioned VC links and the read-only KPI/materials dashboard.

North Star and Primary KPIs (why these matter)
- North Star: Engaged Investor Sessions (EIS) — unique investor sessions that view the dashboard or download materials after receiving a VC link.
- Primary metrics:
  - Link Delivered → Link Click Rate (clicks / links sent)
  - Dashboard View Rate (dashboard views / link clicks)
  - Materials Download Rate (downloads / dashboard views)
  - Meeting Conversion Rate (meetings scheduled / dashboard views)
  - 7-day Retention of Investor (investor returns within 7 days after first view)
- Revenue/Business guardrail: Founder satisfaction NPS for fundraising interactions (qualitative).

Funnel (MECE) — events and where to measure
1. Link Creation (founder action)
   - Event: vc_link_created
   - Properties: link_id, founder_id, investor_contact_email (hashed), permission_level (view/download), expires_at (timestamp), notes
2. Link Delivery (sent via email/invite)
   - Event: vc_link_sent
   - Properties: link_id, delivery_channel, recipient_hashed_email, sent_at
3. Link Interaction
   - Event: vc_link_clicked (first open + subsequent opens tracked separately)
   - Properties: link_id, investor_id (if authenticated), recipient_hashed_email, ip_country, user_agent
4. Dashboard View
   - Event: dashboard_viewed
   - Properties: link_id, investor_id, session_id, view_duration_seconds, page (KPIs/materials/etc.)
5. Material Actions
   - Event: material_downloaded
   - Properties: material_id, link_id, file_size, download_method
6. Engagement Conversions
   - Event: meeting_requested (via CTA)
   - Properties: link_id, investor_id, requested_at
7. Access & Security Audit
   - Event: link_expired, link_revoked, permission_changed
   - Properties: admin_id, link_id, previous_permission, new_permission, timestamp

Event Taxonomy (naming & consistency)
- Use snake_case event names
- Include required common properties on every event: timestamp_iso, environment (prod/staging), sdk_source (web/backend/email), platform, app_version, session_id, correlation_id
- For privacy: never send raw PII. Always hash emails (SHA256) or use hashed identifiers. Keep raw PII only in secure backend logs with access controls.

Instrumentation requirements (what engineering must provide)
- Endpoint: POST /api/tracking/events (or integrate with Segment server-side). Must accept the event name and payload.
  - Validation: enforce required common properties & schema per event type.
  - Idempotency: accept event_id to dedupe duplicate sends.
- Link access flow: when a link is clicked, backend should:
  1) validate token & permission
  2) log vc_link_clicked, dashboard_viewed
  3) create a session_id and return a response used by frontend to attach to subsequent events
- Analytics data store: events should be forwarded to Segment/Amplitude/PostHog (company standard) and stored raw for audits (S3/warehouse)
- Retention & compliance: event payloads containing hashed PII stored for 1 year; raw audit logs (for security team) retained as policy dictates.

Sample event JSON (for engineering)
- vc_link_clicked
{
  "event": "vc_link_clicked",
  "timestamp_iso": "2026-03-06T12:34:56Z",
  "environment": "prod",
  "sdk_source": "link-server",
  "link_id": "abc123",
  "recipient_hashed_email": "sha256:...",
  "session_id": "sess_xyz",
  "ip_country": "US",
  "user_agent": "..."
}

Experiment ideas (prioritized)
1. Onboarding / Link CTA (P0)
   - Hypothesis: A redesigned link invitation with a one-line KPI snapshot will increase Link Click Rate by +10%.
   - Primary metric: link_click_rate. Secondary: dashboard_view_rate.
   - Sample size guidance: baseline click rate assumed 20%; to detect 10% relative uplift (2 percentage points) with 80% power, roughly N≈15k links (back-of-envelope); refine with analytics team.
2. Time-limited vs Persistent Links (P1)
   - Hypothesis: Time-limited links create urgency and increase dashboard views but may reduce long-term retention.
   - Metric: dashboard_view_rate, 7-day return rate.
3. Permission Defaults (P1)
   - Hypothesis: Default to ‘view-only’ vs ‘view+download’ will reduce materials downloads but improve security — choose based on founder preference.
4. Dashboard Preview vs Full View (P2)
   - Hypothesis: Show KPI preview in email increases click rate; full dashboard requires click-through.

Acceptance criteria for instrumentation
- All funnel events listed above are emitted for 95% of flows in production.
- Events include session_id and link_id so sessions can be correlated with link and founder.
- Data arrives in analytics backend (Amplitude/PostHog) within 5 minutes for 99% of events.
- PII-handling policy implemented: no raw emails in client-side events.

Next steps (for design & engineering)
- Design: wireframes should include explicit UI locations for event triggers (e.g., CTA buttons, download links). Add microcopy for time-limited link expiration messages.
- Engineering: implement tracking endpoint + ensure server-side logging and forwarding to analytics.

Files created
- This file: output/specs/venture_capital_engagement_growth.md

Questions / open decisions
- Baseline metrics needed from analytics/data team (current link click baseline). Request Samantha for last 90-day data.
- Decide default permission level (ask product/PO Alex).

Contact
- Jessica (Growth). For exec summary and conversion uplift estimates.
