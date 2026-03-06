Security Review: Venture Capital API (Frontend checklist input)

Situation
- The frontend team completed output/docs/venture_capital_api_review_for_frontend.md with endpoints, fields, pagination, response envelope, auth scopes, and mock data. Marcus will convert that into OpenAPI v3 and create mocks.

Complication
- Several security-relevant questions remain unresolved that MUST be specified in the OpenAPI before mocks/specs are produced: total_count availability, cursor token format/contents, rate-limit headers, auth token expiry & refresh behaviour, and error schema. Leaving these underspecified causes design/implementation drift and security gaps (tamperable cursors, replayable tokens, accidental PII exposure, inadequate error handling).

Resolution / Deliverables in this report
- I performed a focused security review and created a concise remediation and confirmation checklist Marcus must include in the OpenAPI and mock server.
- File: output/reports/security_review_venture_capital_api.md (this file)

Key findings (Risk | Issue | Location | Fix)
- HIGH | Ambiguous cursor token specification: an opaque cursor may be accepted by backend without integrity or expiry. Risk: tampering or infinite pagination access. | Pagination section | Use opaque cursor format that is signed and time-limited (HMAC or JWT). Include entropy and server-side validation. Add max TTL (e.g., 15 minutes) and server-side cursor revocation/rotation policy.

- HIGH | Missing explicit auth token lifecycle & revocation plan. Risk: long-lived tokens abused, no revocation for compromised tokens. | Auth section / frontend checklist | Define: access token lifetime (recommend 15m), refresh token lifetime (recommend 7d), rotation of refresh tokens (rotate on use), refresh token storage policy (httpOnly secure cookie or secure storage), revocation endpoint and token blacklist/INTROSPECTION when needed.

- MEDIUM | Rate-limit headers unspecified. Risk: clients unaware of remaining quota or Retry strategy → unexpected 429 bursts. | API responses / headers | Standardize headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset (unix epoch seconds) and include Retry-After for 429 responses. Document per-route limits in OpenAPI description.

- MEDIUM | Error schema not standardized. Risk: inconsistent client behavior, leaking internal error details. | Error handling | Use RFC 7807 Problem Details (application/problem+json) or a consistent envelope: {"errors": [{"code":"...","message":"...","details":{}}], "meta":{}}. Example errors: 400 (validation), 401 (unauth), 403 (forbidden), 404, 409 (conflict), 429 (rate limit), 500 (internal). Provide example bodies for each.

- MEDIUM | Mock data contains real-looking PII. Risk: exposing actual user data in shared mocks. | Mock data section | Ensure mock ventures are synthetic or anonymized. Strip or redact any real email/phone/SSN. Mark mocks as non-production.

- LOW | CORS, security headers & transport not explicit. Risk: insecure integrations. | API global constraints | Require TLS-only (HTTPS) in spec; document CORS policy (whitelist origins), and recommend production security headers (HSTS, X-Content-Type-Options, CSP where applicable).

- LOW | Pagination total_count semantics unclear. Risk: clients depend on total_count for UX; computing exact total_count may be expensive and leak info. | Pagination section | Decide: either provide total_count (accurate but potentially expensive) or provide has_more boolean + approximate_total_count field. Document behavior and performance implications.

Concrete security requirements for the OpenAPI (what Marcus must include)
1) Auth & scopes
   - securitySchemes: include bearerAuth (JWT) and/or OAuth2 flows if using third-party auth. If using JWTs, include token structure in description (claims, signing algorithm e.g., RS256), and required scopes for each endpoint. Use least privilege scope names (e.g., ventures.read, ventures.write).
   - Tokens: Access token expiry = 15 minutes (recommended). Refresh token expiry = 7 days (recommended). If you choose different values, justify in the spec.
   - Refresh token rotation: implement rotation and include a revocation endpoint. Document storage guidance for the frontend (httpOnly cookie recommended for refresh tokens; Authorization header for access token).

2) Cursor pagination
   - Cursor token format: MUST be opaque to clients. Implementation options (pick one and document):
     a) Signed opaque token: base64(HMAC(server_secret, payload)) with payload={last_id,timestamp,limit,nonce}. Validate signature server-side and enforce TTL (e.g., 15 min).
     b) JWT with 'exp' claim and minimal claims (last_id cursor). Sign with server key (RS256). Do not include PII in the token.
   - Document token encoding, TTL, and behavior on expired or malformed cursor (return 400 with error code and human message).
   - total_count: explicit decision required. If provided, mark whether it is exact or approximate and the cost. If not provided, include has_more boolean.

3) Rate-limiting
   - Per-route rate limits documented in OpenAPI. Include response headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset. For 429 responses include Retry-After.

4) Error responses
   - Add Problem Details schema (application/problem+json) or a documented error envelope. Include machine-readable error codes, user message, and trace id (do not expose internal stack traces). Example for 401: {"type":"about:blank","title":"Unauthorized","status":401,"trace_id":"..."}.

5) Mock data hygiene
   - Ensure example responses and mock server use anonymized/synthetic data. Add a comment in OpenAPI examples: "DO NOT USE IN PRODUCTION".

6) Transport & headers
   - Mark OpenAPI servers as https://. Document CORS policy and required security headers. Recommend HSTS and disable TLS 1.0/1.1 in production.

7) Logging & audit
   - Document that sensitive fields (PII) are redacted in logs and that authentication/authorization events are audit-logged with trace IDs.

Acceptance criteria (security sign-off gating criteria)
- No HIGH findings outstanding. Specifically:
  - Cursor tokens are signed & TTL enforced.
  - Token lifecycle and revocation are documented.
- OpenAPI contains required securitySchemes and scopes with example usage.
- Example error responses for 400/401/403/404/429/500 are present and use the agreed schema.
- Mocks use synthetic data only.
- Rate-limit headers and behavior (429 + Retry-After) included.

Recommended defaults (reversible)
- Access token TTL: 15 minutes (revocable). Refresh token TTL: 7 days with rotation.
- Cursor TTL: 15 minutes. Use HMAC-signed opaque cursor.
- Rate-limit headers: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, Retry-After.
- Error format: RFC 7807 Problem Details.

Tests & QA (what to add)
- Security test cases for pagination: replay/modify cursor tokens, expired cursor test.
- Auth tests: expired access token, revoked refresh token, missing scope.
- Rate-limit tests: assert headers present and 429 handling.
- Mock validation: verify no real emails/PII in mock responses.

Next steps for Marcus (explicit asks)
1) In the OpenAPI: state whether total_count is provided and whether it is exact or approximate.
2) Choose cursor token approach (signed opaque vs JWT). Document token format, TTL, and failure response semantics.
3) Include securitySchemes and scope names; set and document token TTLs and refresh behavior (rotation + revocation).
4) Add example responses for success and each error code (use problem+json or agreed envelope).
5) Ensure mock server uses synthetic data and includes rate-limit headers for 200 and 429 responses.

Contact / escalation
- If you prefer a different token TTL or design trade-off, note it in the OpenAPI and ping me. Nothing should be merged while any HIGH item above remains unresolved.

Report prepared by: Isabella (Security Engineer)
Date: [auto-generated]
