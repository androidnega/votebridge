# Phase 32.1 — Public Experience Simplification

**Type:** Frontend public UX (no backend changes)  
**Date:** June 2026  
**Baseline:** Phase 32 route consolidation (`0ef4abf`)

---

## A. Completion Report

Phase 32.1 reduces VoteBridge's public surface to a **single landing page** at `/` and applies a consistent **100vh boxed layout** to authentication screens. The Observer Portal is **excluded from v1.0** but preserved for a future release.

### Deliverables

| Area | Outcome |
|------|---------|
| Observer portal | Route removed; `/observe` redirects to `/`; implementation kept in `observerRoutes.v2.js` |
| Landing page | Single viewport, no scroll — branding, election status, countdown, sign-in, support |
| Auth layout | Same boxed, centered, 100vh philosophy as landing |
| Shared branding | `PublicBrandHeader` component for TTU + VoteBridge identity |
| CSS utilities | `vb-public-screen`, `vb-public-frame`, `vb-public-card` |
| Documentation | This document |

### Verification

| Command | Result |
|---------|--------|
| `npm run build` | Pass |
| `python manage.py check` | Not run — Django venv unavailable in shell |
| `python manage.py test` | Not run — Django venv unavailable in shell |

---

## B. Architecture Compliance

- **No backend changes** — Views → Services → Repositories → Models unchanged
- **No authentication logic changes** — login, OTP, biometric flows untouched
- **Election data** — landing reuses existing `GET /elections/public/portal/` via `useElectionPortal`
- **Election integrity preserved** — no vote totals or rankings added to public UI

---

## C. Database Changes

None.

---

## D. APIs

None added or modified.

---

## E. Vue Components

### New

| Component | Purpose |
|-----------|---------|
| `PublicBrandHeader.vue` | TTU logo, institution name, VoteBridge title |
| `router/observerRoutes.v2.js` | Deferred observer routes for future release |

### Updated

| File | Changes |
|------|---------|
| `LandingView.vue` | Minimal 100vh card — status, countdown, sign-in, support |
| `PublicLayout.vue` | Full-screen centered shell, no marketing nav/footer |
| `AuthLayout.vue` | Unified boxed 100vh layout (login, OTP, forgot/reset, info) |
| `router/index.js` | Observer route removed with v2 comment |
| `legacyRedirects.js` | `/observe` → `/` |
| `main.css` | Public experience utility classes |

### Preserved (not routed in v1.0)

| File | Notes |
|------|-------|
| `ObserverPortalView.vue` | Full implementation retained |
| `ObserverLayout.vue` | Layout retained |
| Observer CSS utilities | Retained in `main.css` |

---

## F. Security Impact

None. Public portal API exposure unchanged. Observer portal simply not linked or routed in v1.0.

---

## G. Performance Impact

Positive — landing page bundle smaller (removed `PublicElectionPortalContent`, FAQ, feature grids).

---

## H. Responsive Design Notes

- **Desktop (1280×720+):** Single viewport, no vertical scroll
- **Mobile:** `h-screen` + `overflow-hidden` on shell; content scales within card (`max-w-md` / `max-w-content`)
- Auth forms remain usable on small screens; info pages use slightly wider card (`max-w-lg`)

---

## I. Testing Strategy

| Check | Method |
|-------|--------|
| Build | `npm run build` |
| Landing viewport | Manual — `/` at 1440×900, no page scroll |
| Auth viewport | Manual — `/auth/login`, same layout |
| Observer removed | `/observe` redirects to `/`; no nav links |
| Backend | `python manage.py check && python manage.py test` when venv available |

---

## J. Deployment Notes

Frontend-only deploy. No migrations.

To **re-enable Observer Portal** in a future release:

1. Import and spread `observerRoutesV2` from `router/observerRoutes.v2.js` into `router/index.js`
2. Remove `/observe` entries from `legacyRedirects.js`
3. Restore navigation links if desired

---

## Public routing (v1.0)

| Path | Purpose |
|------|---------|
| `/` | Landing — election status + sign-in |
| `/auth/login` | Sign in |
| `/auth/forgot-password` | Forgot password |
| `/auth/reset-password` | Reset password |
| `/auth/otp` | OTP verification |
| `/auth/biometric-verify` | Biometric step |
| `/verify` | Public results verification (unchanged) |
| `/maintenance` | Maintenance page (unchanged) |
| `/observe` | Redirects to `/` (v1.0) |

---

## Homepage redesign

### Removed

- Observer portal link
- FAQ / feature grids
- `PublicElectionPortalContent` sections (timeline, announcements, candidates)
- Marketing hero with multiple CTAs
- Verify results link from landing
- Public header/footer chrome

### Displayed

1. TTU logo + institution name  
2. VoteBridge title + tagline  
3. Current election title  
4. Phase status (with live indicator when voting is open)  
5. Countdown clock when applicable  
6. **Sign in to vote** (primary)  
7. **Help & support** (mailto election office)

### Layout

- **Shell:** `vb-public-screen` — `h-screen overflow-hidden`
- **Frame:** `vb-public-frame` — centered, `max-w-content` (1280px)
- **Card:** `vb-public-card` — bordered white panel, generous padding

---

## Layout guidelines (auth + public)

| Token | Value |
|-------|--------|
| Viewport | 100vh, no document scroll |
| Max frame width | 1280px (`max-w-content`) |
| Card width | ~448px login (`max-w-md`), ~512px info (`max-w-lg`) |
| Background | `surface-muted` |
| Card | White, `border-border`, `rounded-card`, soft shadow |
| Primary action | Full-width brand button |
| Support | Text link below card (auth) or inside card (landing) |

---

## UX rationale

1. **Single public entry** — voters and staff share one clear front door at `/`
2. **Election-first** — status and countdown answer “is voting open?” immediately
3. **No scroll on desktop** — reduces cognitive load; feels like an official kiosk/portal
4. **Observer deferred** — v1.0 focuses on voting workflow; observer feed can return when requirements are finalized
5. **Auth consistency** — same boxed layout builds trust and matches landing visual language
