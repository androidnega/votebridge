# Phase 33.1 — Enterprise Color System & Visual Identity

**Type:** Frontend design system (no backend changes)  
**Date:** June 2026  
**Baseline:** Phase 33 Super Admin dashboard (`4fec586`)

---

## A. Completion Report

Phase 33.1 standardises VoteBridge's visual identity around a single **enterprise color system** — institutional green, deep navy chrome, neutral surfaces, and semantic status colours used only for alerts and system health.

### Deliverables

| Area | Outcome |
|------|---------|
| Design tokens | `designTokens.js` + `tailwind.config.cjs` aligned |
| Global styles | `main.css` utilities updated (buttons, cards, forms, topbar, vault, tables) |
| Chrome | Deep navy sidebar and dashboard header |
| KPI cards | Neutral white `StatCard` / `vb-kpi-card` — no coloured accents |
| Charts | Primary green series; neutrals for secondary data |
| Strong room | Navy vault shell retained |
| Documentation | This document |

---

## B. Architecture Compliance

- **UI-only** — no Views → Services → Repositories → Models changes
- **No API changes**
- **No business logic changes**
- Tokens consumed via Tailwind theme + `designTokens.js` for ECharts

---

## C. Database Changes

None.

---

## D. APIs

None.

---

## E. Vue Components

### Token sources

| File | Role |
|------|------|
| `config/designTokens.js` | JS token export (`colors`, `chartColors`, typography) |
| `tailwind.config.cjs` | Tailwind `brand`, `navy`, `ink`, status palettes |
| `assets/styles/main.css` | Component utility classes |

### Updated components

| Component | Changes |
|-----------|---------|
| `StatCard.vue` | White KPI cards; label/value/hint only — no accent badges |
| `VButton.vue` | Secondary = gray border; danger = red outline |
| `VCard.vue` | White + border + soft shadow |
| `VTable.vue` | Light borders; hover rows only |
| `AppShell.vue` | Navy sidebar |
| `AppSidebar.vue` | Navy chrome; green active items |
| `AppTopbar.vue` | Navy header; inverted user menu |
| `UserMenu.vue` | `inverted` prop for dark header |
| `useEChart.js` | Chart palette from `chartColors` |
| `GaugeChart.vue`, `HeatmapChart.vue` | Primary green from tokens |

---

## F. Security Impact

None — cosmetic only.

---

## G. Performance Impact

Negligible — CSS/token changes only.

---

## H. Responsive Design Notes

- Navy header and sidebar unchanged at all breakpoints
- KPI grid and tables remain mobile-first
- Topbar governance shortcuts: icons on `md`, labels on `2xl`

---

## I. Testing Strategy

| Check | Method |
|-------|--------|
| Visual regression | Manual pass: dashboard, sidebar, strong room, auth, reports |
| Build | `npm run build` |
| Contrast | Primary green on white; white on navy — WCAG AA |
| Backend | `python manage.py check` / `test` when venv available |

---

## J. Deployment Notes

Frontend-only deploy. No migrations or env vars.

### Verification

| Command | Result |
|---------|--------|
| `npm run build` | Run at commit |
| `python manage.py check` | Not run — Django venv unavailable in shell |
| `python manage.py test` | Not run — Django venv unavailable in shell |

---

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Primary (brand) | `#1E5F46` | Buttons, active nav, links, primary chart series |
| Primary hover | `#184C38` | Button hover |
| Navy | `#1E293B` | Sidebar, dashboard header, strong room shell |
| Background | `#F8FAFC` | App canvas (`surface-muted`) |
| Surface | `#FFFFFF` | Cards, tables, forms |
| Border | `#E2E8F0` | Cards, inputs, dividers |
| Text primary | `#0F172A` | Headings (`ink-primary`) |
| Text secondary | `#64748B` | Metadata (`ink-secondary`) |
| Success | `#16A34A` | Alerts, badges, health — status only |
| Warning | `#D97706` | Alerts, badges — status only |
| Danger | `#DC2626` | Alerts, validation — status only |
| Information | `#2563EB` | Info alerts — status only |

---

## Usage Guidelines

### Do

- Use `brand-*` for primary actions and active navigation
- Use `navy` for structural chrome (sidebar, topbar, vault)
- Use white cards with `border-border` and `shadow-card`
- Use status colours only for alerts, badges, and health indicators
- Use `chartColors` from `designTokens.js` for ECharts

### Don't

- Gradients, glassmorphism, or neon accents
- Coloured KPI card backgrounds
- Status colours as branding (e.g. green KPI badges)
- Hardcoded hex in new components — use Tailwind tokens

---

## Design Principles

1. **Trust** — restrained palette, consistent chrome
2. **Security** — dark navy for restricted areas (strong room, control room)
3. **Professionalism** — white surfaces, subtle shadows
4. **Simplicity** — large metrics, small captions, minimal icons
5. **Election integrity** — no decorative colour that implies outcomes

---

## Accessibility Notes

- Focus rings: `ring-brand-600` on interactive elements
- Body text: `#0F172A` on `#F8FAFC` — AA compliant
- White text on `#1E293B` navy — AA for UI chrome labels
- Touch targets: `min-h-touch` (44px) preserved
- Status colours paired with text labels, not colour alone

---

## Component Examples

```html
<!-- Primary button -->
<button class="vb-btn-primary">Save changes</button>

<!-- Secondary button -->
<button class="vb-btn-secondary">Cancel</button>

<!-- KPI card -->
<div class="vb-kpi-card">
  <p class="text-sm text-ink-secondary">Open elections</p>
  <p class="text-3xl font-semibold text-ink-primary">3</p>
</div>

<!-- Vault / strong room panel -->
<div class="vb-vault-shell">…</div>
```

---

## Chart Palette

Primary series: `#1E5F46`  
Secondary series: `#64748B`, `#334155`, `#94A3B8`, `#CBD5E1`  
Grid lines: `#E2E8F0` (via ECharts defaults)  
No gradient fills on enterprise dashboards.
