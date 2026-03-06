Design Task Brief — Investor/VC Engagement Portal (for Maya)

Situation
Jessica created a Growth & Instrumentation spec (output/specs/venture_capital_engagement_growth.md). The design team must implement UI that emits the required events so experiments can run and metrics can be measured.

Complication
Design must include explicit hooks (data attributes, component IDs) to ensure events are emitted from the correct UI elements. Mobile and desktop variants both required.

Deliverables (P1)
1) Desktop + Mobile wireframes for the Investor/VC Engagement Portal (key flows: onboarding, company profile, outreach, preferences)
2) UI assets and component list (component name, ID, props, variant states) for each interactive element that emits events
3) Interaction → Event mapping embedded in the design files (must reference output/specs/investor_portal_interaction_event_mapping.md)
4) Accessibility notes and keyboard/ARIA considerations for all interactive elements
5) A single design package saved to: output/design/investor_portal/ containing:
   - wireframes_desktop.pdf
   - wireframes_mobile.pdf
   - component_list.md
   - interaction_event_mapping.md (copy of or link to output/specs/investor_portal_interaction_event_mapping.md)

Acceptance criteria
- All event-emitting elements have data-event attributes and component IDs in wireframes
- Interaction→Event mapping matches Growth spec event names and required properties
- Wireframes show experiments variant treatments where applicable (e.g., CTA A/B)
- Assets organized and named as specified above

Constraints & Notes
- Coordinate with Engineering: instrumentation must be implemented 48 hours before client release in staging
- Avoid introducing new event names. Use those in output/specs/venture_capital_engagement_growth.md
- Ensure event payload values match visible labels to minimize translation errors

Timeline
- 5 business days for initial wireframes and component list

Next step
- #ai-design — Maya, please pick up this task. Deliverables to save to output/design/investor_portal/ as listed.

