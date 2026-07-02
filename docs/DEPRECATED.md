# Deprecated Components & Routes — VoteBridge v1.0 RC1

Items listed here are **not used by the Vue SPA** but may remain for backward compatibility. Do not build new features on deprecated surfaces.

## Removed in Phase 27 (orphan Vue files)

| File | Replacement |
|------|-------------|
| `HomeView.vue` | `DashboardHubView.vue` |
| `election-management/*` | Election workspace (`/elections/:uuid/*`) |
| `DeliveryLogsView.vue` | `PlatformLogsView.vue` (communications tab) |
| `OperationsLogsView.vue` | `PlatformLogsView.vue` (operations tab) |
| `ActivityLogsView.vue` | `PlatformLogsView.vue` (USSD tab) |
| `StrongroomEvidenceExportView.vue` | Contextual actions on `StrongroomElectionView.vue` |

## Legacy Django template pages

Routes under `/dashboard/*` and `/auth/login/` (HTML) are **deprecated**. The Vue SPA at `/` is the supported interface.

| Legacy path | Vue equivalent |
|-------------|----------------|
| `/dashboard/elections/` | `/elections` |
| `/dashboard/elections/<uuid>/vote/` | `/elections/<uuid>/vote` |
| `/dashboard/security/` | `/strongroom/investigations/security` |

Block or redirect these in production Nginx if not needed.

## Removed legacy API login endpoints

`auth/student/login/`, `auth/admin/login/`, and `auth/super-admin/login/` were removed. Use unified `POST /api/v1/accounts/auth/login/` only.

## Legacy frontend redirects (kept)

| Path | Redirects to |
|------|--------------|
| `/election-management/*` | `/elections` |
| `/analytics` | `/reports` |
| `/system-control/*` | `/settings/*` |
| `/security`, `/fraud` | Strong room investigations |
