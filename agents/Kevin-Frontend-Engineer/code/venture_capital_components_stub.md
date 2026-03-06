# Venture Capital — Frontend Component Stubs & Props/API Contract

Source of truth: output/design/venture_capital_design_spec.md (Maya)

Summary
- Deliverables: initial React component stubs + props/API contract to align frontend ↔ backend
- Location: output/code/frontend/

Components (purpose + key props)

1) VCPage.tsx (page-level container)
- Props:
  - fetchVentures(params: FetchParams) => Promise<FetchResult>
  - initialQuery?: string
  - initialFilters?: Filters
- Responsibility: manage page state (query, filters, pagination), call fetchVentures, pass data down to list/filters/search components.

2) VCSearchBar.tsx
- Props:
  - query: string
  - onChange(query: string): void
  - onSubmit?(): void
- Behavior: debounced input (300ms), accessible label, shows clear button when query present.

3) VCFilters.tsx
- Props:
  - filters: Filters
  - onChange(next: Filters): void
  - availableOptions?: { stages: string[]; industries: string[] }
- Behavior: local controlled inputs, call onChange when user updates filter set.

4) VentureList.tsx
- Props:
  - ventures: Venture[]
  - loading: boolean
  - total: number
  - onLoadMore?: () => void
  - onSelect?: (id: string) => void
- Behavior: renders DealCard per item, empty + loading states, accessible list semantics.

5) DealCard.tsx
- Props:
  - venture: Venture
  - onClick?: (id: string) => void
- Behavior: compact summary of venture (name, stage, industries, short description, raised), clickable.

Shared Types (code: types.ts)
- Venture:
  - id: string
  - name: string
  - logoUrl?: string
  - stage: string
  - industries: string[]
  - short_description?: string
  - raised_amount_usd?: number
  - last_updated?: string (ISO 8601)

- Filters:
  - stages?: string[]
  - industries?: string[]
  - min_raised?: number
  - max_raised?: number

Fetch contracts (VCPage.fetchVentures)
- Request params (FetchParams):
  - query?: string
  - page?: number (1-based)
  - per_page?: number
  - filters?: Filters

- Expected response shape (FetchResult):
  {
    items: Venture[],
    total_count: number,
    page: number,
    per_page: number
  }

Backend expectations / questions for Marcus (please confirm):
- Endpoint & method preferred for list fetch (suggestion: GET /api/v1/ventures)
- Pagination format: do you return `total_count` + `page`/`per_page` or Link headers? (current stubs expect total_count)
- Field types: confirm `id` type (string vs integer), `raised_amount_usd` units (integer cents vs USD float), `last_updated` format (ISO-8601)
- Filtering query syntax: do you accept arrays (e.g., ?stages[]=seed&industries[]=saas) or CSV (`stages=seed,series_a`)?

Frontend decisions made (reversible)
- Pagination: 1-based page + per_page; frontend will support load-more and page param. (Can switch to cursor later.)
- Dates: expect ISO-8601 strings and render using toLocaleDateString on the client.

Acceptance criteria
- Backend provides a working list endpoint matching FetchResult within spec above.
- API returns consistent field names (id, name, stage, industries, short_description, raised_amount_usd, last_updated).

Next steps
- #ai-backend — Marcus: please confirm the above API contract and return a sample JSON response. After you confirm, I will iterate UI to integrate real fetch and finalize props.

Files created (frontend stubs & tests):
- output/code/VCPage.tsx
- output/code/VCSearchBar.tsx
- output/code/VCFilters.tsx
- output/code/VentureList.tsx
- output/code/DealCard.tsx
- output/code/types.ts
- output/code/venture_capital_components_stub.md
- output/tests/VCPage.test.tsx
- output/tests/VCSearchBar.test.tsx
- output/tests/VCFilters.test.tsx
- output/tests/VentureList.test.tsx
- output/tests/DealCard.test.tsx

Notes
- Styling: Tailwind utility classes used in stubs.
- State: VCPage lifts state; child components are controlled via props.

