Investor Portal — Interaction Event Mapping

Purpose
- Provide full mapping of UI elements → event names → payload schema → sample JSON → implementation notes.
- Location: output/design/investor_portal/interaction_event_mapping.md

Mapping
1) Search
- Element: vc-search-input
- Event: search_submitted
- Payload schema:
  {
    "event": "search_submitted",
    "userId": "<user_id|null>",
    "pageContext": "dashboard",
    "query": "string",
    "timestamp": "ISO8601"
  }
- Sample:
  {"event":"search_submitted","userId":"u_123","pageContext":"dashboard","query":"fintech","timestamp":"2026-02-10T10:00:00Z"}
- Notes: debounce client-side 300ms, send on Enter or Search button click

2) Investor Card Click
- Element: vc-investor-card-<id>
- Event: investor_card_selected
- Payload schema: {event, userId, pageContext, investorId, positionInList, timestamp}
- Sample: {"event":"investor_card_selected","userId":"u_123","pageContext":"dashboard","investorId":"i_456","positionInList":3,"timestamp":"..."}
- Notes: positionInList needed for funnel analysis

3) Follow Click
- Element: vc-investor-card-<id> > follow button
- Event: investor_followed
- Payload schema: {event, userId, investorId, followState (true/false), timestamp}

4) Composer Send
- Element: vc-composer-modal > send
- Event: outreach_sent
- Payload schema: {event,userId,recipients:[investorId],subject,templateId|null,variant (if experimental),timestamp}
- Notes: block send until recipients validated; batch send emits single event with recipients array

5) Card Swipe (mobile)
- Element: vc-investor-card-<id>
- Event: card_swiped
- Payload: {direction: left|right, investorId, userId, timestamp}
- Notes: only track intentional swipes exceeding 40px

6) CTA Clicks (experiment tracking)
- Element: vc-cta-<name>
- Event: cta_clicked
- Payload: {event, userId, ctaName, variant, pageContext, timestamp}
- Notes: include data-experiment attribute on CTA if variant-specific

General implementation notes
- All events must include: event, userId (if logged in), pageContext, timestamp
- Use consistent naming: snake_case_event_names
- Use data-event and component-id attributes in DOM for easier instrumentation
- For SPAs: emit routeChange events when navigating between major screens

Acceptance criteria for instrumentation
- Each interactive DOM element has data-event and component-id attributes
- Events match schemas above; backend accepts the payload fields
- Event emission timing documented (e.g., onClick, onSubmit, debounce rules)

