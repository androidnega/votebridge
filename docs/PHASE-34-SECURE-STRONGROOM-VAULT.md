# Phase 34 — Secure Electoral Strong Room Vault

**Type:** Governance, multi-custodian vault access, terminal UX  
**Date:** June 2026  
**Baseline:** Phase 33.1 enterprise color system (`af00bcd`)

---

## A. Completion Report

Phase 34 redesigns the Strong Room from a sidebar module into a **secure electoral vault** accessed only through completed elections via a controlled workflow.

### Delivered

| Area | Status |
|------|--------|
| Strong Room removed from primary sidebar / topbar search | ✅ |
| Committee nomination → Super Admin approval → lock on election open | ✅ |
| Access request with lawful reason before vault entry | ✅ |
| Multi-custodian terminal authentication (individual accounts) | ✅ |
| Session timeout, auto reseal, custody records | ✅ |
| Post-auth evidence sections (no tab-heavy vault nav) | ✅ |
| Route guards block bookmark bypass | ✅ |
| Backend tests (`test_vault.py`) | ✅ |
| Frontend production build | ✅ |

### Governance workflow

```
Before election opens
  Admin → nominate committee + session duration
  Super Admin → approve committee
  Super Admin → activate configuration

Election opens
  → Committee, duration, and config become immutable

After election closed/archived
  Super Admin → access request (reason + justification)
  Super Admin → approve request
  Custodians → sequential terminal authentication
  → Vault opens with countdown
  → Timeout or manual close → reseal + custody record
```

### Verification

| Command | Result |
|---------|--------|
| `python manage.py check` | Run in deployment environment (Django venv required locally) |
| `python manage.py test apps.strongroom.tests.test_vault` | Run in deployment environment |
| `npm run build` | ✅ Pass |

---

## B. Architecture Compliance

Business logic remains in **Services**; repositories access data only; API views are thin.

| Layer | Components |
|-------|------------|
| Models | `StrongroomCommittee`, `StrongroomCommitteeMember`, `VaultAccessRequest`, `VaultSession` |
| Repositories | `vault_repository.py` |
| Services | `vault_committee_service`, `vault_access_service`, `vault_session_service` |
| API | `vault_views.py` |
| Signals | `on_election_pre_save` locks approved committee when election → `open` |

**No changes** to election lifecycle logic, vote casting, or certification services. Vault layer composes existing integrity/dashboard data for evidence display only.

---

## C. Database Changes

Migration: `strongroom/migrations/0002_vault_governance.py`

| Model | Purpose |
|-------|---------|
| `StrongroomCommittee` | Per-election committee config; status `draft` → `pending_approval` → `approved` → `locked` |
| `StrongroomCommitteeMember` | Custodian users with `custodian_order` |
| `VaultAccessRequest` | Access reason, justification, approval workflow |
| `VaultSession` | Multi-custodian auth state, expiry, authenticated custodians JSON |

---

## D. APIs

Base: `/api/v1/strongroom/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `elections/{uuid}/committee/` | Get or configure committee |
| POST | `elections/{uuid}/committee/submit/` | Admin submits for approval |
| POST | `elections/{uuid}/committee/approve/` | Super Admin approves |
| GET/POST | `elections/{uuid}/access-requests/` | List or create access requests |
| POST | `elections/{uuid}/access-requests/{uuid}/review/` | Approve or deny |
| POST | `elections/{uuid}/vault-sessions/` | Start session from approved request |
| GET | `vault-sessions/{uuid}/` | Terminal polling / session status |
| POST | `vault-sessions/{uuid}/authenticate/` | Custodian credential verification |
| POST | `vault-sessions/{uuid}/close/` | Manual close and reseal |

Evidence is included in the active session status payload (`evidence` key) — no separate public export endpoint without an active session.

---

## E. Vue Components

| Component / View | Role |
|------------------|------|
| `ElectionVaultCommitteeView.vue` | Pre-open committee configuration |
| `ElectionVaultAccessView.vue` | Access requests and terminal entry |
| `VaultTerminalView.vue` | Secure terminal authentication |
| `VaultEvidenceView.vue` | Post-auth evidence sections |
| `ResultDetailView.vue` | “Open electoral vault” entry for closed elections |

**Navigation**

- Removed from `sidebarNav.js`, `SuperAdminTopbarActions.vue`, `GlobalSearch.vue`
- Election workspace tabs: **Strong room committee** (draft/scheduled), **Vault access** (closed/archived)
- Legacy `/dashboard/strongroom/*` routes redirect to results or election vault access

**Store:** `strongroom.js` extended with committee, access request, and vault session actions.

**Router guard:** `requiresVaultSession` / `requiresActiveVault` in `guards.js`.

---

## F. Security Impact

| Control | Implementation |
|---------|----------------|
| No shared vault password | Each custodian uses own account + password (+ existing MFA policies) |
| Sequential multi-custodian auth | `vault_session_service.authenticate_custodian` enforces order |
| No direct vault URLs | Route guard validates session; inactive sessions redirect |
| Committee lock on open | Signal + service validation |
| Audit trail | Custody actions for committee, requests, auth, open, reseal |
| Election integrity | No vote totals/rankings exposed during `open` elections (unchanged) |

Custody actions: `committee_submitted`, `committee_approved`, `committee_locked`, `vault_access_requested`, `vault_access_approved`, `vault_access_denied`, `vault_session_initiated`, `vault_custodian_verified`, `vault_access_denied`, `vault_opened`, `vault_resealed`.

---

## G. Performance Impact

- Vault session polling: 30s interval on terminal and evidence views
- Evidence package reuses existing integrity dashboard aggregation (no duplicate vote queries)
- Lazy-loaded vault route chunks in production build

---

## H. Responsive Design Notes

- Terminal view: full-width card, monospaced inputs, 44px touch targets on authenticate button
- Evidence sections: horizontal scrollable section chips on mobile; single active panel
- Committee member picker: scrollable checkbox list with max height

Terminal styling: `vb-vault-terminal`, `vb-vault-terminal-input`, blinking cursor animation in `main.css`.

---

## I. Testing Strategy

### Backend (`apps/strongroom/tests/test_vault.py`)

- Committee configure → submit → approve
- Committee locks when election opens
- Access request on closed election
- Sequential two-custodian authentication → `access_granted`
- Wrong password → authentication error

### Frontend

- `npm run build` — route chunks for vault views compile
- Manual: closed election → results → vault access → terminal → evidence → timeout reseal

### Regression

- Existing strongroom integrity APIs unchanged
- Investigation routes moved to `/dashboard/investigations/*` (legacy strongroom URLs redirect)

---

## J. Deployment Notes

1. Run migration: `python manage.py migrate strongroom`
2. No new environment variables
3. Super Admin permissions required for vault operations (`CanManageStrongroom`)
4. After deploy: verify Strong Room absent from sidebar; configure committee on a scheduled demo election; complete lifecycle and test vault access on closed election

---

## Access reasons

| Code | Label |
|------|-------|
| `court_order` | Court Order |
| `candidate_appeal` | Candidate Appeal |
| `electoral_commission_review` | Electoral Commission Review |
| `internal_audit` | Internal Audit |
| `integrity_verification` | Integrity Verification |

---

## Terminal states

`waiting_for_custodian_N`, `access_granted`, `access_denied`, `vault_resealed`, `session_expired` — returned as `terminal_state` on session payloads for UI display.
