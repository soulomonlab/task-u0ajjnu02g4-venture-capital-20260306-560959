Investor Portal — Wireframes (ASCII)

Files: output/design/investor_portal/wireframes_ascii.md

DESKTOP — Manage Links / Create

[Header: Logo | Project Name                           | User Avatar]
-----------------------------------------------------------------------
| LeftNav | Main Area: Create VC Link Form                | RightRail |
|---------|-----------------------------------------------|-----------|
| Nav     | Title: Create VC Link                          | Tips      |
| Items   | ----------------------------------------------------------      |
|         | Form:                                                      |
|         | Label: Link name [____________________]                   |
|         | Label: Expiry [7 days v]  [custom datepicker]             |
|         | Permission: ( ) View-only   ( ) View + Download           |
|         | Allowed emails/domains: [someone@vc.com, + add]           |
|         | Optional note: [___________]                             |
|         | [ Create Link (Primary) ]  [ Cancel ]                     |
|         | --------------------------------------------------------- |
|         | After create: Modal -> Generated link with Copy button    |

DESKTOP — Landing (Investor via link)

[Header: Logo]  [Trust strip: Expires in 3d | View-only]
----------------------------------------------------------
Main area: KPI grid (3 columns)
[ Revenue ] [ Users    ] [ MRR  ]
[ Churn   ] [ CAC      ] [ Burn ]

Materials row:
[PDF-thumb1] [pdf-thumb2] [image-thumb3]  [View all]

Footer: minimal

MOBILE — Landing

[Header: Logo | hamburger]
[Trust strip: Expires in 2d | View-only]
KPI stack:
[ Revenue card ]
[ Users card   ]
[ MRR card     ]
Materials: carousel (swipe)

MOBILE — Create flow (progressive)
Step 1: Name + Expiry
Step 2: Permissions + allowed emails
Step 3: Review + Create

Notes:
- Focus states, spacing tokens, and responsive reflow are defined in the spec.
- Provide skeleton loaders for KPI cards while data loads.

