# Phase 29 — Governance Alignment & Product Experience Enhancement

**Type:** Governance separation + UX enhancement  
**Date:** June 2025  
**Baseline:** Phase 28 product experience (`8ce488e`)

---

## 1. Executive Summary

Phase 29 aligns VoteBridge with **real-world university election governance** by separating operational election management (Election Administrator / `admin`) from platform governance (Super Admin / `super_admin`). The Election Control Room received a dark SOC-style redesign, and a new public landing page displays live campus election phase using existing services.

### Verification results

| Command | Result |
|---------|--------|
| `python manage.py check` | ✅ Pass |
| `python manage.py test` | ✅ Pass (75 tests) |
| `npm run build` | ✅ Pass |

---

## 2. Governance Model

### Separation of duties

| Responsibility | Election Administrator (`admin`) | Super Admin (`super_admin`) |
|----------------|-----------------------------------|----------------------------|
| Create / edit / delete elections | ✅ | ❌ |
| Positions, candidates, eligibility | ✅ | ❌ |
| Open / pause / resume / close / archive | ✅ | ❌ |
| Generate & preview results | ✅ | ❌ |
| Strong room | ❌ | ✅ |
| Certify / publish / archive results | ❌ | ✅ |
| Institution & security settings | ❌ | ✅ |
| Fraud investigations | ❌ | ✅ |
| Reports (read) | ✅ | ✅ |

Super Admin may **read** elections (list/detail) for oversight but cannot mutate election lifecycle or configuration.

---

## 3. Updated Permission Matrix

### Backend permission classes

| Class | Phase 29 roles |
|-------|----------------|
| `CanManageElections` (write) | `admin` only |
| `CanManageCandidates` (write) | `admin` only |
| `CanManagePositions` (write) | `admin` only |
| `CanManageVoterEligibility` (write) | `admin` only |
| `CanManageVotingChannels` (write) | `super_admin` only |
| `CanGenerateResults` | `admin` only |
| `CanViewResultReports` | `admin` only |
| `CanCertifyResults` | `super_admin` only |
| `CanPublishResults` | `super_admin` only |
| `CanArchiveResults` | `super_admin` only |
| `CanViewStrongroom` | `super_admin` only |
| `CanManageStrongroom` | `super_admin` only |
| `PublicCampusStatusView` | `AllowAny` |

New base class: `IsElectionAdministrator` in `apps/accounts/permissions.py`.

### Frontend getters

| Getter | Meaning |
|--------|---------|
| `isElectionOfficer` | `admin` — election operations |
| `isSuperAdmin` | `super_admin` — governance |
| `isStaff` | `admin` or `super_admin` — shared admin surfaces (reports, results hub) |
| `isAdmin` | `admin` only (alias for election officer) |

---

## 4. Election Control Room Redesign

**File:** `frontend/src/vue/views/elections/workspace/ElectionWorkspaceMonitor.vue`  
**Route:** `/elections/:uuid/monitor` (tab label: **Control room**)

### Design

- Dark slate (`bg-slate-950`) SOC aesthetic
- Large turnout percentage and countdown to close
- System link and security posture indicators
- Channel activity, fraud flags, security alerts
- Incident panel + recent events feed (`ActivityFeed`)
- Critical actions with `ConfirmDialog`: Pause, Close, Emergency incident

No business logic changes — uses existing `electionStore`, `operationsStore`, and `useDashboardRealtime`.

### Screenshots

> Screenshots should be captured from a running dev server with an open election:
> - Desktop: 1440px — control room full layout
> - Mobile: 390px — stacked metrics and action buttons

---

## 5. Landing Page Redesign

**Route:** `/welcome` (public)  
**File:** `frontend/src/vue/views/public/LandingView.vue`

### Sections

- Hero (TTU branding + VoteBridge)
- Current election status (dynamic)
- Secure voting overview
- Voting process (4 steps)
- Platform security & Why VoteBridge
- FAQ
- Support & Sign in

### Dynamic phases (`GET /api/v1/elections/public/campus-status/`)

| Phase | Display |
|-------|---------|
| `before_election` | Standby |
| `election_scheduled` | Scheduled |
| `election_open` | Voting open |
| `awaiting_certification` | Processing |
| `results_published` | Results published |

Uses `election_service.get_public_campus_status()` — no vote totals or rankings exposed.

Unauthenticated users visiting `/` are redirected to `/welcome`.

---

## 6. Architecture Compliance

✅ Views → Services → Repositories → Models preserved  
✅ Public status endpoint delegates to `ElectionService`  
✅ No duplicated business logic  
✅ Frontend-only control room and landing presentation changes

---

## A. Completion Report

Governance separation enforced in backend permissions and frontend navigation. Super Admin UI reframed as platform governance center. Election Control Room and public landing page delivered.

## B. Architecture Compliance

See §6.

## C. Database Changes

None.

## D. APIs

| Endpoint | Change |
|----------|--------|
| `GET /api/v1/elections/public/campus-status/` | **New** — public election phase |
| Election write endpoints | `super_admin` → 403 |
| Strong room endpoints | `admin` → 403 |

## E. Vue Components

- `LandingView.vue` (new)
- `ElectionWorkspaceMonitor.vue` (control room redesign)
- `SuperAdminDashboardView.vue` (governance focus)
- `auth.js` getters, `sidebarNav.js`, router roles, `PublicLayout.vue`

## F. Security Impact

**Positive:** Enforced separation of duties at API and UI layers. Super Admin cannot alter active elections or certify and operate simultaneously without a separate admin account.

## G. Performance Impact

Neutral. Public campus status is a lightweight read. Control room uses existing realtime feeds.

## H. Responsive Design Notes

Control room stacks metrics on mobile; action buttons wrap. Landing page uses responsive grids throughout.

## I. Testing Strategy

- `backend/apps/elections/tests/test_governance.py` — super_admin 403 on create/open; public status anonymous
- Existing suite regression (75 tests)
- Manual: super_admin sidebar has no election workspace; admin control room on open election

## J. Deployment Notes

Deploy backend + frontend together. No migrations. Optional: link external marketing site to `/welcome`.

---

## Final Recommendations

1. Capture desktop/mobile screenshots for control room and landing in release notes.
2. Add E2E test for super_admin forbidden on election create via Playwright/Cypress.
3. Consider countdown interval refresh in control room (`setInterval`) for live timer.
