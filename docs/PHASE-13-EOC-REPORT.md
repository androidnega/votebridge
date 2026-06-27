# Phase 13 — Enterprise Operations Center (EOC)

**Date:** June 2025  
**Scope:** Full-stack operational monitoring module for Admin and Super Admin roles. No auth flow changes. No new database models. No duplicate business logic.

---

## A. Backend Completion Report

The `apps.operations` Django app delivers a read-only Enterprise Operations Center that aggregates platform metrics from existing domain services and repositories.

| Area | Status | Notes |
|------|--------|-------|
| App scaffold | ✅ | `backend/apps/operations/` — repositories, services, API, permissions, validators |
| Dashboard aggregation | ✅ | `OperationsDashboardService` composes election, session, fraud, security, comms, USSD, health, performance |
| Health monitoring | ✅ | PostgreSQL, Redis, Channels, workers, SMS/email, USSD, CPU/memory/storage (via optional `psutil`) |
| Activity feed | ✅ | Unified stream from existing `AuditLog` via `audit_log_service` |
| Performance metrics | ✅ | Cached 24h throughput, auth events, resource usage, hourly vote trend |
| REST API | ✅ | 10 endpoints under `/api/v1/operations/` |
| WebSocket consumer | ✅ | `OperationsConsumer` on `/ws/realtime/operations/` |
| Permissions | ✅ | `CanAccessOperationsCenter` (= Admin / Super Admin only) |
| Audit | ✅ | Log viewer access recorded via `monitoring_service.record_event` |
| Tests | ✅ | 5 tests — access control, validation, service composition |
| Django check | ✅ | `manage.py check` — no issues |

**No new models or migrations.** All data is read from existing tables through repositories and services.

---

## B. Frontend Completion Report

A complete Vue module mirrors every backend endpoint with lazy-loaded routes, Pinia state, and realtime WebSocket integration.

| Area | Status | Notes |
|------|--------|-------|
| API client | ✅ | `frontend/src/vue/api/operations.js` |
| Pinia store | ✅ | `stores/operations.js` — fetch actions, filters, realtime handlers |
| Sidebar navigation | ✅ | Operations group with 10 sub-items in `AppSidebar.vue` |
| Module sub-nav | ✅ | `operationsNav` in `config/moduleNav.js` |
| Router | ✅ | 10 lazy routes under `/operations/*` (admin/super_admin meta) |
| WebSocket | ✅ | `connectOperations()` in `services/websocket.js` |
| Views (10/10) | ✅ | Overview, Activity, Health, Infrastructure, Elections, Sessions, Communications, Queues, Performance, Logs |
| Build | ✅ | `npm run build` passes |

Every page uses `PageHeader`, `ModuleNav`, `LoadingSkeleton`, `EmptyState`, and design-system tokens. Overview and Activity connect to realtime on mount.

---

## C. APIs Created

Base path: `/api/v1/operations/`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `overview/` | GET | Aggregated EOC dashboard snapshot |
| `activity/` | GET | Paginated operational activity feed (category, search, hours) |
| `health/` | GET | Component health probes with status/timestamp |
| `infrastructure/` | GET | Node/link topology for infrastructure diagram |
| `elections/` | GET | Active election monitor (integrity-safe for OPEN elections) |
| `sessions/` | GET | Online users, session stats, recent sessions |
| `communications/` | GET | SMS/email/notification queue dashboard |
| `queues/` | GET | Notification, SMS, email, USSD, worker status |
| `performance/` | GET | Throughput and resource metrics with trends |
| `logs/` | GET | Audit log viewer (search, pagination, event_type filter) |

All responses: `{ "success": true, "data": ... }`.

---

## D. Services Created

| Service | File | Responsibility |
|---------|------|----------------|
| `OperationsDashboardService` | `operations_service.py` | Overview, infrastructure, election monitor, sessions, communications, queues |
| `OperationsHealthService` | `operations_service.py` | Health probes (healthy / warning / critical / unknown) |
| `OperationsActivityService` | `operations_service.py` | AuditLog → categorized activity items |
| `OperationsPerformanceService` | `operations_service.py` | Cached performance aggregates and hourly trends |

**Reused services (not duplicated):**

- `dashboard_service` — admin overview, election monitoring snapshots
- `communication_service` — comms dashboard and provider status
- `audit_log_service` — activity feed source
- `monitoring_service` — audit on log viewer access
- `ElectionResultRepository`, `USSDSessionRepository` — pending workloads and USSD stats

---

## E. Repositories Created

| Repository | File | Methods |
|------------|------|---------|
| `OperationsRepository` | `repositories/operations_repository.py` | `election_counts`, `active_elections`, `session_stats`, `pending_workloads`, `recent_votes_count`, `online_users_estimate` |

Read-only aggregation queries only. No write paths.

---

## F. Views Created

### Backend (DRF `APIView`)

- `OperationsOverviewView`
- `OperationsActivityView`
- `OperationsHealthView`
- `OperationsInfrastructureView`
- `OperationsElectionMonitorView`
- `OperationsSessionsView`
- `OperationsCommunicationsView`
- `OperationsQueuesView`
- `OperationsPerformanceView`
- `OperationsLogsView`

### Frontend (Vue SFC)

- `OperationsOverviewView.vue`
- `OperationsActivityView.vue`
- `OperationsHealthView.vue`
- `OperationsInfrastructureView.vue`
- `OperationsElectionMonitorView.vue`
- `OperationsSessionsView.vue`
- `OperationsCommunicationsView.vue`
- `OperationsQueuesView.vue`
- `OperationsPerformanceView.vue`
- `OperationsLogsView.vue`

---

## G. Components Reused

| Component | Usage |
|-----------|-------|
| `AppShell` / `DashboardLayout` | Page wrapper via router layout |
| `PageHeader` | Title, breadcrumbs, actions on every EOC page |
| `ModuleNav` | Horizontal sub-navigation |
| `StatCard` | KPI grids (Overview, Sessions, Queues, Performance) |
| `VCard` | Section containers |
| `VTable` | Election monitor, sessions, logs |
| `LoadingSkeleton` | Loading states |
| `EmptyState` | Empty activity/logs |
| `VAlert` | Error display |
| `VButton`, `VInput` | Filters and actions |
| `StatusBadge` | Election/session status |
| `ActivityFeed` | Live activity timeline |
| `ConnectionStatusIndicator` | Realtime connection on Overview |
| `VIcon` | Sidebar + empty states (`operations` icon added) |

---

## H. Components Created

| Component | File | Purpose |
|-----------|------|---------|
| `OpsHealthBadge` | `components/operations/OpsHealthBadge.vue` | healthy / warning / critical / unknown badge |
| `MetricBars` | `components/operations/MetricBars.vue` | Minimal bar chart for throughput trends |
| `InfrastructureDiagram` | `components/operations/InfrastructureDiagram.vue` | CSS/SVG node-link topology (no static images) |

---

## I. WebSocket Events

**Consumer:** `OperationsConsumer` (`/ws/realtime/operations/`)

**Subscribed groups:**

- `operations` — EOC snapshot broadcasts
- `security` — security alert events
- `fraud` — fraud case events
- `communications` — SMS/email/notification events
- `ussd` — USSD session events
- `results` — results pipeline events

**Snapshot on connect:** Full overview payload from `operations_dashboard_service.get_overview()`.

**Frontend handling (`stores/operations.js`):**

- `dashboard_stats` → refreshes overview
- Other events → prepended to `liveEvents` (max 100) for Activity/Overview realtime indicators

Uses existing `BaseRealtimeConsumer` and `realtimeService.connectOperations()` — no parallel WebSocket implementation.

---

## J. Responsive Behaviour

| Breakpoint | Layout |
|------------|--------|
| Mobile | Single-column stat grids, stacked filters, drawer sidebar |
| Tablet (`xs`+) | 2-column stat grids |
| Laptop (`lg`+) | 4-column KPI grids, persistent sidebar |
| Desktop / Ultra-wide (`2xl`+) | Overview uses `2xl:grid-cols-5`; infrastructure diagram expands horizontally |

Patterns: `grid-cols-1 xs:grid-cols-2 lg:grid-cols-4`, `flex-col sm:flex-row` headers, `VTable` mobile card fallback, lazy route chunks per page.

Sidebar collapse state persisted via existing `useSidebar` composable.

---

## K. Performance Improvements

| Technique | Detail |
|-----------|--------|
| Redis cache (30s TTL) | Overview, health, performance keys |
| Service composition | Single repository queries; no N+1 in election monitor (`select_related`) |
| Lazy routes | Each EOC page code-split |
| Paginated APIs | Activity/logs capped at 50–200 per request |
| Optional `psutil` | Resource metrics without blocking if unavailable |
| WebSocket snapshot | Initial overview pushed on connect; incremental events thereafter |

---

## L. Security Considerations

| Control | Implementation |
|---------|----------------|
| Role restriction | `CanAccessOperationsCenter` on all endpoints; router meta `roles: ['admin', 'super_admin']` |
| Election integrity | `sanitize_payload()` on OPEN election monitor data; `total_votes_cast` stripped |
| No rankings/winners | OPEN elections never expose candidate rankings, vote totals, or winners |
| Audit trail | Log viewer access recorded as `ADMIN_ACTION` |
| Read-only EOC | No mutation endpoints in operations module |
| Generic errors | Existing auth patterns unchanged |

---

## M. Architecture Compliance

| Rule | Status |
|------|--------|
| Business logic in services | ✅ All aggregation in `operations_service.py` |
| DB access via repositories | ✅ `OperationsRepository` only |
| Thin API views | ✅ Views delegate to services |
| Vue → stores/composables | ✅ `useOperationsStore` |
| Reuse existing realtime | ✅ `OperationsConsumer` + existing groups |
| No duplicate services | ✅ Composes dashboard, comms, audit, USSD, results |
| No auth changes | ✅ |
| No schema changes | ✅ No migrations |
| Design system | ✅ Flat colours, Inter, card radius, no gradients |

---

## N. Testing Strategy

| Test | Location | Coverage |
|------|----------|----------|
| Student 403 on overview | `test_operations.py` | Permission enforcement |
| Admin 200 + payload shape | `test_operations.py` | Happy path |
| Invalid activity category | `test_operations.py` | Validator |
| Health check structure | `test_operations.py` | Service probe |
| Overview composition | `test_operations.py` | Dashboard service |

**Recommended manual QA:**

1. Login as `admin@ttu.edu.gh` → navigate Operations sidebar
2. Verify Overview loads stats and WebSocket connects (green indicator)
3. Open Election Monitor during an OPEN demo election — confirm no vote totals/rankings
4. Filter Live Activity by Security / Fraud categories
5. Run `python manage.py test apps.operations.tests`

---

## O. Migration Notes

**No database migrations required.**

Deployment steps:

1. Ensure `apps.operations` is in `INSTALLED_APPS` (already wired)
2. Ensure Redis is available for cache and Channels
3. Optional: add `psutil` to requirements for CPU/memory/disk metrics (graceful fallback to `unknown` without it)
4. Rebuild frontend: `npm run build`
5. Restart ASGI worker for `OperationsConsumer` route

---

## P. Recommended Next Phase

| Priority | Enhancement |
|----------|-------------|
| High | Log export endpoint + CSV download on Logs page |
| High | Dedicated WebSocket client count metric (Channels layer introspection) |
| Medium | Time-series storage for API latency / auth / vote metrics (Prometheus or TimescaleDB) |
| Medium | Virtual scrolling on Activity feed for very large audit volumes |
| Medium | Global search (⌘K) entries for Operations routes |
| Low | Alert thresholds configurable per component (warning/critical boundaries) |
| Low | Push notifications to EOC when health status degrades |

---

**Verification commands:**

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.development python manage.py check
cd backend && python manage.py test apps.operations.tests
cd frontend && npm run build
```

**Access:** Admin or Super Admin → Sidebar → Operations → Overview (`/operations`).
