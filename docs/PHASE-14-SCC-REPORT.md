# Phase 14 — Enterprise System Control Center (SCC)

**Date:** June 2025  
**Scope:** Super Admin–only platform configuration module. No duplicate business logic. Reuses audit, OTP, operations health, and communication services.

---

## A. Backend Completion Report

| Area | Status | Notes |
|------|--------|-------|
| App scaffold | ✅ | `backend/apps/system/` |
| Database models | ✅ | Institution, settings, revisions, feature flags, maintenance, backups |
| Settings service | ✅ | Versioned key-value store with rollback revisions |
| Step-up auth | ✅ | OTP challenge via existing `OTPService` + cache token (5 min) |
| Maintenance middleware | ✅ | Blocks non–Super Admin API when maintenance enabled |
| Provider management | ✅ | Wraps `CommunicationProvider` + `communication_service.test_provider` |
| Backup service | ✅ | JSON config snapshot backups to `backend/backups/` |
| Storage service | ✅ | Disk/media/logs/DB usage via `psutil` + PostgreSQL |
| Environment service | ✅ | Read-only runtime info |
| REST API | ✅ | 18 endpoints under `/api/v1/system/` |
| Seed migration | ✅ | Default settings, feature flags, institution profile |
| Tests | ✅ | 4 tests — access control, public branding, settings seed |
| Django check | ✅ | No issues |

---

## B. Frontend Completion Report

| Area | Status | Notes |
|------|--------|-------|
| API client | ✅ | `api/systemControl.js` |
| Pinia store | ✅ | `stores/systemControl.js` with step-up token state |
| Step-up UX | ✅ | `useStepUp` composable + `StepUpModal` (VModal + OTP) |
| Module nav | ✅ | `systemControlNav` (21 items) |
| Sidebar | ✅ | System Control group (Super Admin only) |
| Router | ✅ | 21 lazy routes under `/system-control/*` |
| Views | ✅ | Overview, institution, branding, category settings, providers, flags, maintenance, storage, backup, environment, runtime, license, about |
| Build | ✅ | `npm run build` passes |

---

## C. Database Changes

**New app:** `apps.system`

| Model | Table | Purpose |
|-------|-------|---------|
| `InstitutionProfile` | `system_institution_profile` | Institution identity, branding JSON, contacts |
| `SystemSetting` | `system_setting` | Versioned configuration key-value |
| `SettingRevision` | `system_setting_revision` | Audit trail + rollback support |
| `FeatureFlag` | `system_feature_flag` | Module toggles |
| `MaintenanceState` | `system_maintenance_state` | Maintenance / emergency controls |
| `BackupRecord` | `system_backup_record` | Backup job metadata |

**Migrations:**

- `system/0001_initial.py`
- `system/0002_seed_system_defaults.py`

**No changes** to existing apps' core business tables. `CommunicationProvider` reused in place.

---

## D. APIs Created

Base path: `/api/v1/system/`

| Endpoint | Method | Access | Purpose |
|----------|--------|--------|---------|
| `overview/` | GET | Super Admin | SCC dashboard snapshot |
| `branding/` | GET | Public | SPA branding bootstrap |
| `maintenance/` | GET | Public | Maintenance banner state |
| `step-up/challenge/` | POST | Super Admin | Send step-up OTP |
| `step-up/verify/` | POST | Super Admin | Verify OTP → step-up token |
| `institution/` | GET/PATCH | Super Admin | Institution profile (+ preview query) |
| `settings/<category>/` | GET/PATCH | Super Admin | Category settings (step-up for sensitive) |
| `revisions/<key>/` | GET/POST | Super Admin | History + rollback |
| `feature-flags/` | GET | Super Admin | List flags |
| `feature-flags/<key>/` | PATCH | Super Admin | Toggle flag (step-up) |
| `maintenance/control/` | GET/PATCH | Super Admin | Maintenance controls (step-up) |
| `providers/` | GET | Super Admin | List providers (masked secrets) |
| `providers/<uuid>/` | PATCH/POST | Super Admin | Update / test provider |
| `storage/` | GET/POST | Super Admin | Usage / cleanup (step-up) |
| `backups/` | GET/POST | Super Admin | List / create backup (step-up) |
| `backups/<uuid>/` | POST | Super Admin | Verify backup |
| `environment/` | GET | Super Admin | Read-only environment info |
| `license/` | GET | Super Admin | License metadata |
| `runtime/` | GET | Super Admin | Runtime configuration |

---

## E. Services Created

| Service | Responsibility |
|---------|----------------|
| `StepUpAuthService` | OTP challenge + cache token validation |
| `SystemSettingsService` | CRUD, versioning, rollback, public branding |
| `InstitutionService` | Institution profile + preview |
| `FeatureFlagService` | Module toggles + `is_enabled()` helper |
| `MaintenanceService` | Maintenance state + cache |
| `ProviderManagementService` | Provider CRUD (masked) + test |
| `StorageService` | Usage metrics + log cleanup |
| `BackupService` | Config snapshot backup + verify |
| `EnvironmentService` | Read-only environment probe |
| `SystemOverviewService` | SCC dashboard composition |
| `SystemAuditService` | Thin wrapper → `monitoring_service.record_event` |

**Reused (not duplicated):**

- `operations_health_service` — health probes for overview
- `communication_service` — provider test + dashboard stats
- `monitoring_service` — all SCC writes audited as `ADMIN_ACTION`
- `OTPService` — step-up OTP delivery

---

## F. Repositories Created

| Repository | Methods |
|------------|---------|
| `InstitutionRepository` | `get_or_create_profile`, `save_profile` |
| `SystemSettingRepository` | `get_by_key`, `list_by_category`, `list_public` |
| `SettingRevisionRepository` | `create`, `list_for_key` |
| `FeatureFlagRepository` | `list_all`, `get_by_key`, `save` |
| `MaintenanceRepository` | `get_or_create_state`, `save` |
| `BackupRepository` | `list_all`, `create`, `get_by_uuid` |
| `ProviderRepository` | `list_all`, `get_by_uuid`, `save` |

---

## G. UI Components Created

| Component | Path |
|-----------|------|
| `StepUpModal` | `components/system-control/StepUpModal.vue` |
| `SettingsForm` | `components/system-control/SettingsForm.vue` |

**Reused:** `PageHeader`, `ModuleNav`, `VCard`, `VTable`, `VButton`, `VInput`, `VModal`, `StatCard`, `StatusBadge`, `LoadingSkeleton`, `EmptyState`, `VAlert`, `OpsHealthBadge`, `useToast`

---

## H. Responsive Behaviour

- All SCC pages use `vb-page` + responsive stat grids (`xs:grid-cols-2`, `lg:grid-cols-4`)
- `ModuleNav` horizontal scroll on mobile
- `StepUpModal` bottom sheet on mobile (`items-end sm:items-center`)
- Sidebar System Control group collapses with existing drawer/collapse behaviour
- Provider and feature flag cards stack single-column on mobile

---

## I. Security Considerations

| Control | Implementation |
|---------|----------------|
| Role gate | `CanAccessSystemControlCenter` = `IsSuperAdmin` only |
| Step-up auth | OTP (MFA purpose) + 5-minute cache token for sensitive writes |
| Secret masking | Provider config + sensitive settings return `***` |
| Secret storage | Django `Signer` encryption for sensitive setting/provider values |
| Audit | Every write → `AuditLog.ADMIN_ACTION` with `subsystem: system_control` |
| Maintenance bypass | Super Admin retains API access during maintenance |
| Election integrity | SCC does not expose vote data; no changes to voting logic |

---

## J. Audit Compliance

All configuration mutations record:

```python
monitoring_service.record_event(
    event_type=AuditLog.EventType.ADMIN_ACTION,
    metadata={"subsystem": "system_control", "action": "...", ...},
)
```

Actions audited: settings update, rollback, institution update, feature flag toggle, maintenance update, provider update/test, backup create/verify, storage cleanup.

`SettingRevision` table provides version history independent of `AuditLog` for rollback UI.

---

## K. Performance Considerations

| Technique | Detail |
|-----------|--------|
| Redis cache | Maintenance state, public branding (60s), settings cache invalidation |
| Lazy routes | 21 code-split SCC pages |
| Read-heavy overview | Composes cached operations health (30s TTL) |
| Backup snapshots | File-based JSON — no blocking DB dump in Phase 14 |
| Middleware | Single DB read per API request when maintenance enabled (cached) |

---

## L. Migration Notes

1. Run migrations: `python manage.py migrate system`
2. Seed runs automatically in `0002_seed_system_defaults`
3. `MaintenanceModeMiddleware` added after `AuthenticationMiddleware` in `base.py`
4. Mount: `path("api/v1/system/", include("apps.system.api.urls"))`
5. Optional: add `psutil` for full storage/CPU metrics
6. Rebuild frontend: `npm run build`

**Runtime settings note:** JWT lifetimes and similar values are stored in DB for SCC management. Existing services continue reading Django `settings` from env until a future integration phase wires `SystemSettingsService` into auth bootstrap.

---

## M. Testing Strategy

| Test | Coverage |
|------|----------|
| Admin 403 on overview | Super Admin gate |
| Super Admin 200 overview | Happy path + payload shape |
| Public branding 200 | Unauthenticated branding API |
| Default settings seeded | Authentication category contains JWT setting |

**Manual QA:**

1. Login as `superadmin` / `[REDACTED]`
2. Open **System Control** → Overview
3. Toggle a feature flag → complete step-up OTP
4. Enable maintenance → verify non-admin API returns 503
5. Create backup → verify file in `backend/backups/`
6. Update institution settings → confirm audit log entry

---

## N. Recommended Next Phase

| Priority | Enhancement |
|----------|-------------|
| High | Wire `SystemSettingsService` into auth/JWT/OTP runtime (hot reload) |
| High | Full provider CRUD with Hubtel/Twilio/Mailgun/SendGrid/SES types |
| High | Media upload for logo/favicon (currently URL fields) |
| Medium | Scheduled backup cron + restore workflow |
| Medium | Security key (WebAuthn) step-up alongside OTP |
| Medium | Feature flag enforcement in domain services |
| Low | Global search entries for SCC routes |
| Low | Dark mode token overrides from branding settings |

---

**Verification:**

```bash
cd backend && python manage.py migrate system && python manage.py test apps.system.tests
cd frontend && npm run build
```

**Access:** Super Admin → Sidebar → System Control → `/system-control`
