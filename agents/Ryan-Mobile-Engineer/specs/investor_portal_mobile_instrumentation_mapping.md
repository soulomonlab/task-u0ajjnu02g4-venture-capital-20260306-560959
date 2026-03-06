# Mobile Instrumentation Mapping — Investor Portal

Purpose: Mobile mapping of UI interactions to analytics events, aligned with design deliverables:
- output/design/investor_portal_interaction_event_mapping.md
- output/specs/venture_capital_engagement_growth.md

Files produced in this change:
- output/code/hooks/useAnalytics.ts
- output/code/components/InvestorCard.tsx
- output/code/components/ProfileHeader.tsx
- output/code/components/PitchDeckModal.tsx
- output/code/components/RequestIntroModal.tsx
- output/code/components/Scheduler.tsx

Key decisions (Mobile Engineer)
- Use a single useAnalytics hook to ensure consistent payloads (user_id, session_id, experiment metadata).
- Support optional serverAck for critical events (hook returns a promise that resolves when server confirms receipt).
- Offline-safe: events are queued in AsyncStorage if device is offline; queue is flushed when network is available.
- Minimal dependency surface: plain fetch for network; AsyncStorage for persistence; no heavy analytics SDK tied in here to keep testing simple and reversible.

Event mapping (short):
1) investor_card_tap
   - Trigger: tap on InvestorCard leading to Investor Profile screen
   - Payload: { user_id, session_id, investor_id, experiment: {name, variant} }
   - serverAck: false
   - Files: InvestorCard.tsx

2) request_intro_submitted
   - Trigger: user submits RequestIntroModal
   - Payload: { user_id, session_id, target_investor_id, request_id }
   - serverAck: true (must confirm success from backend before marking conversion)
   - Files: RequestIntroModal.tsx, useAnalytics.ts

3) pitch_deck_viewed
   - Trigger: PitchDeckModal opened
   - Payload: { user_id, session_id, pitch_deck_id }
   - serverAck: false
   - Files: PitchDeckModal.tsx

4) profile_header_follow_tap
   - Trigger: follow button tapped in ProfileHeader
   - Payload: { user_id, session_id, target_user_id }
   - serverAck: true (server must confirm follow created)
   - Files: ProfileHeader.tsx, useAnalytics.ts

5) scheduler_action
   - Trigger: scheduling flow completed (Scheduler component)
   - Payload: { user_id, session_id, meeting_id, scheduled_time }
   - serverAck: true
   - Files: Scheduler.tsx

Implementation notes / instructions for QA:
- Verify that events include user_id and session_id in payloads.
- For serverAck events, validate that the hook waits for backend ack before resolving and that failures retry or surface an error.
- Test offline behavior: queue events while offline and verify flush after reconnect.
- Confirm experiment metadata is attached when provided by remote config.

Next steps (Mobile Engineer):
- Handing off to QA (Dana) to validate instrumentation and offline behavior on device farm.
- #ai-qa should run the test checklist in output/tests/mobile_instrumentation_test_plan.md (created separately if requested).
