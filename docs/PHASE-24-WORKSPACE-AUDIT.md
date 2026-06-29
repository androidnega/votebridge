# Phase 24 — Enterprise Workspace & Page Rationalization Audit

**Audit type:** Read-only product, workflow, and usability review  
**Date:** June 2025  
**Scope:** Every page, tab, widget, and action accessible to **Super Admin** and **Admin**  
**Constraint:** No backend functionality removal recommended — navigation and presentation only

---

## Executive Summary

Phase 23 successfully reduced sidebar noise, but the product still carries **enterprise platform surface area** beneath a thinner navigation layer. Super Admin retains access to **60+ distinct routes** (including legacy deep links). Admin retains **40+ routes** despite a **5-item** primary sidebar (excluding Profile).

**Key findings:**

1. **Election lifecycle is fragmented** — create, positions, candidates, and eligibility live on separate pages; schedule, close, pause, and candidate approval are missing or buried in the API layer.
2. **Strong Room has 9 top-level tabs** — several reuse full standalone pages with conflicting breadcrumbs; **Certification duplicates Results**.
3. **Reports primary tabs are reasonable**, but **Reports Overview is overloaded** with ops/security KPIs and duplicates dashboard metrics; **10 advanced analytics pages** remain orphaned without in-UI discovery.
4. **Settings has 12 tabs plus 10+ hub-only pages** — appropriate for platform owners, excessive for university election officers.
5. **Dashboards still duplicate turnout, open elections, and health signals** across Admin, Super Admin, Reports, and Operations (deep link).
6. **Admin can reach technical pages via URL/search** (Operations, Fraud, Security, USSD) though they are hidden from the sidebar — a partial consolidation.

**Overall product posture:** Closer to a university election platform than pre-Phase 23, but still **hybrid** between election operations and infrastructure administration.

---

## 1. Super Admin Audit

### 1.1 Sidebar inventory

| Sidebar item | Route | Module tabs (in-page) |
|--------------|-------|------------------------|
| Dashboard | `/` | — |
| Election management | `/elections` | Elections, Candidates, Positions, Voter eligibility |
| Results | `/results` | Overview, Certification, Publication, Archive |
| Reports | `/reports` | Overview, Participation, Turnout, Results, Historical trends, Export reports |
| Strong room | `/strongroom` | 9 tabs (see §3) |
| Settings | `/settings` | 12 tabs (see §4) |
| Profile | `/profile` | — |

### 1.2 Dashboard (`/` → `SuperAdminDashboardView`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Command-center snapshot: elections in progress, turnout, security, platform health |
| **Workflow** | Morning check-in before/during elections; triage alerts |
| **Frequency** | Daily during election season; weekly otherwise |
| **Widgets** | 4 StatCards (open elections, turnout %, security alerts, total elections); `PlatformHealthWidgets` (6 tiles); open election cards; activity feed; live security feed |
| **Quick actions** | Elections, Reports, Strong room, Settings |
| **APIs** | `dashboardApi` (super-admin overview), `operationsApi.getOverview`, `securityApi` feed + WebSocket |

| Question | Assessment |
|----------|------------|
| Why does it exist? | Single landing point for election + platform status |
| Who needs it? | Super Admin, returning officers |
| How often? | High during active elections |
| Belongs on main page? | Yes — but **trim duplicate metrics** |
| Merge opportunity? | Turnout/open elections overlap Reports; health tiles duplicate Operations |
| Implementation detail? | Platform health tiles are **infra-oriented** |
| Hide until required? | Health tiles only when degraded |

**Verdict:** **Essential, slightly overloaded.** Feels election-focused at the top but still surfaces infrastructure. **Too technical** for a pure election-officer mental model.

---

### 1.3 Election Management

#### Elections list (`/elections`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Browse all elections; entry to detail |
| **Tabs** | ModuleNav: Elections, Candidates, Positions, Eligibility |
| **Actions** | Create election (button → `/elections/create`); row click → detail |
| **APIs** | `electionsApi.list` |

**Verdict:** **Essential.** Table-only; no inline status actions (schedule/close).

#### Create election (`/elections/create`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Create draft election (title, type, dates, channel flags) |
| **Frequency** | Per election cycle (low) |
| **APIs** | `electionsApi.create` |

**Verdict:** **Essential one-time setup.** Correctly not on daily path.

#### Election detail (`/elections/:uuid`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Election hero, countdown, readiness checklist, open action, position/candidate preview |
| **Widgets** | Status badge, countdown, readiness panel, position list, candidate preview cards |
| **Actions** | Refresh readiness; **Open election** (scheduled only, when ready) |
| **APIs** | `electionsApi.get`, `getReadiness`, `open`; voting preview API |
| **Missing in UI** | Schedule, pause, close, archive (API exists in `electionsApi`) |

**Verdict:** **Essential hub** but **missing lifecycle actions** — officers must use legacy Django dashboard or API for most transitions.

#### Candidates (`/election-management/candidates`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Per-election candidate list + add form |
| **Actions** | Add candidate (name, department, manifesto, position) |
| **Missing** | Approve/reject (API exists); photo upload; edit/delete |
| **APIs** | `listPositions`, `listCandidates`, `createCandidate` |

**Verdict:** **Essential but incomplete** for real approval workflow.

#### Positions (`/election-management/positions`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Per-election position list + add form |
| **APIs** | `listPositions`, `createPosition` |

**Verdict:** **Essential.** No edit/delete in UI.

#### Voter eligibility (`/election-management/eligibility`)

| Aspect | Detail |
|--------|--------|
| **Purpose** | Per-election eligibility records |
| **Actions** | Add by **raw user UUID** (high friction) |
| **APIs** | `listEligibility`, `createEligibility` |

**Verdict:** **Essential function, poor UX** — feels like an implementation surface, not an election officer tool.

**Election Management overall:** **Fragmented across 5 routes** with repeated election picker. **Missing functionality** for schedule/close/approve. **Too technical** on eligibility.

---

### 1.4 Results (`/results` + children)

| Page | Purpose | Tabs | Super Admin only? | APIs |
|------|---------|------|-------------------|------|
| Overview | List results with status, turnout, view detail | Results nav (4) | No — Admin sees overview only | `results` list, queues WS |
| Certification | Queue of results awaiting certification | Shared `resultsNav` | Yes | `fetchQueues` |
| Publication | Publish certified results | Shared | Yes | `publish` |
| Archive | Archive published results | Shared | Yes | archive APIs |
| Detail (`/results/:uuid`) | Per-election result breakdown | — | No | result detail |

**Admin experience:** Results nav tabs **hidden** — Admin gets list + detail only (appropriate).

**Duplication:** Certification also appears under **Strong Room** (same `CertificationQueueView` component).

**Verdict:** **Essential workspace.** Super Admin tabs are well-scoped. **Certification should not live in two workspaces.**

---

### 1.5 Reports (`/reports` + children)

See §5 for full Reports audit. Super Admin has same access as Admin for primary Reports tabs.

**Hidden advanced pages** (no sidebar/tab link): `/analytics/students`, `/departments`, `/faculties`, `/programmes`, `/security`, `/fraud`, `/operations`, `/communications`, `/ussd`, `/strongroom` — reachable only via URL, search, or external docs.

**Verdict:** Primary Reports **usable**; advanced analytics **under-discovered**.

---

### 1.6 Strong Room (`/strongroom` workspace)

See §3. Super Admin only in sidebar; routes also allow Admin via deep link.

**Verdict:** **Essential for Super Admin** but **over-tabbed** and internally inconsistent (breadcrumbs).

---

### 1.7 Settings (`/settings` workspace)

See §4. Super Admin only.

**Verdict:** **Required for platform owner**, not for day-to-day election officers. Correctly restricted.

---

### 1.8 Profile (`/profile`)

Account settings, password, session — **essential**, low traffic.

---

### 1.9 Deep-link pages (Super Admin, not in sidebar)

| Route cluster | Pages | Purpose | Frequency | Verdict |
|---------------|-------|---------|-----------|---------|
| `/operations/*` | 9 views | Infra monitoring, queues, sessions, performance | Incident-driven | **Hide until alert** — correctly off sidebar |
| `/communications/*` | 6 views | SMS/email templates, providers, queue, test | Setup + incidents | **Settings-adjacent** |
| `/ussd/*` | 3+ views | USSD dashboard, sessions, logs | During USSD elections | **Voting channels** |
| `/platform/logs` | 1 view (3 query tabs) | Ops/comms/USSD audit logs | Investigations | **Strong Room audit** |
| `/security`, `/fraud` | 2 views | Standalone security/fraud dashboards | Incidents | **Duplicate Strong Room tabs** |
| `/analytics/*` | 10 advanced | Dimensional drill-downs | Ad hoc reporting | **Reports drill-downs** |
| `/system-control/*` | Legacy aliases | Same as Settings | Rare | **Backward compat** |
| `/biometrics/enroll` | 1 view | Enrollment | One-time setup | **Settings → Identity** |
| `/verify` | Public | Result verification | Post-election | **Evidence export link** |

---

## 2. Admin Audit

### 2.1 Sidebar vs accessible surface

**Sidebar (5 + Profile):** Dashboard, Election management (4 children), Results, Reports, Profile.

**No sidebar access:** Strong Room, Settings, Results certification/publication/archive.

**Still reachable** (router allows `admin` role): `/strongroom/*`, `/security`, `/fraud`, `/operations/*`, `/communications/*`, `/ussd/*`, `/platform/logs`, `/analytics/*`, `/biometrics/history`.

### 2.2 Unnecessary options for Admin

| Item | Issue |
|------|-------|
| Platform health widgets on dashboard | 6 infra tiles — **election officers don't need WebSocket/queue detail daily** |
| Reports Overview — system utilization | CPU/memory/disk gauges — **implementation detail** |
| Reports Overview — fraud/security KPIs | Investigative; belongs in Strong Room (Super Admin) |
| Deep-link Operations/Fraud/Security | **Role confusion** — hidden from nav but discoverable via search |
| Global search entries for USSD, ops health | Surfaces technical pages to Admin |

### 2.3 Duplicate functionality (Admin)

| Duplication | Locations |
|-------------|-----------|
| Turnout / votes cast | Dashboard StatCards + LiveTurnoutWidget + Reports Overview |
| Open elections count | Dashboard + Reports (election KPIs) + Operations (deep link) |
| Security alerts | Dashboard + Reports Overview + Activity feed fallback text (points to removed Security Center) |
| Election list | Elections page + Dashboard cards |
| Participation vs Turnout reports | Overlapping charts (programme turnout vs election turnout table) |

### 2.4 Missing workflow steps (Admin)

| Step | Status |
|------|--------|
| Schedule election | **No Vue UI** (API: `schedule`) |
| Approve/reject candidates | **No Vue UI** (API exists) |
| Bulk eligibility import | **No Vue UI** |
| Search voter by index number | **No Vue UI** (UUID only) |
| Close / pause election | **No Vue UI** |
| Monitor live turnout during election | Partial — dashboard widget only; no dedicated election monitor for Admin |
| Post-close results | View only — certification/publication **Super Admin only** |

### 2.5 Read-only vs hidden recommendations

| Page | Recommendation |
|------|----------------|
| Results detail (after publish) | **Read-only** for Admin — appropriate |
| Results certification/publication | **Hidden from Admin** — correct (Super Admin) |
| Strong Room | **Hidden from Admin sidebar** — correct; deep link still works (consider guard alignment) |
| Settings | **Hidden** — correct |
| Advanced analytics (security, fraud, ops) | **Read-only or Super Admin only** for investigations |
| Operations infrastructure | **Super Admin / on-call only** |

### 2.6 Admin overall verdict

Admin workspace is **closer to election operations** than Super Admin but still exposes **technical depth** through dashboard widgets, Reports overview, and discoverable deep links. **Missing functionality** hurts the core Admin journey more than **excess navigation**.

---

## 3. Strong Room Audit

### 3.1 Current sections

| Tab | Route | Component | Standalone page? | Primary use phase |
|-----|-------|-----------|------------------|-------------------|
| Vote integrity | `/strongroom` | `StrongroomDashboardView` | Yes (election list) | Post-vote / certification |
| Certification | `/strongroom/certification` | `CertificationQueueView` | **Duplicate of Results** | Certification |
| Audit trail | `/strongroom/audit` | `PlatformLogsView` | Yes (full page embedded) | Investigations |
| Fraud investigation | `/strongroom/fraud` | `FraudView` | Yes (own PageHeader) | Investigations |
| Chain of custody | `/strongroom/custody` | `StrongroomCustodyHubView` | Hub → election detail | Certification / audit |
| Identity assurance | `/strongroom/identity` | `BiometricHistoryView` | Yes (breadcrumb: Security) | Investigations |
| Trusted devices | `/strongroom/trusted-devices` | `TrustedDevicesView` | Yes | Security incidents |
| Security timeline | `/strongroom/security` | `SecurityView` | Yes (own PageHeader) | Live monitoring |
| Evidence export | `/strongroom/export` | `StrongroomEvidenceExportView` | Link hub (3 cards) | Post-certification |

**Per-election detail:** `/strongroom/:electionUuid` — integrity score, seals, custody timeline, verify/lock actions.

### 3.2 Per-section analysis

#### Vote integrity (dashboard)
- **Why:** Entry to per-election strongroom records
- **Who:** Super Admin (primary), Admin (deep link)
- **Frequency:** Post-election, certification periods
- **Separate page?** Yes — election picker list is appropriate
- **Merge?** Could merge with Chain of custody (both are election-scoped lists)

#### Certification
- **Duplicate** of `/results/certification`
- **Recommendation:** **Single location** under Results OR Strong Room, not both; cross-link only

#### Audit trail
- **Reuses** Platform Logs with 3 sub-tabs (operations, communications, USSD)
- **Investigation-only** — correct workspace
- **Could be tab** within a unified "Investigation" view rather than top-level peer to Vote integrity

#### Fraud investigation
- Overlaps **Security timeline** (alerts) and **Reports → fraud analytics**
- **Investigation-only**
- **Could merge** with Security timeline as "Incidents" tab with fraud | alerts sub-tabs

#### Chain of custody
- Hub duplicates Vote integrity list with custody-focused copy
- **Could be tab** on election strongroom detail, not top-level

#### Identity assurance
- **Overlaps** Settings → Identity assurance (config) and Biometric history
- Investigation view — **correct in Strong Room**
- Settings copy is **configuration** — keep separate purposes but **clarify naming**

#### Trusted devices
- Niche — **incident-driven**
- **Could be modal/panel** from Security timeline case row

#### Security timeline
- Live alert feed — overlaps dashboard `LiveSecurityFeed` and Fraud KPIs
- **Could merge** with Fraud investigation

#### Evidence export
- **Link hub only** — not a feature page
- **Should be actions** on Results/Strongroom detail, not a tab

### 3.3 Recommended simplified investigation workspace (conceptual — not implemented)

```
Strong Room
├── Overview          (election integrity list — current Vote integrity)
├── Election detail   (per-election: seals, custody, verify, export actions)
├── Certification     (OR link to Results — pick one home)
└── Investigations    (single area)
    ├── Tabs: Alerts | Fraud cases | Audit log | Biometrics | Devices
    └── Filters: election, date range, severity
```

**Reduce 9 top-level tabs → 3–4.** Move Evidence export to contextual actions. Fold custody into election detail.

---

## 4. Settings Audit

### 4.1 Primary tabs (`settingsNav` — 12 items)

| Page | Required? | Visit frequency | Grouping | One-time setup? | Hide from daily nav? |
|------|-----------|-----------------|----------|-----------------|----------------------|
| Overview | Yes | Monthly | — | No | No (hub) |
| Institution | Yes | Once / year | **Institution** | Yes | After setup |
| Authentication | Yes | Rare | **Security** | Mostly | Yes |
| Communication providers | Yes | Once + fixes | **Communications** | Partial | After setup |
| Voting channels | Yes | Per election | **Communications** | No | No |
| Maintenance | Yes | Incidents | **Operations** | No | **Until needed** |
| Feature flags | Debatable | Rare | **Platform** | No | **Yes — power user** |
| Backup | Yes | Weekly/monthly | **Operations** | No | **Until needed** |
| System configuration | Hub only | Rare | **Operations** | Partial | Yes |
| Identity assurance (config) | Yes | Once | **Security** | Yes | After setup |
| Security policies | Yes | Rare | **Security** | Mostly | Yes |
| API & integrations | Yes | Once | **Integrations** | Yes | After setup |

### 4.2 Hub-only / legacy pages (not in tab bar)

| Page | Route | Notes |
|------|-------|-------|
| Branding | `/settings/branding` | One-time — **merge under Institution** |
| Election policies | `/settings/election-policies` | Linked from Voting channels |
| Notifications | `/settings/notifications` | Linked from Voting channels |
| USSD config | `/settings/ussd` | Linked from Voting channels |
| SMS / Email | `/settings/sms`, `/settings/email` | Sub-pages of providers |
| Runtime / Environment / Storage / Audit | `/settings/system` hub | **Technical — IT only** |
| License / About | Hub "License & about" | **Rare** |

### 4.3 Recommended Settings hierarchy (conceptual)

```
Settings
├── Overview (status banner + grouped cards — keep)
├── Institution & branding
│   ├── Profile, branding, election policies
├── Voting & communications
│   ├── Voting channels (web, USSD, SMS)
│   ├── Providers, templates (link to /communications/templates)
│   └── Test center
├── Security & access
│   ├── Authentication, identity assurance, security policies
│   └── API & integrations
└── Platform operations (collapsed / advanced)
    ├── Maintenance, backup, feature flags
    └── System configuration (runtime, env, storage, audit)
```

**Reduce visible tabs from 12 → 5 groups.** Feature flags and runtime config are **implementation details** for most university admins.

---

## 5. Reports Audit

### 5.1 Primary Reports tabs

| Tab | Content | Overlap |
|-----|---------|---------|
| Overview | 8 KPIs, participation gauge, vote throughput chart, **CPU/memory/disk** | Dashboard + Operations |
| Participation | Programme bar chart, heatmap | Overview turnout |
| Turnout | `AnalyticsElectionsView` — trend line, bar chart, comparison table | Overview + Results |
| Results | **Same component as Turnout** | **Direct duplicate tab** |
| Historical trends | Time-series institutional trends | Turnout/historical elsewhere |
| Export reports | Type + format selectors, download | Evidence export hub |

### 5.2 Duplicated / unnecessary KPIs (Reports Overview)

| KPI | Also on |
|-----|---------|
| Overall turnout / Avg turnout | Admin dashboard, Super Admin dashboard |
| Total votes | Dashboard |
| Fraud cases / Security alerts | Dashboard, Strong Room, Operations |
| SMS success % | Operations, Communications |
| System utilization (CPU/RAM/Disk) | Operations, Settings overview |

### 5.3 Advanced analytics (orphaned drill-downs)

10 pages under `/analytics/*` — students, departments, faculties, programmes, security, fraud, operations, communications, USSD, strongroom.

- **Not linked** from Reports ModuleNav
- **Appropriate as drill-downs** from Participation, Turnout, or Investigation areas
- Several **overlap** primary tabs (e.g. `analytics/security` vs Strong Room)

### 5.4 Recommendations

1. **Remove duplicate Turnout / Results tab** — single "Election results & turnout" tab
2. **Strip Reports Overview** to 4–5 election KPIs; link "View infrastructure" to Operations (Super Admin)
3. **Move fraud/security/ops KPIs** to Strong Room or advanced section
4. **Surface advanced analytics** as "Explore by dimension" from Overview, not orphan URLs
5. **Export** — keep; add contextual export on Results detail

---

## 6. Dashboard Audit

### 6.1 Super Admin dashboard — primary questions

| Question | Answered? | Where |
|----------|-----------|-------|
| Are elections running? | Yes | Open elections cards + stat |
| How is turnout? | Yes | Turnout stat (duplicated in Reports) |
| Any security issues? | Yes | Alerts stat + security feed |
| Is platform healthy? | Partially | Health widgets (technical) |
| What should I do next? | Weak | No prioritized action queue |

### 6.2 Admin dashboard — primary questions

| Question | Answered? | Where |
|----------|-----------|-------|
| What elections are open? | Yes | Cards + stat |
| How is turnout? | Yes | LiveTurnoutWidget + votes stat |
| Any blockers? | Partial | Alerts only; fraud text references removed Security Center |
| Can I manage elections? | Yes | Quick buttons |
| System health? | Over-served | 6 health tiles |

### 6.3 Duplicate / repeated elements

| Element | Super Admin | Admin |
|---------|-------------|-------|
| Open elections list | Yes | Yes |
| Turnout | Stat + (Reports) | Stat + LiveTurnoutWidget |
| Security alerts | Stat + feed + activity | Stat + activity |
| Platform health | 6 widgets | 6 widgets |
| Activity feed | Yes | Yes |

### 6.4 Recommended minimal dashboards (conceptual)

**Super Admin (5 blocks):**
1. **Election status** — open / scheduled count + open election cards
2. **Turnout snapshot** — single live widget
3. **Action queue** — certification pending, open alerts (count + links)
4. **System status** — single line (healthy / attention) — expand to Operations on click
5. **Recent activity** — 5 items max

**Admin (4 blocks):**
1. **Open elections** — cards with link to monitor
2. **Turnout** — live widget only
3. **My tasks** — readiness blockers, pending candidate approvals
4. **Quick actions** — create election, manage positions

**Remove from both:** redundant stat grid, full health widget grid on default view.

---

## 7. Election Management Audit

### 7.1 Workflow coverage

| Step | Page | In workspace? | Gap |
|------|------|---------------|-----|
| Create election | `/elections/create` | Yes | — |
| Add positions | `/election-management/positions` | Separate tab | Election picker friction |
| Add candidates | `/election-management/candidates` | Separate tab | No approve/reject |
| Set eligibility | `/election-management/eligibility` | Separate tab | UUID-only input |
| Review readiness | `/elections/:uuid` | **Outside** workspace tabs | Context switch |
| Schedule | — | **Missing** | Legacy Django only |
| Open | `/elections/:uuid` | Outside tabs | — |
| Monitor | Dashboard / Reports | Outside workspace | No election-scoped monitor |
| Close | — | **Missing** | — |

### 7.2 Unnecessary navigation

- **4 separate tabs** each with election picker instead of **election-scoped hub** (`/elections/:uuid/manage`)
- ModuleNav duplicates sidebar children
- Readiness lives on detail page but positions/candidates live elsewhere — **officers bounce between 5 routes**

### 7.3 Recommended conceptual model (not implemented)

```
Election Management
├── All elections (list + create)
└── Election workspace (:uuid)
    ├── Setup (positions, candidates, eligibility)
    ├── Readiness & schedule
    ├── Live monitor (when open)
    └── Close & handoff to results
```

---

## 8. Workflow Audit

### 8.1 Super Admin journey

```
Login → Dashboard → Review election → Strong Room → Certification → Publish Results
```

| Step | Route(s) | Page changes | Friction |
|------|----------|--------------|----------|
| Login | `/auth/login` → `/` | 2 | Low |
| Dashboard | `/` | 1 | Low |
| Review election | `/elections` → `/elections/:uuid` | 2 | Medium — no lifecycle summary |
| Strong Room | `/strongroom` → `/strongroom/:uuid` | 2 | Medium — 9 tabs intimidating |
| Certification | `/strongroom/certification` **or** `/results/certification` | 1 | **Duplicate entry points** |
| Publish | `/results/publication` | 1 | **Not linked from Strong Room** — context switch to Results |

**Unnecessary changes:** Certification in two workspaces; publish not in Strong Room flow; Strong Room sub-pages reset breadcrumbs to old "Fraud" / "Security" labels.

### 8.2 Admin journey

```
Login → Create Election → Positions → Candidates → Eligibility → Schedule → Readiness → Open → Monitor → Close
```

| Step | Route(s) | Achievable in Vue? |
|------|----------|-------------------|
| Login | `/auth/*` → `/` | Yes |
| Create | `/elections/create` | Yes |
| Positions | `/election-management/positions` | Yes (picker) |
| Candidates | `/election-management/candidates` | Partial (no approve) |
| Eligibility | `/election-management/eligibility` | Partial (UUID only) |
| Schedule | — | **No** |
| Readiness | `/elections/:uuid` | Yes (tab switch) |
| Open | `/elections/:uuid` | Yes |
| Monitor | `/` or `/reports` | Partial |
| Close | — | **No** |

**Page changes for full journey today:** **≥8 route changes** with **2 dead ends** (schedule, close) without legacy Django.

---

## 9. Workspace Complexity Scores

Scores 1 (poor/simple) – 10 (excellent/simple for users; or high complexity for Technical Complexity).

### Super Admin workspaces

| Workspace | Nav simplicity | Workflow efficiency | Enterprise readiness | User friendliness | Technical complexity |
|-----------|----------------|---------------------|----------------------|-------------------|----------------------|
| Dashboard | 7 | 6 | 8 | 6 | 6 |
| Election management | 5 | 4 | 7 | 5 | 5 |
| Results | 8 | 7 | 9 | 7 | 4 |
| Reports | 6 | 5 | 8 | 5 | 7 |
| Strong room | 4 | 5 | 9 | 4 | 8 |
| Settings | 5 | 6 | 10 | 4 | 9 |

**Justification (summary):**
- **Results** scores highest on navigation — clear tabs, matches certification workflow.
- **Strong room** scores low on simplicity — too many peer tabs, embedded pages with mismatched chrome.
- **Settings** scores high enterprise readiness (complete platform control) but low friendliness for university staff.
- **Election management** workflow efficiency is low due to fragmentation and missing lifecycle UI.

### Admin workspaces

| Workspace | Nav simplicity | Workflow efficiency | Enterprise readiness | User friendliness | Technical complexity |
|-----------|----------------|---------------------|----------------------|-------------------|----------------------|
| Dashboard | 8 | 6 | 6 | 7 | 5 |
| Election management | 5 | 3 | 6 | 4 | 5 |
| Results | 9 | 8 | 7 | 8 | 3 |
| Reports | 6 | 6 | 7 | 6 | 6 |

**Justification:** Admin sidebar is **simple (good)** but election workflow **efficiency is poor** due to missing schedule/close/approve and scattered setup pages. Results read-only view is **appropriate and friendly**.

---

## 10. Simplification Opportunities

| # | Opportunity | Impact | Effort | Backend change |
|---|-------------|--------|--------|----------------|
| 1 | Election-scoped management hub (`:uuid/setup`) | High | Medium | No |
| 2 | Add schedule/close/approve to Vue election UI | High | Medium | No (APIs exist) |
| 3 | Deduplicate Certification (Results **or** Strong Room) | Medium | Low | No |
| 4 | Collapse Strong Room to 3–4 areas | High | Medium | No |
| 5 | Group Settings into 5 sections | Medium | Low | No |
| 6 | Slim Reports Overview; merge Turnout/Results tabs | Medium | Low | No |
| 7 | Link advanced analytics from Reports | Medium | Low | No |
| 8 | Minimal dashboards; health on-demand | Medium | Low | No |
| 9 | Voter search by index for eligibility | High | Medium | No |
| 10 | Align Admin deep-link guards with sidebar policy | Low | Low | No |
| 11 | Contextual evidence export (remove tab) | Low | Low | No |
| 12 | Fix activity feed copy (Security Center → Strong room) | Low | Trivial | No |

---

## 11. Final Recommendations

### Priority 1 — Election officer productivity
1. **Unify election setup** under a single election workspace with sub-steps (positions → candidates → eligibility → readiness).
2. **Complete lifecycle UI** in Vue: schedule, pause, close, archive, candidate approve/reject.
3. **Replace UUID eligibility** with index-number search and bulk import.

### Priority 2 — Workspace rationalization
4. **Pick one home for Certification** (recommend **Results**); Strong Room links there.
5. **Consolidate Strong Room investigations** into one area with sub-tabs; move custody to election detail.
6. **Collapse Settings** visible tabs into 5 groups; tuck feature flags and runtime under "Advanced".

### Priority 3 — Reporting & dashboards
7. **Slim dashboards** to election-first blocks; defer infrastructure to alert-driven drill-down.
8. **Deduplicate Reports** — one turnout/results tab; move ops KPIs out of Reports Overview.
9. **Wire advanced analytics** into Reports as explicit drill-downs.

### Priority 4 — Role clarity
10. **Admin:** remove or guard deep-link technical routes not in sidebar; fix stale navigation copy.
11. **Super Admin:** treat Settings + Strong Room as **distinct modes** — "Run elections" vs "Own platform" — consider a mode switcher rather than flat sidebar.

### What not to do
- Do not remove APIs, services, or backend modules.
- Do not delete Operations, Communications, or Analytics — **re-home** behind health alerts, Settings, and Reports drill-downs.
- Do not expose candidate rankings or live totals while elections are OPEN (integrity rule unchanged).

---

## Appendix A — Complete route inventory (Admin & Super Admin)

### Sidebar-visible (Admin)
`/`, `/elections`, `/elections/create`, `/election-management/*`, `/results`, `/results/:uuid`, `/reports`, `/reports/*`, `/profile`

### Sidebar-visible (Super Admin additional)
`/strongroom`, `/strongroom/*`, `/settings`, `/settings/*`, `/results/certification`, `/results/publication`, `/results/archive`

### Deep-link only (both roles unless noted)
`/security`, `/security/trusted-devices`, `/fraud`, `/operations/*`, `/communications/*`, `/ussd/*`, `/platform/logs`, `/analytics/*`, `/biometrics/history`

### Super Admin only (guarded)
`/settings/*`, `/system-control/*`, `/results/certification|publication|archive`, `/biometrics/enroll`

---

## Appendix B — API dependency map (frontend stores)

| Workspace | Primary stores / APIs |
|-----------|----------------------|
| Dashboard | `dashboardStore`, `operationsStore`, `securityStore` |
| Elections | `electionStore`, `electionsApi`, `votingStore` |
| Results | `resultsStore` |
| Reports | `analyticsStore` |
| Strong room | `strongroomStore`, `fraudStore`, `securityStore`, `operationsStore`, `notificationsStore`, `ussdStore` |
| Settings | `systemControlStore` |
| Operations (deep) | `operationsStore` |
| Communications (deep) | `notificationsStore`, communications APIs |

---

*End of Phase 24 audit. No code was modified. Await implementation phase instructions.*
