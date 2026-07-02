# Phase 55 — Intelligent Authentication & Unified Voting Workflow

## Summary

Phase 55 delivers role-aware unified login (no role selector), passwordless student OTP, staff password→OTP, auto SVT on web Vote Now, USSD Election PIN + MSISDN validation, and phone locking during open elections.

## 1. Authentication flow

| Role | Identity | Steps |
|------|----------|--------|
| Student / Candidate | Index number (`BC/ITS/24/047`) | Continue → OTP → Dashboard |
| Election Admin | Email or username | Continue → Password → OTP → Dashboard |
| Super Admin | Email or username | Continue → Password → OTP → (optional biometric) → Dashboard |

**Service:** `AuthService.continue_authentication()` in `backend/apps/accounts/services/auth_service.py`

## 2. Login UI

- `frontend/src/vue/views/auth/LoginView.vue` — **Student** and **Administrator** sign-in modes
- **Student / candidate:** index number only → Continue → OTP → Dashboard
- **Administrator:** email or username → password → OTP → Dashboard (Super Admin may require biometric step-up)
- Student mode label: *Index number* · placeholder `BC/ITS/24/047`
- Staff mode label: *Email or username*

## 3. Backend services modified

| Service | Changes |
|---------|---------|
| `AuthService` | Intelligent identity routing; student passwordless OTP; USSD MSISDN match |
| `OTPService` | 5-minute expiry; resend cooldown (60s); max 3 resends; masked destination |
| `SVTService` | `start_voting_session()` — issue + validate on Vote Now |
| `ElectionPinService` | Generate hashed 6-digit PINs when election opens |
| `ElectionService` | Triggers PIN generation on `OPEN` transition |
| `UserService` | Blocks phone updates during open elections |
| `UssdFlowService` | Index + MSISDN; Election PIN before ballot |

## 4. APIs modified

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/accounts/auth/login/` | Optional password; returns `requires_password` or `requires_otp` |
| POST | `/api/v1/security/elections/{uuid}/svt/start/` | Auto SVT when web voting begins |

## 5. Vue components updated

- `LoginView.vue`, `auth.js` store
- `VotingWizardView.vue` — removed manual token gate; auto session start
- `ProfileView.vue` — **Verify My Ballot**
- `security.js`, `voting.js` — `startVotingSession()`

## 6. SMS templates

- `election_pin` — seeded in `notifications/migrations/0005_election_pin_template.py`

## 7. USSD workflow

1. Dial USSD → enter index number  
2. MSISDN matched to registered phone  
3. Select election → enter **6-digit Election PIN**  
4. Internal SVT issued + ballot (student never sees SVT)  
5. Vote → confirmation → session ends  

## 8. Architecture verification

```
Views → Services → Repositories → Models
```

Business logic remains in services (`AuthService`, `OTPService`, `SVTService`, `ElectionPinService`, `UssdFlowService`). Views are thin API adapters.

## 9. Test results

```
apps.accounts.tests.test_phase55_auth
  ✓ Student index → OTP (no password)
  ✓ Admin → requires_password
  ✓ Admin password → OTP
  ✓ USSD MSISDN mismatch rejected
```

Run: `python manage.py test apps.accounts.tests.test_phase55_auth`

## 10. OTP rules (configured)

| Rule | Value |
|------|-------|
| Validity | 5 minutes |
| Max verify attempts | 5 |
| Resend cooldown | 60 seconds |
| Max resends | 3 |

Settings: `backend/config/settings/base.py`

## Migrations

- `elections/0006_electionvoterpin.py`
- `notifications/0005_election_pin_template.py`

Apply: `python manage.py migrate`
