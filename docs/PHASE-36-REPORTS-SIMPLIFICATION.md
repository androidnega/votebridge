# Phase 36 — Reports Workspace Simplification

**Type:** Reports UX consolidation  
**Date:** June 2026  
**Baseline:** Phase 35 governance workflow (`e506cf9`)

---

## A. Completion Report

Phase 36 replaces the multi-tab Reports module with a single institutional reporting workspace. All former report sub-pages are consolidated into one continuous page with unified filters, shared charts, and inline export.

### Delivered

| Area | Status |
|------|--------|
| Single-page `ReportsWorkspaceView` | ✅ |
| Removed horizontal report tabs (`Overview`, `Participation`, `Turnout`, `Historical`, `Export`) | ✅ |
| Removed explore sub-navigation (`By Students`, `Departments`, `Faculties`, `Programmes`, `Security`, `Fraud`, `Communications`, `USSD`) | ✅ |
| Unified filter bar (election, academic year, faculty, department, programme) | ✅ |
| KPI cards (completed elections, average turnout, registered voters, total votes cast) | ✅ |
| Three charts (turnout trend line, faculty participation bar, election distribution donut) | ✅ |
| Filtered election report table | ✅ |
| Export buttons above table (PDF, Excel, CSV) | ✅ |
| Super Admin governance summary widgets | ✅ |
| Legacy route redirects to `/dashboard/reports` | ✅ |
| Frontend production build | ✅ |

### Verification

| Command | Result |
|---------|--------|
| `python manage.py check` | ✅ Pass |
| `python manage.py test` | ✅ Pass (78 tests) |
| `npm run build` | ✅ Pass |

---

## B. Architecture Compliance

**No backend services, repositories, or reporting calculations were modified.**

| Layer | Phase 36 changes |
|-------|------------------|
| Views | New `ReportsWorkspaceView.vue` |
| Composables | New `useReportsWorkspace.js` (UI composition + client-side filters) |
| Store | `fetchReport(type, format, params)` accepts optional filter params |
| Router | All legacy report routes redirect to `reports` |
| Config | `reportsNav` / `reportsAdvancedNav` emptied |

Data continues to flow:

**Views → Composables / Store → existing `analyticsApi` → backend Services**

Business logic remains in backend analytics services; the composable only filters and aggregates API responses in the browser.

---

## C. Database Changes

None.

---

## D. APIs

No new endpoints. Existing analytics APIs reused:

| Purpose | Endpoint |
|---------|----------|
| KPI overview | `GET /analytics/overview/` |
| Election comparison table | `GET /analytics/elections/` |
| Participation / faculty / programme breakdown | `GET /analytics/participation/` |
| Faculty rows | `GET /analytics/faculties/` |
| Turnout trend | `GET /analytics/historical/?period=daily` |
| Academic year metadata | `GET /elections/` (list, for `start_date` only) |
| Export | `GET /analytics/reports/institution/?format={pdf\|excel\|csv}` |

Optional export param: `election_uuid` when an election filter is active.

---

## E. Vue Components

### New layout (`ReportsWorkspaceView`)

1. **Header** — “Election Reports” with institutional subtitle and live connection indicator.
2. **KPI cards** — Completed elections, average turnout, registered voters, total votes cast (recomputed when filters change).
3. **Filter bar** — Five `<select>` controls in a responsive grid; reset button clears all.
4. **Charts**
   - Turnout trend — `LineChart` from historical daily vote trends.
   - Faculty participation — horizontal `BarChart` from faculties / filtered programmes.
   - Election distribution — `PieChart` (donut) from filtered election rows.
5. **Report table** — `VTable` with status badges; rows from `elections.comparison` filtered client-side.
6. **Export** — PDF, Excel, CSV buttons above the table (institution report type).

### Super Admin

Additional compact summary cards surface governance metrics already present in overview data: security alerts, fraud cases, SMS delivery %, USSD requests today. Same page — no duplicate routes.

### Election Administrator

Same workspace; governance summary row is hidden. Operational KPIs, filters, charts, and table remain available.

### Removed navigation

- `moduleNav` tabs no longer render on Reports (empty `reportsNav`).
- All `/dashboard/reports/*` sub-routes and legacy `/dashboard/analytics/*` report routes redirect to `/dashboard/reports`.

Legacy view files under `views/analytics/` are retained for reference but are no longer routed.

---

## F. Security Impact

None. No new data exposure; existing `CanAccessAnalytics` permissions unchanged. Open-election integrity rules remain enforced server-side.

---

## G. Performance Impact

- Initial load fetches overview, elections, participation, faculties, historical, and elections list in parallel.
- Filters are client-side — no additional API round-trips on filter change.
- Charts use existing lazy-loaded ECharts components.

---

## H. Responsive Design Notes

- KPI grid: 1 → 2 → 4 columns (`xs` / `lg`).
- Filter toolbar: 1 column on mobile, 2 on `sm`, 5 on `lg`.
- Charts: turnout + donut stack on mobile; side-by-side on `xl`.
- Export buttons wrap on narrow screens.
- Table uses responsive card layout via `VTable` on mobile.

---

## I. Testing Strategy

| Area | Approach |
|------|----------|
| Route redirects | Manual / router tests — legacy URLs land on `reports` |
| Filter behaviour | Change each filter; verify KPI, chart, and table updates |
| Export | CSV download; PDF/Excel structured payload download |
| Roles | Super Admin sees governance row; Admin does not |
| Build | `npm run build` — no compile errors |
| Backend regression | `python manage.py check` and `python manage.py test` |

---

## J. Deployment Notes

- No migrations or environment changes.
- Deploy frontend bundle only.
- Bookmarks to old report URLs (`/dashboard/reports/participation`, `/dashboard/reports/explore/fraud`, etc.) redirect automatically.

---

## Filter Strategy

| Filter | Source | Effect |
|--------|--------|--------|
| Election | `elections.comparison` | Filters table rows; scopes export `election_uuid` |
| Academic year | Derived from `elections` list `start_date` | Filters table rows and turnout trend points |
| Faculty | `participation.programmes` | Filters programme rows; recomputes faculty chart |
| Department | Programme labels | Filters programme rows |
| Programme | Programme codes | Filters programme rows and derived faculty aggregation |

When no rows match, KPIs fall back to overview totals; empty states display for charts.

---

## Chart Mapping

| Chart | Former page | Data source |
|-------|-------------|-------------|
| Turnout trend (line) | Historical / Turnout | `GET /analytics/historical/?period=daily` → `vote_trends` |
| Faculty participation (horizontal bar) | By Faculties / Participation | `GET /analytics/faculties/` or filtered programmes |
| Election distribution (donut) | Departments / Elections | Filtered `elections.comparison` rows |

---

## Export Workflow

1. User applies optional filters (election filter passed to API).
2. User clicks **Export PDF**, **Export Excel**, or **Export CSV** above the table.
3. Frontend calls `GET /analytics/reports/institution/?format={format}` via `analyticsApi.getReport`.
4. **CSV** — browser downloads server-generated CSV content.
5. **PDF / Excel** — browser downloads structured payload file (server prepares data; binary rendering deferred per existing analytics report service).
