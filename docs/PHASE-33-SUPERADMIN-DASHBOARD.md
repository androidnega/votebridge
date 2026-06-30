# Phase 33 — Super Admin Dashboard Redesign

**Type:** Frontend executive dashboard (no backend changes)  
**Date:** June 2026  
**Scope:** Super Admin dashboard only (`SuperAdminDashboardView.vue`)

---

## A. Completion Report

Phase 33 replaces the previous sparse governance center with a **clean executive command center** for Super Admins. The layout surfaces platform health, KPIs, participation trends, election lifecycle distribution, voting channels, operational summaries, recent activity, and quick governance actions — all from **existing APIs and cached analytics**.

### Deliverables

| Area | Outcome |
|------|---------|
| Layout | Greeting header, platform status strip, 4 KPIs, chart section, 3 operational cards, activity feed, quick actions |
| Charts | Participation trend (line), election status (donut), voting channels (horizontal bar) via Apache ECharts |
| Data | Reuses dashboard, operations, results, and analytics stores — no new endpoints |
| Composable | `useSuperAdminDashboard.js` centralises fetch orchestration and derived metrics |
| Documentation | This document |

### Dashboard layout

```
┌─────────────────────────────────────────────────────────────┐
│ Greeting + date                          [Live indicator]   │
├─────────────────────────────────────────────────────────────┤
│ Platform status: health · open elections · realtime         │
├──────────┬──────────┬──────────┬────────────────────────────┤
│ KPI 1    │ KPI 2    │ KPI 3    │ KPI 4                      │
├──────────────────────────────┬──────────────────────────────┤
│ Participation trend (line)   │ Election status (donut)      │
├──────────────────────────────┴──────────────────────────────┤
│ Voting channels (horizontal bar)                            │
├──────────────┬──────────────┬───────────────────────────────┤
│ Security     │ Results      │ Platform load                 │
├──────────────────────────────┬──────────────────────────────┤
│ Recent platform activity     │ Quick actions panel           │
└──────────────────────────────┴──────────────────────────────┘
```

---

## B. Architecture Compliance

- **No backend changes** — Views → Services → Repositories → Models unchanged
- **No new APIs** — all data from existing dashboard, operations, results, and analytics endpoints
- **No duplicated business logic** — aggregation remains in backend services; Vue composable only maps and merges store snapshots
- **Election integrity preserved** — no candidate rankings, vote totals per candidate, or winners exposed while elections are OPEN beyond existing aggregate platform metrics
- **Component pattern** — presentation in `SuperAdminDashboardView.vue`; data orchestration in `useSuperAdminDashboard.js`

---

## C. Database Changes

None.

---

## D. APIs

No endpoints added or modified. Data sources:

| Store / endpoint | Purpose |
|------------------|---------|
| `GET /dashboard/admin-overview/` | Turnout, votes cast, security alerts, fraud cases, active elections |
| `GET /dashboard/security-feed/` | Recent security alerts for activity feed |
| `GET /security/monitoring/` | Monitoring summary (via `fetchSuperAdminDashboard`) |
| `GET /fraud/integrity-report/` | Fraud integrity snapshot |
| `GET /elections/` | Election list counts |
| `GET /users/` | Active user count |
| `GET /operations/overview/` | Platform health, election counts, sessions, workloads, USSD/SMS summaries |
| `GET /results/queues/` | Certification and publication queue lengths |
| `GET /analytics/overview/` | Cached participation trend, election status distribution, completed elections |
| Dashboard WebSocket (`super-admin` scope) | Live activity feed and stat updates |

Fetch strategy avoids duplicate calls: operations and analytics overviews are fetched only when store cache is empty.

---

## E. Vue Components

### New

| File | Purpose |
|------|---------|
| `composables/useSuperAdminDashboard.js` | Load orchestration, KPI/chart/activity computed properties |

### Updated

| File | Changes |
|------|---------|
| `views/dashboard/SuperAdminDashboardView.vue` | Full executive command center layout |

### Reused

| Component | Role |
|-----------|------|
| `LineChart`, `DonutChart`, `BarChart` | ECharts visualisations (lazy-loaded) |
| `ActivityFeed` | Recent platform activity list |
| `OpsHealthBadge`, `ConnectionStatusIndicator` | Platform status strip |
| `VCard`, `VButton`, `VAlert`, `LoadingSkeleton` | Card shell and states |

### Chart descriptions

| Chart | Type | Data field | Notes |
|-------|------|------------|-------|
| Participation trend | Line (area) | `analytics.overview.trends.votes_hourly` | Last 24 hours vote throughput |
| Election status | Donut | `analytics.overview.election_status` or `operations.overview.elections` | Lifecycle distribution; zero-count statuses hidden |
| Voting channels | Horizontal bar | Derived from `total_votes_cast` and `ussd_summary.completed_votes` | Web = total − USSD; no new channel API |

---

## F. Security Impact

- Super Admin only route unchanged; no new data exposed
- OPEN election integrity rules unchanged — charts show platform-level aggregates only
- Security feed and fraud counts reuse existing authorised endpoints

---

## G. Performance Impact

- **Cached analytics** — `GET /analytics/overview/` served from Redis cache (60s TTL) on backend
- **Conditional fetches** — operations/analytics overviews skipped when Pinia cache is warm
- **Lazy charts** — ECharts components loaded via `defineAsyncComponent`
- **Single WebSocket** — dashboard realtime scope only; no duplicate analytics socket on this page
- **Parallel load** — `Promise.allSettled` for independent store fetches

---

## H. Responsive Design Notes

| Breakpoint | Behaviour |
|------------|-----------|
| Desktop (`xl`) | Four KPI cards in one row; charts 2/3 + 1/3; activity + actions side by side |
| Tablet (`sm`–`lg`) | Two KPI cards per row; charts stack; operational cards 3-column on `md` |
| Mobile | Single-column throughout; platform status wraps; quick actions full width |

All cards use white surfaces, `border-border`, `rounded-card`, and `shadow-card` per UI standards. No gradients.

---

## I. Testing Strategy

| Layer | Approach |
|-------|----------|
| Manual | Load `/dashboard` as Super Admin — verify KPIs, charts, activity, quick actions |
| Responsive | Resize to mobile/tablet/desktop breakpoints |
| Empty states | Seed-less env — charts and activity show empty copy |
| Regression | Admin and student dashboards unchanged |
| Automated | `python manage.py test`, `npm run build` |

---

## J. Deployment Notes

- Frontend-only deploy; no migrations or environment variables
- No seed data changes required
- Safe to roll out independently of backend releases

### Verification

| Command | Result |
|---------|--------|
| `npm run build` | Pass |
| `python manage.py check` | Not run — Django venv unavailable in shell |
| `python manage.py test` | Not run — Django venv unavailable in shell |
