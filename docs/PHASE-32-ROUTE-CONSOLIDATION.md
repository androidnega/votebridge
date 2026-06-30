# Phase 32 — Route & Navigation Consolidation

**Type:** Frontend routing + navigation standardization (no backend changes)  
**Date:** June 2026  
**Baseline:** Phase 31 design system polish

---

## A. Completion Report

Phase 32 standardizes VoteBridge routing around a **universal authenticated dashboard** at `/dashboard` and a clear **public surface** at `/`, `/observe`, and `/auth/*`. All roles share one post-login destination; dashboard content renders dynamically via `DashboardHubView`.

### Deliverables

| Area | Outcome |
|------|---------|
| Universal dashboard | Single route `/dashboard` — role views via `DashboardHubView` |
| Authenticated namespace | All app routes live under `/dashboard/*` |
| Public routes | `/`, `/observe`, `/auth/login`, `/auth/forgot-password`, `/auth/reset-password` |
| Legacy compatibility | `legacyRedirects.js` maps old top-level paths to `/dashboard/*` |
| Navigation | Sidebar, module nav, breadcrumbs, guards, auth redirects updated |
| Auth flow | OTP/biometric/login always normalize to `/dashboard` |
| Documentation | This document |

### Verification

| Command | Result |
|---------|--------|
| `npm run build` | Pass |
| `python manage.py check` | Not run — Django venv unavailable in shell |
| `python manage.py test` | Not run — Django venv unavailable in shell |

Manual checks:

- Authenticated users redirect to `/dashboard` after login
- `/welcome` redirects to `/`
- Legacy paths (e.g. `/elections`, `/results`) redirect to `/dashboard/...`
- Public `/observe` remains accessible without auth
- Role meta on routes unchanged — permission checks preserved

---

## B. Architecture Compliance

- **No backend changes** — Views → Services → Repositories → Models unchanged
- **No business logic in Vue** — routing/presentation only
- **Permission checks preserved** — route `meta.roles` and guards unchanged
- **Election integrity preserved** — no API or results exposure changes
- **Frontend normalizes `redirect_path`** — backend role paths overridden to `/dashboard` without service changes

---

## C. Database Changes

None.

---

## D. APIs

None added or modified.

---

## E. Vue Components

### New

| File | Purpose |
|------|---------|
| `config/routes.js` | Canonical paths + `normalizeAuthRedirect()` |
| `router/legacyRedirects.js` | Backward-compatible redirects |
| `views/auth/ForgotPasswordView.vue` | Public forgot-password screen |
| `views/auth/ResetPasswordView.vue` | Public reset-password screen |

### Updated

| Area | Changes |
|------|---------|
| `router/index.js` | `/dashboard` authenticated tree; `/` landing; election workspace at `/dashboard/elections/:uuid` |
| `router/guards.js` | Guest redirect → `/dashboard`; public routes unchanged |
| `stores/auth.js` | Default + normalized post-login redirect |
| `config/sidebarNav.js` | All links under `/dashboard` |
| `config/electionWorkspaceNav.js` | Election tabs under `/dashboard/elections/:uuid` |
| `layouts/ElectionLayout.vue` | Breadcrumbs + student tabs use dashboard paths |
| `layouts/PublicLayout.vue` | FAQ, Support, Observer, Login nav |
| `views/public/LandingView.vue` | `#faq`, `#support` anchors; public nav links |
| Auth views | OTP/biometric redirect normalization |
| 50+ views/components | Breadcrumbs and `router.push` paths updated |

### Removed routes

| Route | Replacement |
|-------|-------------|
| `/dashboard/student` | `/dashboard` (dynamic student view) |
| `/dashboard/admin` | `/dashboard` (dynamic admin view) |
| `/dashboard/super-admin` | `/dashboard` (dynamic super-admin view) |
| `/welcome` | `/` (router redirect) |

---

## F. Security Impact

- **Positive:** Clear separation of public vs authenticated URL spaces
- **Unchanged:** Route `meta.roles` enforcement in guards
- **Auth redirect normalization** prevents role-specific URL leakage after login
- **Public observer** remains read-only with no auth bypass

---

## G. Performance Impact

Negligible — additional legacy redirect routes are static path matches evaluated once per navigation.

---

## H. Responsive Design Notes

No layout changes. Public landing nav hides FAQ/Support labels on very small screens (same pattern as observer link).

---

## I. Testing Strategy

| Layer | Approach |
|-------|----------|
| Build | `npm run build` |
| Backend | `python manage.py check && python manage.py test` (when venv available) |
| Manual | Login as student/admin/super_admin → land on `/dashboard` |
| Manual | Visit legacy URLs → confirm redirect to `/dashboard/*` |
| Manual | Public `/`, `/observe`, `/auth/login` without session |
| Regression | Role-restricted routes (strong room, settings) still 403 for wrong role |

---

## J. Deployment Notes

Deploy frontend bundle only. No migrations or backend deploy required.

- Update bookmarks/docs referencing `/welcome` → `/`
- External links to `/elections` continue working via legacy redirects
- Optional: configure CDN/server 301 from `/welcome` to `/` for non-SPA crawlers

---

## Route map — before

### Public

| Path | Purpose |
|------|---------|
| `/welcome` | Landing |
| `/observe` | Observer portal |
| `/auth/login` | Login |
| `/verify` | Results verification |

### Authenticated (mixed root)

| Path | Purpose |
|------|---------|
| `/` | Role hub (auth required) |
| `/dashboard/student` | Student dashboard |
| `/dashboard/admin` | Admin dashboard |
| `/dashboard/super-admin` | Super-admin dashboard |
| `/elections`, `/results`, `/settings`, … | Top-level app routes |
| `/elections/:uuid/*` | Election workspace |

---

## Route map — after

### Public

| Path | Purpose |
|------|---------|
| `/` | Landing (FAQ, Support, Login, Observer links) |
| `/observe` | Observer portal (direct URL or from landing) |
| `/auth/login` | Login |
| `/auth/forgot-password` | Forgot password |
| `/auth/reset-password` | Reset password |
| `/verify` | Public verification (unchanged) |
| `/maintenance` | Maintenance page (unchanged) |

### Authenticated (`/dashboard/*`)

| Path | Purpose |
|------|---------|
| `/dashboard` | Universal dashboard (role-dynamic) |
| `/dashboard/elections` | Election list |
| `/dashboard/elections/create` | Create election |
| `/dashboard/elections/:uuid/*` | Election workspace |
| `/dashboard/results/*` | Results hub |
| `/dashboard/reports/*` | Reports & analytics |
| `/dashboard/strongroom/*` | Strong room |
| `/dashboard/settings/*` | Settings |
| `/dashboard/profile` | Profile |
| `/dashboard/notifications` | Notifications |
| `/dashboard/operations/*` | Operations (super admin) |
| `/dashboard/communications/*` | Communications |
| `/dashboard/ussd/*` | USSD |
| `/dashboard/forbidden` | Access denied |
| `/dashboard/error` | Server error |

---

## Redirect strategy

1. **Router legacy table** (`legacyRedirects.js`) — maps `/elections`, `/results`, `/settings`, etc. to `/dashboard/...`
2. **Role dashboard aliases** — `/dashboard/student|admin|super-admin` → `/dashboard`
3. **Welcome alias** — `/welcome` → `/`
4. **Auth normalization** — `normalizeAuthRedirect()` forces `/dashboard` for backend `redirect_path` and legacy `/` targets
5. **Guest guard** — authenticated users hitting `/auth/login` → `/dashboard`

All redirects are client-side (Vue Router). No HTTP 301 from Django — acceptable for SPA; add server rules if SEO requires.

---

## Authentication flow (after)

```
Landing (/)
  → Login (/auth/login)
  → OTP (/auth/otp)
  → Trusted device / risk check (backend)
  → Biometric (/auth/biometric-verify) if required
  → /dashboard (all roles)
```
