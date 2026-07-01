# Phase 50 — VoteBridge Light Theme Redesign

## A. Completion Report

Phase 50 replaces the dark navy application shell with a light, institutional theme suitable for university and electoral commission use. All dashboard routes continue to use `DashboardLayout` → `AppShell`; navigation structure is unchanged. Visual tokens are centralized in Tailwind (`shell.*`, updated `ink.*`, `surface-muted`).

## B. Architecture Compliance

- **No backend, route, or API changes.**
- Shell styling lives in `AppShell`, navigation components, and shared CSS/Tailwind tokens.
- Page content components inherit the shell automatically via `DashboardLayout`.

## C. Database Changes

None.

## D. APIs

None.

## E. Vue Components

| Component | Change |
|-----------|--------|
| `AppShell.vue` | Light sidebar frame, soft mobile backdrop, institutional brand block |
| `AppSidebar.vue` | Light nav items, 4px green active indicator, increased group spacing |
| `AppTopbar.vue` | White header, light icon buttons, green Super Admin pill |
| `GlobalSearch.vue` | Gray search field on white header |
| `UserMenu.vue` | Light profile trigger and dropdown (removed dark `inverted` mode) |
| `NotificationDropdown.vue` | Minimal dot badge, smaller icon |
| `SuperAdminTopbarActions.vue` | Soft green hover shortcuts |
| `PageHeader.vue` | Typography tokens `#1F2937` / `#6B7280` |
| `ModuleNav.vue` | Green active tab indicator |

## F. Security Impact

None — presentation only.

## G. Performance Impact

Negligible. Same component tree; CSS class changes only. Build verified with `npm run build`.

## H. Responsive Design Notes

- Sidebar remains 280px / 88px collapsed; mobile drawer unchanged.
- Topbar search hidden below `sm`; profile menu compact on smaller widths.
- Touch targets preserved at 44px minimum.

## I. Testing Strategy

- Manual: sign in as Super Admin / Admin / Student — confirm light sidebar, white header, readable nav states.
- `npm run build` — production CSS compiles with new `shell.*` tokens.
- Regression: strongroom vault panels retain intentional dark workspace styling (content module, not global shell).

## J. Deployment Notes

- Frontend rebuild only (`npm run build`).
- No environment variable changes.
- Clear browser cache if stale CSS persists after deploy.

## Design tokens (reference)

| Element | Token / hex |
|---------|-------------|
| Sidebar background | `#F3F4F6` (`shell-sidebar`) |
| Sidebar border | `#E5E7EB` |
| Nav text | `#374151` |
| Nav icon | `#6B7280` |
| Hover / active bg | `#E8F5EE` |
| Active accent | `#166534` |
| Content canvas | `#F9FAFB` |
| Headings | `#1F2937` |
| Descriptions | `#6B7280` |

## Before / after (visual summary)

**Before:** Dark navy sidebar (`#1E293B`), white-on-navy topbar, heavy contrast, cloud-dashboard feel.

**After:** Light gray sidebar, white topbar with soft search field, green active states, institutional civic palette — all pages under `DashboardLayout` inherit the new shell automatically.
