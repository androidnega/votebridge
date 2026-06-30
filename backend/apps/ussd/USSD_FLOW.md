# VoteBridge USSD Flow Documentation

Every step of the Arkesel USSD integration is documented below. The USSD layer is a **thin controller** — all business rules live in existing VoteBridge services.

## Architecture

```
Student → Arkesel USSD → UssdControllerService → UssdFlowService
    → AuthService | EligibilityService | SVTService | BallotService | VoteService
    → Repositories → Database
```

Post-vote: `consume_svt` → Strongroom signal → Communication Service (`vote_confirmation` SMS).

---

## Callback Endpoint

| Item | Value |
|------|-------|
| URL | `POST /api/v1/ussd/callback/` |
| Form format | `sessionId`, `phoneNumber`, `text`, `serviceCode` |
| JSON format | `sessionID`, `msisdn`, `userData`, `newSession`, `network` |
| Form response | `application/json` — `{ sessionID, userID, msisdn, message, continueSession }` |
| JSON response | `application/json` — `{ sessionID, userID, msisdn, message, continueSession }` |

---

## Session State Machine

| Step constant | Purpose |
|---------------|---------|
| `WELCOME` | New session — show main menu |
| `MAIN_MENU` | Route menu selection 1–6 |
| `AUTH_INDEX` | Collect index number |
| `AUTH_PIN` | Collect PIN/password |
| `VOTE_LIST` | List open USSD-enabled elections |
| `VOTE_SELECT` | Begin voting for selected election |
| `VOTE_POSITION` | Advance position index |
| `VOTE_CANDIDATE` | Collect candidate selection |
| `VOTE_REVIEW` | Show ballot summary |
| `VOTE_CONFIRM` | Final confirmation |
| `STATUS_LIST` | Show voting status per election |
| `VERIFY_SVT` | Enter SVT for verification |
| `INFO_LIST` | List elections for information |
| `INFO_DETAIL` | Show election details (no results while OPEN) |
| `HELP` | Help text |

Global navigation: input `0` returns to main menu.

---

## Step-by-Step Flows

### Step 1 — Session initiation

1. Arkesel sends empty `text` or `newSession: true`.
2. `UssdControllerService` parses `sessionId` and `msisdn`.
3. `UssdFlowService` creates `USSDSession` (status: `active`).
4. Response: main menu (`CON`).

**Service calls:** none (session repository only).

---

### Step 2 — Main menu (options 1–6)

| Input | Action | Next step |
|-------|--------|-----------|
| `1` | Vote | `AUTH_INDEX` (if not logged in) or `VOTE_LIST` |
| `2` | My Voting Status | `AUTH_*` or `STATUS_LIST` |
| `3` | Verify Vote | `AUTH_*` or `VERIFY_SVT` |
| `4` | Election Information | `AUTH_*` or `INFO_LIST` |
| `5` | Help | `HELP` |
| `6` | Exit | Session `completed`, `END` |

**Service calls:** none until authenticated.

---

### Step 3 — Authentication (index + PIN)

1. Prompt: `Enter your index number` (format `BC/PROG/YY/NNN`).
2. Validate index pattern (any valid programme code).
3. Prompt: `Enter your PIN`.
4. Call `AuthService.authenticate_student_for_ussd(index_number, password)`.
5. On success: `MFALog.LOGIN_SUCCESS` with `channel: ussd`.
6. On failure: session `failed`, `END Invalid index number or PIN`.

**Service calls:**
- `AuthService.authenticate_student_for_ussd()` — reuses password verification from web login **without OTP**.

---

### Step 4 — Vote: list elections

1. Query elections: `status=OPEN`, `allow_ussd_voting=True`.
2. Filter: `VoterEligibilityRepository.is_user_eligible(election, user)`.
3. Display numbered list.

**Service calls:**
- `VoterEligibilityRepository.is_user_eligible()`

---

### Step 5 — Vote: select election

1. User selects election number.
2. `VoterEligibilityService.check_voter_eligible(election_uuid, user)`.
3. `dashboard_service.get_student_election_status()` — block if already voted.
4. `svt_service.request_svt(election_uuid, user)` — issue token.
5. `svt_service.validate_and_start_ballot(token_code, user, election_uuid)`.
6. `ballot_service.get_ballot(election_uuid, user)`.

**Service calls:**
- `VoterEligibilityService.check_voter_eligible()`
- `dashboard_service.get_student_election_status()`
- `svt_service.request_svt()`
- `svt_service.validate_and_start_ballot()`
- `ballot_service.get_ballot()`

---

### Step 6 — Vote: per-position candidate selection

For each position on the ballot:

1. Display position title and numbered candidates.
2. User selects candidate number.
3. Append to `selections` in session state.
4. Advance `position_index`.

**Service calls:** none (session state only).

---

### Step 7 — Vote: review ballot

1. Display each position and selected candidate name.
2. Options: `1` Submit, `2` Cancel.

---

### Step 8 — Vote: confirm and submit

1. User confirms with `1`.
2. Call `vote_service.submit_ballot(election_uuid, user, token_code, selections, channel_name="ussd")`.
3. Internally: `get_svt_for_submit` → record votes → `consume_svt`.
4. Strongroom seals ballot via existing `SVTToken` post_save signal.
5. Communication Service sends `vote_confirmation` SMS via existing notification signal.
6. Session `completed`, `completed_vote=True`, `END` confirmation message.

**Service calls:**
- `vote_service.submit_ballot(..., channel_name="ussd")`

**Automatic side effects:**
- Audit: `VoteAuditService`, `SVTAuditService`
- WebSocket: `ballot_submitted`, `svt_consumed`
- Strongroom: `BallotSeal` on SVT `USED`
- SMS: `vote_confirmation` template

---

### Step 9 — My Voting Status

1. `dashboard_service.get_student_overview(user)`.
2. Display `confirmation_status` per election (`recorded`, `in_progress`, `token_issued`, `not_started`).
3. **Does not expose** vote totals, rankings, or winners.

---

### Step 10 — Verify Vote

1. Prompt for SVT token.
2. Call `svt_service.verify_vote_by_svt(token_code, user)`.
3. Returns: `is_valid`, `election_title`, `positions_completed` (titles only).
4. **Does not expose** candidate names or standings.

**Service calls:**
- `svt_service.verify_vote_by_svt()` — **not** `vote_service.verify_vote()`.

---

### Step 11 — Election Information

1. List eligible/open/scheduled/closed elections (no results).
2. On selection: show title, status, start/end, position count, instructions.
3. **No live results** while election is OPEN.

**Service calls:**
- `ElectionRepository.get_by_uuid()`

---

## Session Management

| Feature | Implementation |
|---------|----------------|
| Timeout | `USSD_SESSION_TIMEOUT_MINUTES` (default 5) — stale sessions → `expired` |
| Resume | State persisted in `USSDSession.state_data` between requests |
| Cancel | `0` → main menu; review cancel → main menu |
| Invalid input | Re-prompt with `CON` |
| Exit | Menu `6` or successful `END` responses |
| Rate limit | Redis/cache per MSISDN (`USSD_RATE_LIMIT_PER_MSISDN`) |

---

## Security & Audit

- `USSDRequestLog` — every request/response with timing
- `monitoring_service.record_event()` — USSD actions
- `MFALog` — login success/failure via USSD auth
- Fraud hooks — existing `AlertDetectionService` via monitoring pipeline
- No direct Arkesel SMS calls — Communication Service only

---

## Admin APIs

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/ussd/dashboard/` | Metrics |
| `GET /api/v1/ussd/sessions/` | Session monitor |
| `GET /api/v1/ussd/logs/` | Activity logs |
| `GET /api/v1/ussd/sessions/{uuid}/` | Session detail + logs |

WebSocket: `ws/realtime/ussd/` — events `ussd_session_updated`, `ussd_vote_completed`.
