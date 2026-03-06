# Investor Portal — Wireframes & User Flow

Purpose
- Deliver desktop and mobile wireframes, primary user flows, and interaction notes for the Investor/VC Engagement Portal.

Users & Use-cases
- Investor/VC: discover startups, review pitch materials, schedule meetings, accept/decline intro requests.
- Founder: submit pitch, track engagement metrics, respond to investor requests.

Primary flows
1) Discovery → View investor profile → Bookmark / Follow → Request intro / Send message
2) Pitch review → Open pitch deck → Download cap table / Request follow-up meeting
3) Scheduling → Select timeslot → Confirm meeting → Receive calendar invite

Desktop Wireframes (ASCII)

1) Dashboard (desktop)
-------------------------------------------------------------
| Header: Logo | Search [________] | Notifications (3) |User|
-------------------------------------------------------------
| Left nav: Feed | Filters (AUM, Stage, Sector)                |
|               | -------------------------------------------- |
|               | 1. Featured Investor Card  [Follow] [Save]    |
|               | 2. Investor Card                              |
|               | 3. Investor Card                              |
|               | -------------------------------------------- |
| Main content: Recent activity / recommended investors       |
-------------------------------------------------------------
| Right rail: Quick actions: "Request Intro" CTA, Meetings    |
-------------------------------------------------------------

2) Investor Profile (desktop)
-------------------------------------------------------------
| Header                                                      |
-------------------------------------------------------------
| Profile Header: Photo | Name | Firm | Location | Follow Btn   |
| Tags: Sectors / Checkboxes                                  |
-------------------------------------------------------------
| Tabs: Overview | Portfolio | Deals | Team | Events            |
-------------------------------------------------------------
| Overview: short bio, key metrics (Fund size, Avg check)     |
| Portfolio grid (logos)                                      |
| CTA strip: [Request Intro] [Schedule Meeting] [Download Cap]|
-------------------------------------------------------------

3) Pitch Deck Modal
-------------------------------------------------------------
| Modal: Carousel of slides | Download | Open in new window   |
| Footer: "Request follow-up" with quick-form               |
-------------------------------------------------------------

Mobile Wireframes (ASCII)

1) Dashboard (mobile)
-----------------------------
| Top: Logo | Search icon | User |
-----------------------------
| Filters: horizontal chips                   |
| Investor list: Card (compact)               |
| Card: Photo | Name | Firm | Follow icon     |
-----------------------------

2) Investor Profile (mobile)
-----------------------------
| Photo | Name | Firm                          |
| Follow | Request Intro (Primary CTA)        |
| Tabs as accordion: Overview / Portfolio / Deals |
| CTA: Schedule meeting (sticky at bottom)    |
-----------------------------

Notes & Interaction rules
- CTAs follow visual hierarchy: Primary CTA = filled color, Secondary = outline.
- Critical interactions (Request Intro, Schedule Meeting, Download) must emit events per instrumentation spec: output/specs/venture_capital_engagement_growth.md
- Keep inline forms minimal: avoid >3 fields in modal; use follow-up email capture when required.

Design decisions
- Card-based layout chosen to support scanability and responsive reflow.
- Sticky primary CTA on profile increases conversion for scheduling and intros.
- Modal for pitch deck prevents context switch and keeps analytics attribution cleaner.

Files created: this document + related component and mapping files in same folder.
