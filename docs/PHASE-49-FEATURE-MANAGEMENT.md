# Phase 49 — Centralized Feature Management & USSD Simplification

## A. Completion Report

Phase 49 centralizes platform enable/disable state in `FeatureFlagService` and removes duplicate toggles from integration and provider pages. USSD and SMS channels are enforced at the service layer before processing. The USSD main menu is simplified to Vote, My Vote, Election Info, and Exit with dynamic variants when no election is open or USSD voting is unavailable.

## B. Architecture Compliance

- **Views → Services → Repositories → Models** preserved.
- `FeatureFlagService` is the single source of truth; no model access from views.
- Integration pages expose configuration only; toggles live on Feature Flags.
- Business logic remains in services (`ussd_controller_service`, `communication_service`, `auth_service`).

## C. Database Changes

- No schema migrations.
- `ensure_defaults()` seeds new flag keys (`email_notifications`, `otp_authentication`, etc.) when missing.
- `maintenance_mode` flag syncs `MaintenanceState.is_enabled` on toggle.

## D. APIs

| Area | Behaviour |
|------|-----------|
| `GET/PATCH /system/feature-flags/` | Sole location to enable/disable platform modules |
| `GET/PATCH /system/settings/{category}/` | Rejects `flag_managed_setting` keys (e.g. `ussd.voting_enabled`) |
| `POST /ussd/callback/` | Returns `END` immediately when USSD flag is off |
| Login | Skips OTP step when `otp_authentication` flag is off |

## E. Vue Components

| File | Change |
|------|--------|
| `SystemFeatureFlagsView.vue` | Unchanged — canonical toggle UI |
| `SystemProvidersView.vue` | Removed Enable/Disable provider buttons |
| `SystemMaintenanceView.vue` | Removed `is_enabled` toggle; messaging points to Feature Flags |
| `SystemCategorySettingsView.vue` | Backend filters boolean/flag-managed keys for integrations |

## F. Security Impact

- Disabled USSD cannot reach flow/auth/voting logic.
- Disabled SMS/email channels reject outbound delivery at `CommunicationService`.
- OTP bypass when flag off issues session only after password validation (existing auth checks).
- Maintenance active only when `maintenance_mode` flag **and** state agree.

## G. Performance Impact

- Feature flags cached 60s per key (`feature_flag:{key}`).
- USSD disabled path avoids session DB work beyond audit.
- Queue processor skips disabled channels without delivery attempts.

## H. Responsive Design Notes

- Feature Flags grid unchanged (1-col mobile, 2-col lg).
- Integration pages retain config-only forms on all breakpoints.

## I. Testing Strategy

| Test | Coverage |
|------|----------|
| `test_feature_flag_service.py` | Flag defaults, SMS channel gate, settings filter/reject, USSD controller block |
| `test_flow_sessions.py` | Menu exit via `0`, session recovery |
| `test_flow_voting.py` | Election info menu (replaces SVT verify menu test) |
| `test_controller.py` | Callback parsing |
| Trusted device tests | `BIOMETRIC_AUTH_ENABLED=True` override for risk scenarios |

## J. Deployment Notes

1. Run migrations (no new migration required; `seed` / `ensure_defaults` on deploy).
2. Super Admins configure channels on **Settings → Advanced → Feature Flags**.
3. Integration pages (USSD, SMS, Email) remain for provider/credential configuration.
4. Toggle `maintenance_mode` on Feature Flags to activate maintenance (message/stops configured on Maintenance page).
