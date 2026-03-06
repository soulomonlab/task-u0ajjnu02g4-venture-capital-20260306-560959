Dev/demo tokens (for local/dev only)

NOTE: These tokens are for mock/dev use only. Do NOT use in staging/production.

Access token (mock):
- access_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dev_access_token
- expires_in: 900
- scopes: ["view_engagements","view_materials","download_files","upload_files"]

Refresh token (mock cookie):
- Set-Cookie: refresh_token=dev_refresh_token; HttpOnly; SameSite=Lax; Path=/; Max-Age=604800

CSRF token for refresh endpoint (mock):
- x-csrf-token: dev_csrf_token
