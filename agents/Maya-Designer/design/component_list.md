Investor Portal — Component List

Overview
- Purpose: definitive list of UI components, props, IDs, events, and variants required for the Investor/VC Engagement Portal.
- Location: output/design/investor_portal/component_list.md

Components
1) vc-topbar
- Roles: global navigation, search, user menu
- Props: showSearch:Boolean, userAvatar:URL
- Component-id: vc-topbar
- Events: data-event="search_submitted" (payload: {query, timestamp}), data-event="user_menu_opened"

2) vc-search-input
- Props: placeholder, suggestions
- component-id: vc-search-input
- Events: data-event="search_focus", data-event="search_submitted" (onEnter)

3) vc-investor-card
- Props: investorId, name, logoUrl, tags, lastActive, bio
- Component-id pattern: vc-investor-card-<investorId>
- Actions/Events:
  - click: data-event="investor_card_selected" payload:{investorId}
  - follow button: data-event="investor_followed" payload:{investorId}
  - share: data-event="investor_shared" payload:{investorId, method}
- Variants: compact | expanded (controlled by experiment: card_density_test)

4) vc-investor-header
- Props: investorId, name, socials
- component-id: vc-investor-header
- Events: data-event="profile_follow", data-event="profile_shared"

5) vc-composer-modal
- Props: recipients[], subject, body
- component-id: vc-composer-modal
- Events:
  - composer_recipient_added payload:{investorId}
  - composer_body_edited payload:{chars, debounce:1s}
  - outreach_sent payload:{recipients[], subject, templateId (nullable)}

6) vc-cta-button
- Props: variant, colorScheme, disabled
- component-id pattern: vc-cta-<function>-<id>
- Events: data-event="cta_clicked" payload:{ctaName, variant}

7) vc-tabs
- Props: tabs[], activeTab
- Events: data-event="profile_tab_selected" payload:{tabName}

Experiment flags
- Each component supports data-experiment attribute when applicable.
- Example: data-experiment="cta_color_test:B"

Implementation notes
- Use kebab-case for component-id
- All events should include timestamp, userId (if available), and pageContext

Acceptance criteria (for design handoff)
- Every interactive element has component-id and data-event
- Component props listed for dev implementation
- Variant states annotated where experiments apply

