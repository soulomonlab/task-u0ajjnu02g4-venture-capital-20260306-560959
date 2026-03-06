# Venture Capital API Contract

Summary
- Endpoint: GET /api/v1/ventures
- Purpose: Provide a paginated list of venture profiles for the frontend components (venture cards, lists, filters).

Request
- HTTP Method: GET
- Path: /api/v1/ventures
- Query parameters:
  - page (integer, optional, default=1)
  - per_page (integer, optional, default=10, max=100)
  - name (string, optional) — case-insensitive substring search on venture name
  - stage (array of strings, optional) — allowed values: seed, series_a, series_b, series_c, growth, ipo, private
  - industries (array of strings, optional) — filter by one or more industries
  - min_raised_usd (number, optional) — filter ventures that have raised >= this amount (in USD)
  - max_raised_usd (number, optional) — filter ventures that have raised <= this amount (in USD)

Filter query syntax (decision)
- Preferred: repeated query params for arrays (form-style, e.g. ?industries=ai&industries=fintech&stage=seed&stage=series_a).
  - Rationale: explicit, consistent with OpenAPI explode=true, avoids CSV parsing edge cases.
- Backwards-compatible: server will also accept comma-separated values (CSV) for convenience.

Response
- Status: 200 OK
- JSON schema: FetchResult
  {
    "items": [ Venture ],
    "total_count": integer,
    "page": integer,
    "per_page": integer
  }

Venture object (fields)
- id (string, uuid) — unique identifier
- name (string)
- logoUrl (string, URL) — nullable if not provided
- stage (string) — one of: seed, series_a, series_b, series_c, growth, ipo, private
- industries (array[string]) — list of industry slugs (e.g., "ai", "fintech")
- short_description (string, max ~300 chars)
- raised_amount_usd (number) — integer amount in USD (whole dollars). Use integer (no cents).
- last_updated (string, ISO-8601) — last time this record was updated (UTC)

Errors
- 400 Bad Request — invalid query param (e.g., non-integer page or per_page, invalid stage value)
- 429 Too Many Requests — rate limit exceeded
- 500 Internal Server Error

Pagination semantics
- page is 1-indexed
- per_page default 10, server enforces max 100
- total_count is the total number of matching ventures (not just in the current page)

Example curl
curl -s "https://api.example.com/api/v1/ventures?page=1&per_page=10&industries=ai&stage=seed"

Acceptance criteria
- Frontend can request GET /api/v1/ventures?page=1&per_page=10 and receive a JSON matching FetchResult with 10 items.
- All Venture properties listed above are present with correct types.
- Server accepts repeated query params for array filters and also CSV.
- raised_amount_usd values are integers representing USD.

Notes / open questions (answered)
- Q: Should raised_amount_usd be in USD integer or thousands? A: Use integer USD (e.g., 1500000 for $1.5M). Frontend can format to human-readable ($1.5M).
- Q: Array filters syntax? A: Use repeated params preferred; server accepts CSV too.

Files
- OpenAPI spec with full schema and example response: output/docs/openapi_ventures.yaml

