# Phase 31 — VoteBridge Enterprise Design System & Final Product Polish

**Type:** Frontend design system + UX polish (no backend changes)  
**Date:** June 2025  
**Baseline:** Phase 30 election integrity (`f1c6e49`)

---

## A. Completion Report

Phase 31 establishes a **unified enterprise design system** and applies final product polish across admin dashboards, the strong room, and the public election portal. Work is **frontend-only**: no new APIs, models, or business logic.

### Deliverables

| Area | Outcome |
|------|---------|
| Design tokens | `designTokens.js`, Tailwind forest-green brand palette, `main.css` utility classes |
| Election-first admin | `ElectionContextBanner` on admin dashboard — phase, countdown, health, next action |
| Strong room vault UX | Dark vault shell, custody/integrity emphasis, refined election vault view |
| Public portal | Landing + portal content aligned to design tokens |
| Component consistency | `ElectionCard`, `IntegrityStatusCard`, portal panels use shared classes |
| Documentation | This document |

### Verification

| Command | Result |
|---------|--------|
| `python manage.py check` | ✅ Pass |
| `python manage.py test` | ✅ Pass |
| `npm run build` | ✅ Pass |

---

## B. Architecture Compliance

- **No backend changes** — Views → Services → Repositories → Models unchanged.
- **No new REST endpoints** — Public portal reuses `GET /elections/public/portal/`.
- **Election integrity preserved** — No vote totals, rankings, or winners exposed while elections are open.
- **Business logic in services only** — All changes are Vue/CSS presentation layer.

---

## C. Database Changes

None.

---

## D. APIs

None added or modified.

---

## E. Vue Components

### New

| Component | Path | Purpose |
|-----------|------|---------|
| `ElectionContextBanner` | `components/elections/ElectionContextBanner.vue` | Election-first hero — status, countdown, health, CTA |
| `useElectionCountdown` | `composables/useElectionCountdown.js` | Shared live countdown for election dates |

### Updated

| Component / View | Changes |
|------------------|---------|
| `AdminDashboardView` | Election context banner, `PageHeader`, `vb-page` spacing |
| `StrongroomDashboardView` | Vault shell, principles grid, table shell |
| `StrongroomElectionView` | Vault panels, breadcrumbs, audit history styling |
| `StrongroomWorkspaceLayout` | Vault workspace header |
| `LandingView` | Portal hero, surface panels, FAQ/support sections |
| `PublicElectionPortalContent` | `LoadingSkeleton`, `vb-surface-panel`, section titles |
| `ElectionWorkspaceOverview` | `vb-election-hero` |
| `ElectionCard` | `StatusBadge`, `vb-surface-panel` |
| `IntegrityStatusCard` | Vault dark styling with semantic score colours |
| `SuperAdminDashboardView` | `vb-page` spacing |

### Design token files

| File | Role |
|------|------|
| `frontend/tailwind.config.cjs` | Forest green brand palette (`#1E5F46`) |
| `frontend/src/vue/config/designTokens.js` | JS export of colours, typography, spacing |
| `frontend/src/vue/assets/styles/main.css` | `vb-*` utility classes |

---

## F. Security Impact

- **No security regression** — presentation-only changes.
- Strong room vault styling reinforces restricted-workspace mental model without changing permissions (Super Admin only for write operations).
- Public portal continues to hide sensitive data during open elections.

---

## G. Performance Impact

- Minimal — one additional countdown interval per banner instance (same pattern as public portal).
- No new API calls; existing dashboard/portal fetches unchanged.
- CSS utilities compiled at build time; no runtime token overhead.

---

## H. Responsive Design Notes

- `ElectionContextBanner` stacks countdown and actions on mobile; side-by-side on `lg+`.
- Strong room list items use column layout on small screens, row on `sm+`.
- Landing portal hero and candidate grid remain single-column on mobile, multi-column from `md`/`sm` breakpoints.
- All interactive targets maintain `min-h-touch` (44px) via `VButton`.

---

## I. Testing Strategy

| Layer | Approach |
|-------|----------|
| Backend | Full test suite (`python manage.py test --keepdb`) — confirms no accidental backend edits |
| Build | `npm run build` — Tailwind token changes compile cleanly |
| Manual | Admin dashboard with open election; strong room vault; `/welcome` and `/observe` portal |
| Accessibility | Focus rings preserved (`:focus-visible`); ARIA on vault status cards; breadcrumb nav on strong room election view |

---

## J. Deployment Notes

- Deploy frontend build only; no migrations required.
- Brand colour shift (blue → forest green) applies globally via Tailwind — clear browser cache/CDN after deploy if styles appear stale.
- No environment variable changes.

---

## Design Principles

1. **Election-first** — Active election context precedes generic metrics on admin surfaces.
2. **Trust through restraint** — Strong room uses dark, minimal vault aesthetic; no decorative gradients.
3. **Flat professional colour** — Forest green primary, semantic success/warning/danger/info tokens.
4. **Whitespace and hierarchy** — 32px section spacing, 24px card padding, clear typographic scale.
5. **Reuse before create** — Extend `VButton`, `VCard`, `StatusBadge`, `PageHeader`, `EmptyState`, `LoadingSkeleton`.

---

## Color Palette

| Role | Token | Hex |
|------|-------|-----|
| Primary | `brand-600` | `#1E5F46` |
| Primary hover | `brand-hover` | `#184C38` |
| Background | `surface-muted` | `#F5F7F9` |
| Surface | `surface` | `#FFFFFF` |
| Border | `border` | `#E2E8F0` |
| Success | `success-600` | `#2E7D32` |
| Warning | `warning-600` | `#CA8A04` |
| Danger | `danger-600` | `#C62828` |
| Information | `info-600` | `#0F766E` |

### Status badge variants

| Status | Variant |
|--------|---------|
| Draft | grey (`draft`) |
| Scheduled | blue-grey (`scheduled`) |
| Open | green (`open`) |
| Paused | amber (`paused`) |
| Closed | red (`closed`) |
| Archived | dark grey (`archived`) |

---

## Typography Scale

| Use | Class / token |
|-----|----------------|
| Page title | `vb-page-title` / `text-2xl font-semibold text-slate-800` |
| Section title | `vb-section-title` / `text-lg font-semibold text-slate-900` |
| Card title | `text-base font-semibold text-slate-800` |
| Body | `text-sm text-slate-600` |
| Caption | `vb-caption` / `text-xs text-slate-500` |
| Label | `vb-label` / `text-sm font-medium text-slate-800` |

**Font:** Inter Variable, weights 400–700.

---

## Component Standards

### Buttons (`VButton`)

- Variants: `primary`, `secondary`, `danger`, `ghost`
- Sizes: `sm`, `md`, `lg`
- Min height 44px; `rounded-input` (10px)

### Forms (`VInput`, `vb-input`)

- Height 48px; border `border`; focus ring `brand-600`

### Cards (`VCard`, `vb-card`, `vb-surface-panel`)

- Radius 12px (`rounded-card`); padding 24px (`p-card`); soft shadow (`shadow-card`)

### Tables (`VTable`, `vb-table-shell`)

- White surface, ring border; card layout on mobile via existing responsive patterns

### Alerts (`VAlert`)

- Semantic backgrounds: success, error, warning, info — 10px radius

### Empty / loading

- `EmptyState` — dashed border, centred icon, action slot
- `LoadingSkeleton` — variants: `stats`, `card`, `list`

### Modals / toasts

- `VModal`, `ConfirmDialog`, `ToastContainer` — unchanged; copy from `toastMessages.js`

### Spacing utilities

| Token | Value | Class |
|-------|-------|-------|
| Page padding | 32px | `px-page` |
| Section gap | 32px | `space-y-section`, `vb-page` |
| Card padding | 24px | `p-card` |
| Input/button gap | 16px | `gap-button-gap` |

### Shadows & radius

- Card shadow: `shadow-card`
- Input/button radius: `rounded-input` (10px)
- Card radius: `rounded-card` (12px)

### Layout utilities (new)

| Class | Use |
|-------|-----|
| `vb-page` | Standard page vertical rhythm |
| `vb-election-hero` | Active election banner (admin/workspace) |
| `vb-portal-hero` | Public landing hero |
| `vb-surface-panel` | Standard content panel |
| `vb-vault-shell` | Strong room outer vault |
| `vb-vault-panel` | Strong room inner panel |
| `vb-table-shell` | List/table container |

---

## Accessibility Considerations

- `:focus-visible` ring on all interactive elements (`ring-brand-600`, 2px offset)
- ARIA labels on integrity score cards and strong room navigation
- Breadcrumb navigation on strong room election detail
- WCAG AA contrast: brand green on white; vault text uses `slate-100`/`slate-200` on `slate-900`
- Touch targets ≥ 44px on buttons
- OTP/login screens unchanged — no role labels exposed

---

## UI Consistency Checklist

Use this checklist when adding or reviewing pages:

- [ ] Page uses `vb-page` or `space-y-section` for vertical rhythm
- [ ] Page header uses `PageHeader` with title + optional actions
- [ ] Loading state: `LoadingSkeleton` or `VTable :loading`
- [ ] Empty state: `EmptyState` with preset from `emptyStates.js`
- [ ] Error state: `VAlert variant="error"`
- [ ] Status uses `StatusBadge` / `VBadge` — not ad-hoc colour classes
- [ ] Buttons use `VButton` variants — not raw `<button>` with custom colours
- [ ] Cards use `VCard` or `vb-surface-panel` — consistent radius and shadow
- [ ] No gradients (flat colours only)
- [ ] Forest green brand tokens — not legacy blue hex
- [ ] Mobile layout tested — tables collapse, heroes stack
- [ ] Focus rings visible on keyboard navigation
- [ ] Open elections: no vote totals or rankings in UI/API

---

## Seed Data

No changes.
