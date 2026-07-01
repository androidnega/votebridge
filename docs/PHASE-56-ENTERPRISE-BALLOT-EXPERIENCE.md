# Phase 56 — Enterprise Ballot Experience & Secure Voting Session

## Summary

Phase 56 redesigns the student web voting flow into a secure, guided electoral commission-style experience with a **6-digit Secure Voting Token (SVT)**, dedicated verification step, full ballot wizard, review page, and **single-transaction submission**. USSD continues to use internal SVT handling (student never sees the code).

## Web Voting Flow

1. Student logs in (Index Number + OTP)
2. Dashboard → **Vote Now**
3. `ElectionService` / eligibility checks via `BallotService.get_ballot()` and `SVTService.request_svt()`
4. **6-digit SVT** generated, hashed, stored; plain code sent via SMS only
5. **SVT Verification Page** — masked phone, resend with 60s cooldown
6. On successful verification → **one ballot session** for the entire election
7. Ballot wizard (one step per position) → **Review** → **Submit**
8. Single DB transaction records all votes, consumes SVT, returns confirmation reference
9. Confirmation page — reference only (no candidate names)

## SVT Rules

| Rule | Value |
|------|-------|
| Generated when | Student clicks Vote Now only |
| Format | 6 digits |
| Expiry | 10 minutes |
| Max validation attempts | 5 |
| Resend cooldown | 60 seconds |
| Ballot session timeout | 15 minutes after validation |
| Scope | One SVT per election session; one ballot session; consumed on submit |

## Architecture (unchanged)

```
Views → Services → Repositories → Models
```

Business logic remains in Services. No duplication of core services.

### Services reused

- `ElectionService` (election state)
- `BallotService` / `VoteService` (ballot + submission)
- `SVTService` (token lifecycle)
- `NotificationService` / `communication_service` (SMS)
- `OTPService` (login — unchanged)
- `UssdFlowService` (USSD voting — internal SVT)

## Files Modified

### Backend

| Area | Files |
|------|-------|
| SVT model | `apps/security/models.py`, migration `0004_svttoken_ballot_session_fields.py` |
| SVT service | `apps/security/services/svt_service.py` |
| SVT validators | `apps/security/validators.py` |
| SVT API | `apps/security/api/views.py`, `serializers.py`, `urls.py` |
| Voting | `apps/voting/services/vote_service.py` |
| Dashboard | `apps/dashboard/services/dashboard_service.py` |
| Notifications | `apps/notifications/event_handlers.py` (SMS moved to service) |
| Settings | `config/settings/base.py` |
| Utils | `core/utils/phone.py` |
| Tests | `apps/security/tests/test_phase56_ballot.py` |

### Frontend

| Area | Files |
|------|-------|
| Store | `stores/voting.js` |
| Views | `views/elections/VotingWizardView.vue`, `VoteConfirmationView.vue` |
| Components | `SvtVerificationPanel.vue`, `BallotProgressBar.vue`, `BallotReviewStep.vue`, `VoteCandidatePicker.vue`, `VoteSuccessCard.vue` |
| Dashboard | `StudentActiveElectionList.vue`, `composables/useStudentVotePortal.js` |
| API / utils | `api/security.js`, `utils/svtToken.js` |
| Exports | `components/voting/index.js` |

## Vue Components Created

- `SvtVerificationPanel.vue` — SVT entry, masked phone, resend countdown
- `BallotProgressBar.vue` — step X of Y, progress bar
- `BallotReviewStep.vue` — review selections, skipped count, submit

## APIs Updated

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/security/elections/{uuid}/svt/request/` | Issue SVT (SMS); no token in response |
| POST | `/security/elections/{uuid}/svt/resend/` | Resend with cooldown |
| POST | `/security/elections/{uuid}/svt/validate/` | Verify 6-digit code → ballot session |
| GET | `/security/elections/{uuid}/svt/access/` | Voting access status |
| POST | `/voting/elections/{uuid}/submit/` | Single-transaction ballot submit |

## Database Changes

Migration `security.0004_svttoken_ballot_session_fields`:

- `validation_attempts` (smallint)
- `validated_at` (datetime, nullable)
- `last_resent_at` (datetime, nullable)

SVT generation changed to 6-digit numeric codes (hashed at rest).

## Session Storage (browser)

| Key | Content |
|-----|---------|
| `vb_ballot_selections_{uuid}` | Position → candidate UUID map |
| `vb_ballot_step_{uuid}` | Current wizard step |
| `vb_svt_token_{uuid}` | Validated SVT (for submit) |
| `vb_svt_session_{uuid}` | Ballot session metadata |
| `vb_ballot_confirmation_{uuid}` | Post-submit receipt (no choices) |

## Architecture Verification

| Requirement | Status |
|-------------|--------|
| One SVT per election session | ✓ |
| One ballot session | ✓ |
| One submission transaction | ✓ |
| Audit via MFALog / SVTAuditService | ✓ |
| Skip positions allowed | ✓ |
| Review before submit | ✓ |
| Dashboard updates after voting | ✓ |
| Mobile-first UI | ✓ |
| No SVT at login | ✓ |
| No live rankings to students | ✓ (unchanged) |
| USSD internal SVT | ✓ |

## Test Results

```bash
cd backend && python manage.py test apps.security.tests.test_phase56_ballot
# Ran 5 tests — OK
```

Phase 55 auth tests remain compatible.

## Screenshots

Manual verification required:

- Desktop: SVT verification, ballot step, review, confirmation
- Mobile: same flow at 375px width

## Settings

```env
SVT_EXPIRY_MINUTES=10
SVT_MAX_VALIDATION_ATTEMPTS=5
SVT_RESEND_COOLDOWN_SECONDS=60
BALLOT_SESSION_MINUTES=15
```
