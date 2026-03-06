Staging Base URL and Test Credentials

Staging base URL
- https://staging-api.venture.example

Test credentials (service account)
- Header: Authorization: Bearer TEST_SERVICE_TOKEN_v1
- Token scope: create:links, revoke:links, read:audit, read:kpis, teardown
- Token expiry: long-lived for CI usage (rotate monthly)

Teardown endpoint (test-only)
- POST /api/testing/teardown
- Requires Authorization: Bearer TEST_SERVICE_TOKEN_v1
- Returns 202 Accepted on success

Working directory for pytest
- CI runner should run tests from repository root. Command to run the QA suite:
  - python -m pytest output/tests/test_investor_portal_api.py -q

Network/accessibility notes
- Ensure CI runners have outbound HTTPS access to https://staging-api.venture.example
- CORS not required for server-side pytest runner

Contact/Owner
- Marcus (Backend) — provides staging URL, credentials, and ensures endpoints are reachable from CI. #ai-qa will be notified when staging is up.
