# Phase 22 — USSD & SMS Production Readiness

**Date:** June 2026  
**Scope:** Validate, complete, and test existing USSD and SMS implementations for production deployment.

---

## A. Completion Report

| Area | Status | Notes |
|------|--------|-------|
| Architecture audit | ✅ | USSD flow delegates to AuthService, SVTService, BallotService, VoteService — no duplicated business logic |
| Arkesel USSD lifecycle | ✅ | Session create, continue, timeout, recovery (reuse `session_id`) |
| SVT integration | ✅ | `request_svt` → `validate_and_start_ballot` → `submit_ballot` via USSD |
| Eligibility checks | ✅ | `VoterEligibilityService` reused before ballot start |
| SMS OTP | ✅ | `OTPService` → `OTPDeliveryService` → `CommunicationService` → Arkesel |
| Vote confirmation SMS | ✅ | Signal-driven `vote_confirmation` template via `event_handlers` |
| Delivery failure + retry | ✅ | `CommunicationService._handle_failure` + `retry_delivery` + `process_queue` |
| Integration tests | ✅ | Web vote, USSD vote, officer monitoring, strongroom dashboard |
| Callback security | ✅ | Optional `ARKESEL_USSD_CALLBACK_SECRET` header validation |
| Production report | ✅ | This document |

---

## B. Architecture Compliance

```
Arkesel USSD Callback
        ↓
UssdControllerService (parse only)
        ↓
UssdFlowService (state machine)
        ↓
AuthService | SVTService | BallotService | VoteService | DashboardService
        ↓
Repositories / Models
```

- No business logic in views or repositories beyond data access.
- SMS never sent directly from USSD — vote confirmation uses existing `on_svt_saved` signal path.
- Election integrity preserved — no rankings/totals exposed via USSD.

---

## C. Database Changes

None. Phase 22 uses existing `ussd_session`, `ussd_request_log`, `notifications_delivery_log` tables.

---

## D. APIs

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/ussd/callback/` | Arkesel inbound (form + JSON) |
| `GET /api/v1/ussd/dashboard/` | Officer monitoring |
| `GET /api/v1/ussd/sessions/` | Session list |
| `POST /api/v1/notifications/deliveries/<uuid>/retry/` | SMS retry |
| `POST /api/v1/notifications/queue/process/` | Process retry queue |

**New setting:** `ARKESEL_USSD_CALLBACK_SECRET` — set in production and pass as `X-Arkesel-Secret` header.

---

## E. Vue Components

No new UI. Existing `UssdDashboardView.vue` and Communications admin views remain the operator surfaces.

---

## F. Security Impact

| Control | Status |
|---------|--------|
| USSD callback secret | Configurable (recommended for production) |
| Rate limiting per MSISDN | Active (`USSD_RATE_LIMIT_*`) |
| Student auth | Index + PIN only — no OTP on USSD by design |
| SVT single-use | Enforced by `SVTService` |
| SMS API key | Environment variable only |

---

## G. Performance Impact

- Session expiry runs per request (indexed `last_activity_at` query).
- SMS async via signals — USSD response not blocked by Arkesel latency.
- Retry queue batch limit 50 per `process_queue` call.

---

## H. Responsive Design Notes

N/A — backend validation phase.

---

## I. Testing Strategy

| Suite | Command |
|-------|---------|
| USSD unit/integration | `python manage.py test apps.ussd.tests` |
| SMS production | `python manage.py test apps.notifications.tests` |
| Phase 22 E2E | `python manage.py test tests.integration` |
| Full suite | `python manage.py test` |

**Coverage:** session lifecycle, auth, eligibility, SVT verify, full USSD vote, web vote, officer dashboard, strongroom post-vote, OTP SMS, vote confirmation SMS, failure/retry.

---

## J. Deployment Notes

1. Configure Arkesel USSD callback URL: `https://<domain>/api/v1/ussd/callback/`
2. Set `ARKESEL_API_KEY`, `ARKESEL_SENDER_ID`, `ARKESEL_USSD_CALLBACK_SECRET`
3. Enable `allow_ussd_voting` on elections that support USSD
4. Ensure students have `phone_number` for SMS confirmation
5. Schedule `process_queue` (Celery/cron) for SMS retries
6. Monitor `ussd/dashboard` and `notifications/dashboard` in System Control Center

---

## Production Readiness Assessment

### Ready for staging

- USSD vote flow end-to-end
- Web vote flow with SVT
- SMS OTP and vote confirmation dispatch
- Session timeout and carrier session_id recovery
- Admin USSD monitoring APIs

### Blockers before production

| Issue | Severity | Mitigation |
|-------|----------|------------|
| Arkesel callback secret not set | High | Set `ARKESEL_USSD_CALLBACK_SECRET` in production `.env` |
| SMS retry requires scheduler | Medium | Deploy Celery beat or cron for `process_queue` |
| Orphaned SVT on abandoned USSD ballot | Low | Existing SVT expiry rules apply; monitor `IN_USE` tokens |
| Biometric tests unrelated to USSD | Low | Pre-existing mock embedding test gaps — does not block USSD |

### Staging verification checklist

- [ ] Dial short code on Arkesel sandbox — main menu appears
- [ ] Complete vote with test student index + PIN
- [ ] Confirm SMS received (vote_confirmation)
- [ ] Verify vote via menu option 3
- [ ] Confirm session recovery after 5+ minute idle
- [ ] Test invalid callback secret returns 403

---

## Code Changes (Phase 22)

| File | Change |
|------|--------|
| `ussd/repositories/ussd_repository.py` | `reset_session`, abandoned vs expired expiry |
| `ussd/services/ussd_flow_service.py` | Session recovery, timeout log outcome, SMS message accuracy |
| `ussd/permissions.py` | Optional callback secret |
| `apps/ussd/tests/` | Expanded USSD test package |
| `apps/notifications/tests.py` | SMS production readiness tests |
| `tests/integration/` | E2E workflow tests |
