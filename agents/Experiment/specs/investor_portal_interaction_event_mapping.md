Investor Portal — Interaction → Event Mapping

Purpose: Provide design and engineering a single-source mapping from UI interactions (wireframe elements) to the exact event name and payload fields required by Growth/Instrumentation.

File structure: Lists UI element, event name, trigger, required properties, sample payload, and notes for design implementation.

1) Onboarding
- UI Element: "Finish" CTA (last step)
  - Event: onboarding.completed
  - Trigger: click / onboarding finished
  - Required properties: timestamp, user_id/anonymous_id, session_id, experiment_id, variant, page_path, duration_seconds, percent_steps_completed
  - Sample payload:
    {"event":"onboarding.completed","timestamp":"2026-03-01T12:34:56Z","user_id":"u_12345","session_id":"s_98765","experiment_id":"exp_onboard_simplify_v1","variant":"treatment","page_path":"/onboarding/finish","duration_seconds":45,"percent_steps_completed":100}
  - Notes: Add data attribute data-event="onboarding.completed" to CTA; wireframe should show CTA ID for QA reference.

- UI Element: Preference selector (multi-select)
  - Event: onboarding.preference_selected
  - Trigger: change / focus-out
  - Required properties: preference_key, preference_value, user_id/session_id, timestamp, page_path
  - Sample payload:
    {"event":"onboarding.preference_selected","preference_key":"investment_stage","preference_value":"Series A","user_id":"u_12345","session_id":"s_98765","timestamp":"2026-03-01T12:31:00Z","page_path":"/onboarding/preferences"}
  - Notes: Preference selector must include visible labels matching event values to avoid mismatch.

2) Company Profile
- UI Element: Profile page load
  - Event: profile.viewed
  - Trigger: page load / SPA route change
  - Required properties: company_id, user_id/anonymous_id, session_id, page_path, referrer, timestamp
  - Sample payload:
    {"event":"profile.viewed","company_id":"c_456","user_id":"u_12345","session_id":"s_98765","page_path":"/company/c_456","referrer":"/search","timestamp":"2026-03-01T12:40:00Z"}
  - Notes: Include data attribute data-event="profile.viewed" on main profile container.

- UI Element: "I'm interested" button
  - Event: interest.expressed
  - Trigger: click
  - Required properties: target_user_id/company_id, interest_type, investment_stage, user_id/session_id, experiment_id (if in experiment), variant, timestamp
  - Sample payload:
    {"event":"interest.expressed","target_user_id":"founder_6789","company_id":"c_456","interest_type":"co_lead","investment_stage":"Series A","user_id":"u_12345","session_id":"s_98765","experiment_id":"exp_interest_structured_v1","variant":"treatment","timestamp":"2026-03-01T12:50:00Z"}
  - Notes: Design should surface structured options for interest_type (e.g., co_lead, passive, syndicate) and investment_stage dropdown. The button must be accessible for keyboard users.

3) Outreach
- UI Element: Outreach CTA (on profile)
  - Event: outreach.clicked
  - Trigger: click
  - Required properties: company_id, cta_variant, user_id/session_id, timestamp, page_path
  - Sample payload:
    {"event":"outreach.clicked","company_id":"c_456","cta_variant":"variant_b","user_id":"u_12345","session_id":"s_98765","timestamp":"2026-03-01T13:00:00Z","page_path":"/company/c_456"}
  - Notes: In A/B tests, CTA must include variant label as data attribute data-variant="variant_b".

- UI Element: Outreach form submit
  - Event: outreach.submitted
  - Trigger: form submit success
  - Required properties: company_id, message_length, success (bool), user_id/session_id, timestamp
  - Sample payload:
    {"event":"outreach.submitted","company_id":"c_456","message_length":120,"success":true,"user_id":"u_12345","session_id":"s_98765","timestamp":"2026-03-01T13:02:00Z"}
  - Notes: If submission fails, emit outreach.submitted with success:false and error_code.

4) Re-engagement
- UI Element: Profile viewed without interest (backend trigger)
  - Event: profile.viewed_no_interest
  - Trigger: backend job detecting view without interest after 48h
  - Required properties: company_id, user_id/anonymous_id, session_id, timestamp, view_timestamp
  - Sample payload:
    {"event":"profile.viewed_no_interest","company_id":"c_456","user_id":"u_12345","session_id":"s_98765","timestamp":"2026-03-03T13:00:00Z","view_timestamp":"2026-03-01T12:40:00Z"}
  - Notes: Backend should tag users for re-engagement emails; design should supply email templates for personalization tokens.

5) User Menu
- UI Element: Save preferences in profile
  - Event: preferences.saved
  - Trigger: click / save success
  - Required properties: user_id, preferences_changed (list), timestamp, page_path
  - Sample payload:
    {"event":"preferences.saved","user_id":"u_12345","preferences_changed":["investment_stage:Series A","sector:Fintech"],"timestamp":"2026-03-01T13:10:00Z","page_path":"/profile/settings"}
  - Notes: Preference changes should be granular; each change can optionally emit preference.changed per item for granular analytics.

General implementation notes for design
- Add clear data-event and data-variant attributes to interactive elements in wireframes so front-end devs can hook events.
- Provide component IDs for key CTAs and forms in the component list.
- Ensure accessible labels and keyboard interactions for all event-emitting elements.

Acceptance criteria for design
- Wireframes include data-event attributes and explicit component IDs
- Mobile and desktop variants show how components render and where events are emitted
- Interaction flow diagrams map to experiment IDs for variant exposure

Next steps for design
- Produce desktop + mobile wireframes and component list, and place them in output/design/investor_portal/
- Include a combined interaction→event mapping in the design deliverable (this file should be referenced)

