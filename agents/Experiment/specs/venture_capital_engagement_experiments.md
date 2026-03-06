# Venture Capital Engagement — Experiment Plan

Purpose: Provide prioritized, instrumented growth experiments tied to clear hypotheses, success metrics, stop conditions, and exact interaction→event mappings so Design and Engineering can implement and QA reliably.

Summary
- Scope: Experiments to increase investor/VC engagement and improve signal capture for lead qualification in the Investor/VC Engagement Portal.
- Deliverable: 5 prioritized experiments + instrumentation requirements, sample event JSON, and an instrumentation QA checklist.

Prioritized Experiments

1) Improve Onboarding Completion (High-impact, P0)
- Hypothesis: Simplifying the onboarding steps and surfacing a "Save investment preferences" CTA will increase onboarding completion rate by 15% within 4 weeks.
- Primary metric: Onboarding completion rate (completed_onboarding / onboarding_started)
- Target uplift: +15% relative
- Guardrail metrics: Time-to-complete ≤ +20% baseline; error rate ≤ baseline
- Duration / sample: 4 weeks or 3,000 users (whichever first)
- Stop condition: No improvement after 2 weeks with >1,000 users OR negative impact on guardrails
- Decision outcomes: Rollout if ≥15% uplift with p<0.05; iterate if 5–15%; stop and rollback if negative on guardrails
- Required events (see Instrumentation section)

2) Increase 'Interested' Signal Capture (P1)
- Hypothesis: Replacing a single free-text "notes" field with structured interest options + 1-click "I'm interested" will increase explicit interest signals recorded by 25%.
- Primary metric: Number of explicitly captured 'interest' signals per user
- Target uplift: +25%
- Guardrails: No reduction in submission rate; average time on page ≤ baseline +10%
- Duration / sample: 3 weeks or 2,000 users
- Stop condition: No uplift after full run or increased abandonment
- Decision outcomes: Promote if uplift achieved; A/B test alternatives if partial

3) CTA Wording A/B for Outreach Conversion (P1)
- Hypothesis: CTA variant B ("Request intro to this founder") will convert 10% better than control ("Contact founder").
- Primary metric: CTA click → outreach submission conversion rate
- Target uplift: +10%
- Duration / sample: 2 weeks, minimum 1,000 exposures per variant
- Stop condition: Low sample or non-significant result

4) Re-engagement via Event-Triggered Email (P2)
- Hypothesis: Sending a contextual email when a VC views a company profile but does not express interest within 48 hours increases return visits by 20%.
- Primary metric: 7-day return visit rate after profile view without interest
- Target uplift: +20%
- Guardrails: Unsubscribe rate impact ≤ baseline +0.1%
- Duration: 4 weeks

5) Lead Qualification Scoring Signal Experiment (P2)
- Hypothesis: Adding an explicit 'investment stage' selector increases lead qualification accuracy (measured by downstream follow-ups / meetings) by 10%.
- Primary metric: Conversion to first meeting / qualified lead
- Target uplift: +10%
- Duration: 6 weeks

Instrumentation (Acceptance Criteria)
- Every experiment must emit the events listed below; events must follow the taxonomy: <entity>.<action> (e.g., onboarding.completed, profile.viewed, interest.expressed)
- Events must include these common properties: timestamp (ISO-8601), user_id (if authenticated), anonymous_id (if not), session_id, experiment_id (if in experiment), variant, page_path, referrer
- Event payloads must validate against schema (see sample JSON)
- At least one downstream consumer (analytics, growth, or email) must confirm receipt within 24 hours in staging before production rollout
- QA acceptance: 100% of flows exercised in staging produce events with required properties; schema validation passes

Sample Event JSON
- onboarding.completed
{
  "event": "onboarding.completed",
  "timestamp": "2026-03-01T12:34:56Z",
  "user_id": "u_12345",
  "anonymous_id": null,
  "session_id": "s_98765",
  "experiment_id": "exp_onboard_simplify_v1",
  "variant": "treatment",
  "page_path": "/onboarding/finish",
  "duration_seconds": 45
}

- interest.expressed
{
  "event": "interest.expressed",
  "timestamp": "2026-03-01T12:50:00Z",
  "user_id": "u_12345",
  "session_id": "s_98765",
  "target_user_id": "founder_6789",
  "interest_type": "co_lead",
  "investment_stage": "Series A",
  "experiment_id": "exp_interest_structured_v1"
}

Interaction → Event Mapping (interface elements → event names & payload)
- Onboarding: "Finish" CTA click → onboarding.completed {duration_seconds, percent_steps_completed}
- Preference selector: change event → onboarding.preference_selected {preference_key, preference_value}
- Company profile view: page load → profile.viewed {company_id, referrer}
- "I'm interested" button: click → interest.expressed {target_user_id, interest_type, investment_stage}
- Outreach CTA click: click → outreach.clicked {company_id, cta_variant}
- Outreach form submit: submit → outreach.submitted {company_id, message_length, success:true}

Instrumentation QA checklist
- Events emitted for every major path (happy + error flows)
- Required properties present and populated
- experiment_id and variant consistently set for exposed users
- No PII in free-text properties (mask or hash as required)
- Events arrive in analytics pipeline within 1 hour in staging
- Automated schema validation test exists for each event

Implementation notes & constraints
- Use stable event names across experiments to avoid analytics fragmentation
- Keep event payloads flat (no nested objects) and with explicit typed fields
- Default to emitting user_id when available; else emit anonymous_id
- For experiments tied to UI changes, coordinate release windows so instrumentation rollout precedes client release by at least 48 hours in staging

Next actions (for design + engineering collaboration)
- Design: consume the Interaction→Event mapping to ensure UI elements emit the mapped events and include experiment hooks for variant rendering
- Engineering: implement events to match the sample JSON schema and run the QA checklist in staging
- Growth/Experiment Owner: monitor metrics and apply stop conditions; record decision outcomes

Appendix: Experiment tagging convention
- experiment_id format: exp_<short_name>_v<major>
- variant values: control | treatment | variant_<label>

