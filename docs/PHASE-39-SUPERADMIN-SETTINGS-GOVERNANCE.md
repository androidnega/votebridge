# Phase 39 — Super Admin Settings Governance Alignment

**Type:** Governance UX refinement  
**Date:** June 2026  
**Scope:** Super Admin Settings module — platform administration, not election administration

---

## A. Completion Report

Phase 39 realigns the Super Admin Settings experience with the responsibilities of a **Platform Administrator**. Election configuration remains with Election Administrators; Settings focuses on governance, infrastructure, integrations, security, and administration.

### Delivered

| Area | Status |
|------|--------|
| Platform status shows **Current Platform State** (no election names) | ✅ |
| **Elections & Policies** renamed to **Platform Defaults** | ✅ |
| Election-specific config removed from Super Admin settings UI | ✅ |
| **Election Administration** section (manage admins, not elections) | ✅ |
| **Integrations** section (SMS, USSD, email, Redis, WebSockets) | ✅ |
| **Strong Room Configuration** hub (policies only — no vault access) | ✅ |
| **Administrative activity** feed on Settings overview | ✅ |
| Quick actions updated (maintenance, validate gateways, backup, audit, operations) | ✅ |
| Institution, branding, auth, security, maintenance, backup, etc. preserved | ✅ |
| Grouped cards, two-level navigation, no new tabs | ✅ |
| `npm run build` | ✅ |

### Governance philosophy

- **Super Admin** governs the **platform**: infrastructure, integrations, defaults, administrator accounts, vault *policies*.
- **Election Administrator** governs **elections**: voting windows, eligibility, candidates, schedules, per-election channels.
- Settings copy and navigation reinforce **separation of duties** — Super Admin must not appear to configure individual elections.

---

## B. Architecture Compliance

| Layer | Changes |
|-------|---------|
| Views | Settings overview, hub views, new section pages — presentation only |
| Composables | `useSettingsIntegrations`, `useElectionAdministrators` |
| Services | `SystemOverviewService` — platform state, admin activity, integrations snapshot (read-only aggregation) |
| Repositories / Models | Unchanged |

Data flow preserved: **Views → Composables/Stores → API → Services → Repositories → Models**

No business logic added to API views.

---

## C. Database Changes

None.

New platform default key `election_policies.default_timezone` is seeded via `ensure_defaults()` when the settings service runs — no migration required.

---

## D. APIs

### Modified (response shape only)

| Endpoint | Change |
|----------|--------|
| `GET /api/v1/system/overview/` | Replaces `active_election` (title) with `platform_state`, adds `admin_activity`, `integrations`, expanded `quick_actions` |

### Reused (unchanged)

| Purpose | Endpoint |
|---------|----------|
| Platform defaults | `GET/PATCH /api/v1/system/settings/{category}/` |
| Providers | `GET /api/v1/system/providers/`, `POST .../test/` |
| USSD integration health | `GET /api/v1/ussd/integration/` |
| Election administrators | `GET/POST /api/v1/accounts/users/`, activate/deactivate/unverify |
| Audit export / logs | `GET /api/v1/security/monitoring/audit-logs/`, `/dashboard/platform/logs` |

---

## E. Vue Components & Routes

### Settings overview (`SystemControlOverviewView`)

- Platform status banner with **Current platform state** (primary + secondary lines)
- Infrastructure health tiles (unchanged services)
- Grouped configuration cards (8 sections)
- Administrative activity sidebar feed
- Updated quick actions

### New / updated routes

| Route | View |
|-------|------|
| `/dashboard/settings/platform-defaults` | `PlatformDefaultsView` |
| `/dashboard/settings/integrations` | `SystemIntegrationsView` |
| `/dashboard/settings/election-administration` | `SettingsElectionAdministrationView` |
| `/dashboard/settings/strongroom-config` | `SettingsStrongroomConfigView` |
| `/dashboard/settings/election-policies` | Redirect → platform defaults |
| `/dashboard/settings/sms`, `/email`, `/license`, `/about` | Aliases to existing system-control views |

### Navigation (`settingsNav`)

Overview · Institution · **Integrations** · Security · Advanced

(Voting hub redirects to Integrations.)

### Config

- `systemControlHub.js` — section groups, quick action routes
- `platformDefaults.js` — allowed default keys (hides per-election policy keys)

---

## F. Security Impact

- Overview no longer exposes **active election titles** to Super Admin settings (reduces operational leakage).
- Election administrator management uses existing `CanManageUsers` permissions.
- Platform activity feed filters `admin_action` logs with `subsystem: system_control` and no election context.
- Step-up verification unchanged for sensitive settings saves.

---

## G. Performance Impact

- Overview adds one bounded audit query (max 50 rows, returns ≤8 items) — negligible.
- Integrations page reuses cached health checks via existing operations health service.
- No additional polling or WebSocket payloads.

---

## H. Responsive Design Notes

- Settings overview: single column on mobile; configuration cards stack; sidebar (quick actions, activity) flows below main content on `xl` breakpoint.
- Integrations: 1-column cards on mobile, 2-column on `lg`.
- Election administration table uses existing `VTable` mobile card layout.
- Touch targets ≥44px on quick action buttons.

---

## I. Testing Strategy

| Command | Result |
|---------|--------|
| `python manage.py check` | Run in Django environment |
| `python manage.py test apps.system.tests --noinput` | Extended overview assertions |
| `python manage.py test --noinput` | Full suite in CI |
| `npm run build` | ✅ Pass |

Manual verification:

- Settings overview shows platform state, not election name
- Platform defaults excludes voting windows / eligibility fields
- Election administration lists `admin` role users
- Integrations validate connection reuses provider test + USSD health
- Strong room config links do not open vault
- Quick actions route correctly

---

## J. Deployment Notes

- No migrations to apply.
- Deploy frontend + backend together so overview JSON matches UI expectations.
- Legacy bookmarks to `/dashboard/settings/election-policies` redirect to platform defaults.
- Run settings default seed if `default_timezone` should appear immediately.

---

## Separation of duties summary

| Super Admin Settings | Election Administrator workspace |
|---------------------|----------------------------------|
| Platform defaults | Voting windows & schedules |
| Integrations & infrastructure | Channel configuration per election |
| Election admin accounts | Candidates & eligibility |
| Strong room *policies* | Committee nomination per election |
| Maintenance & backups | Election lifecycle |
