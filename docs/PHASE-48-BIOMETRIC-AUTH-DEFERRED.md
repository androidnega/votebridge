# Phase 48 — Disable Mandatory Biometric Authentication (v1.0)

## A. Completion Report

Mandatory biometric login has been deferred for VoteBridge v1.0 via deployment flag `BIOMETRIC_AUTH_ENABLED=False` (default). Password → OTP → dashboard is now the sole login path for all roles. The biometric module, APIs, models, Vue pages, and database tables remain intact for future activation.

## B. Architecture Compliance

- Policy change only — no business logic in views or Vue components.
- `BiometricPolicyService.is_auth_enabled()` gates `is_module_enabled()` and `requires_verification_at_login()`.
- `AuthService.verify_otp_and_authenticate()` unchanged structurally; biometric branch skipped when policy off.
- Stale OTP cache sanitized via `_sanitize_cached_auth_result()`.

## C. Database Changes

None. No migrations. `future_biometrics` feature flag seed respects `BIOMETRIC_AUTH_ENABLED` in `seed_demo_data`.

## D. APIs

| Endpoint | Change |
|----------|--------|
| `POST /accounts/auth/otp/verify/` | Returns JWT + `redirect_path` when biometrics disabled (no `requires_biometric` / `requires_enrollment`) |
| `GET /biometrics/status/` | Adds `auth_enabled`, `deployment_status`, `deployment_message` |

## E. Vue Components

| Component | Change |
|-----------|--------|
| `BiometricAuthStatusCard.vue` | New — Identity Assurance status card (Disabled message) |
| `SystemCategorySettingsView.vue` | Renders status card on identity-assurance page |
| `guards.js` | Clears stale pending auth when module disabled |
| `auth.js` | Defensive skip of biometric redirect if backend sends disabled flags |

## F. Security Impact

Password, OTP, JWT, sessions, trusted devices, and audit logging unchanged. Biometric step-up and login verification inactive until `BIOMETRIC_AUTH_ENABLED=True` and `future_biometrics` flag enabled.

## G. Performance Impact

Negligible — one fewer risk-assessment / pending-auth branch on OTP verify when disabled.

## H. Responsive Design Notes

`BiometricAuthStatusCard` uses existing `VCard` / `StatusBadge` patterns; mobile-friendly.

## I. Testing Strategy

`apps.biometrics.tests.test_login_biometric_policy`:

- Student, admin, super admin OTP → tokens, no biometric fields (disabled)
- Enrolled admin still receives JWT when disabled
- Enabled path: admin without profile → `requires_enrollment`

Existing biometric tests use `@override_settings(BIOMETRIC_AUTH_ENABLED=True)`.

## J. Deployment Notes

1. Set in `.env`: `BIOMETRIC_AUTH_ENABLED=False` (default).
2. To restore biometrics: `BIOMETRIC_AUTH_ENABLED=True` + enable `future_biometrics` in System Control.
3. Restart Django after env change.
4. Users with stale `vb_pending_auth` in sessionStorage are redirected to login by router guard.

**Documentation:** Biometric authentication has been deferred for VoteBridge v1.0 and remains available for future activation.
