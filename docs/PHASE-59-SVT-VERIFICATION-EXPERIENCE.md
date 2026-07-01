# Phase 59 — Secure Voting Token Verification Experience

Phase 59 replaces the 6-digit OTP-style SVT with a human-friendly **Voting Code** (`VB-XXXX-XXXX`) and a dedicated premium verification page at `/dashboard/vote/verify/:uuid`.

## Flow

1. Student clicks **Vote Now** on the dashboard.
2. `ElectionService` / `SVTService` verify eligibility and issue a token.
3. Plain formatted code is sent via SMS; only the hash is stored.
4. Student is redirected to **Secure Voting Verification**.
5. After successful validation, a short unlock animation plays and the student enters the ballot wizard.

**Login authentication ≠ ballot authorization.** The SVT is the final gate before the secure ballot.

## Token format

| Layer | Format |
|-------|--------|
| SMS / UI | `VB-7F4K-92XM` (also accepts `SVT-` prefix when pasted) |
| Storage | SHA-256 hash of normalized `VB-XXXX-XXXX` |
| Generation | `core.utils.svt_token_format.generate_formatted_svt()` |

Settings unchanged: 10-minute expiry, 60-second resend cooldown, 5 validation attempts.

## Architecture (unchanged)

Views → Services → Repositories → Models

Reused services: `SVTService`, `ElectionService`, `NotificationService`, `VotingService`.

## Frontend

| File | Role |
|------|------|
| `VoteVerifyView.vue` | Dedicated verification page |
| `SvtCodeField.vue` | Segmented display + auto-formatting input |
| `useVoteEntry.js` | Vote Now → request SVT → redirect |
| `svtToken.js` | Client-side normalize/validate |
| `VotingWizardView.vue` | Ballot only; redirects if session not validated |

## API

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/security/elections/{uuid}/svt/request/` | Issue voting code |
| POST | `/security/elections/{uuid}/svt/validate/` | Verify code → ballot session |

`token_code` serializer fields accept up to 20 characters (formatted code).

## Tests

- `backend/apps/security/tests/test_phase59_svt_format.py`
- Updated Phase 56 ballot tests for new format
- `frontend/src/vue/utils/svtToken.test.js`
