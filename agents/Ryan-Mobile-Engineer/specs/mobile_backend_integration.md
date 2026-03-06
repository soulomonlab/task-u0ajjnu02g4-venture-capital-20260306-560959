Mobile — Backend Integration Checklist

Purpose
- Summarize backend decisions that directly affect mobile implementation, offline/caching behavior, PII handling on device, and acceptance criteria so mobile work can proceed in parallel where safe.

Core dependencies (blocking product/backend decisions)
- PII retention & deletion policy (product): how long PII is retained server-side, whether deletion is immediate or soft-delete + delayed purge, and whether the mobile client must trigger/confirm deletion flows.
- Expected search QPS and latency SLA (product/backend): low/medium/high to size paging, debouncing, and whether client-side throttling is required.
- API contracts for auth, search, user data, and deletion endpoints (backend): schemas, pagination, rate limits, error codes, and webhook/events for asynchronous deletion.

MECE breakdown of mobile requirements
1) Auth & Session
   - JWT-based auth: mobile will store tokens in secure storage (iOS Keychain / Android Keystore).
   - Token refresh endpoint required (refresh token or silent re-auth flow).
   - Acceptance: login/refresh/logout flows work offline->online sync; expired token returns 401.

2) User data & PII
   - Minimal PII on device by default. Fields to store: user_id, display_name, avatar_url, email (optional), last_synced_at.
   - Encryption at rest required for PII (OS secure storage + optional encrypted DB for other fields).
   - Deletion flow: if server-side PII is deleted, backend must emit a deletion confirmation event or make endpoint for mobile to poll; mobile must remove local copies within retention window.
   - Acceptance: when product triggers deletion for a user, mobile removes PII within X hours and stops further syncs.

3) Search
   - Client will call /v1/search with pagination (cursor or offset), debounced input (300–500ms), and incremental load (infinite scroll).
   - If expected QPS=high → require server-side rate limits and backoff handling on client; implement local caching of recent queries.
   - Acceptance: searches return and render <500ms median; pagination loads next page on scroll; stale results handled via cache TTL.

4) Offline & Caching
   - Caching for: user profile, recent search results, and last-known lists. Use small local DB (SQLite via WatermelonDB or MMKV/realm based on size).
   - Sync strategy: conservative: read-from-cache-first, then refresh when online; writes queued and retried with exponential backoff.
   - Acceptance: app usable for read operations for 10 minutes offline; queued writes delivered when connectivity returns.

5) Push / Notifications
   - Backend must provide endpoints to register device tokens and to send targeted deletion or reauth notifications.
   - Acceptance: device token registration + push reception verified on iOS/Android.

6) Observability & Error Handling
   - Mobile requires stable error codes and metrics endpoints (or agreed tags) to map failures (401, 429, 5xx).
   - Acceptance: Sentry/analytics events for auth failures, deletion confirmations, and search latencies.

7) API Fields & Contract Checklist for GH issues (mobile-impact)
   - Auth: POST /v1/auth/login, POST /v1/auth/refresh, POST /v1/auth/logout
   - User: GET /v1/users/{id} (include avatar_url, last_modified, pii_fields list), PATCH /v1/users/{id}
   - Deletion: POST /v1/users/{id}/delete (or DELETE /v1/users/{id}) + webhook/event for deletion confirmation
   - Search: GET /v1/search?q=&cursor=&limit= (specify rate limits, QPS, expected latency)
   - Push: POST /v1/device_tokens (register), DELETE /v1/device_tokens/{id}

Mobile dev estimates (preliminary, depends on backend confirmations)
- Auth & token handling: 2 dev-days
- User profile + PII deletion/sync flows: 2.5 dev-days
- Search integration + caching/pagination: 2 dev-days
- Offline DB & sync queue: 1.5 dev-days
- QA/device testing & bugfixes: 1 dev-day
Total: ~9 dev-days (adjust ±30% based on backend decisions)

Trade-offs & recommended defaults (reversible)
- Default to "store minimal PII and require encrypted storage" to reduce compliance exposure; if product needs richer local profile, expand later.
- Default search QPS=medium and implement client-side debouncing + pagination; this is safest and reversible.

Acceptance criteria for mobile deliverable
- Login, token refresh, and logout flows pass on iOS and Android.
- User profile loads and updates; avatar displays; local PII is encrypted.
- Deletion triggered server-side leads to local PII removal within agreed retention window (verify on QA devices).
- Search returns paginated results, debounced input, and handles offline gracefully.

Blocking items for Product/Backend
- Product (Alex): confirm PII retention & deletion policy and expected search QPS.
- Backend (Marcus): create GH issues for the API tasks listed above and confirm exact API contract (paths, field names, pagination style, rate limits, and deletion events/webhooks).

Notes
- I will start implementing mobile screens and auth flows once the auth contract and PII deletion contract are stable. If Product cannot decide quickly, I will implement conservative defaults listed above and keep code configurable.

