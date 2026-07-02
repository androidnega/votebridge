# VoteBridge — Seeder Structure Spec

Use this document to **define demo/seed data** before implementation. Fill in the tables and YAML blocks, then hand this file back for seeder work.

> **Scope:** Campus e-voting **prototype** data (login → vote → results). Advanced entities are optional add-ons.
>
> **Existing commands (reference):** `seed_demo_users`, `seed_demo_data`, `seed_active_election`, `reset_votebridge_dev`

---

## 1. Seeder profile (choose one)

Check the scenario you want, then fill Section 2 onward.

| Profile | Users | Elections | Votes | Best for |
|---------|-------|-----------|-------|----------|
| **A — Minimal** | 8 (all roles) | 0 | 0 | Login / role testing only |
| **B — Live demo** | 8+ | 1 OPEN | 0 | Presentation: fresh election, zero turnout |
| **C — Full dashboard** | ~28 | 4 (mixed statuses) | ~150+ on one election | Admin monitor, charts, fraud samples |
| **D — Custom** | _you define_ | _you define_ | _you define_ | Fill everything below |

**Selected profile:** `<!-- A | B | C | D -->`

**Institution branding (optional override):**

| Field | Value |
|-------|-------|
| `institution_name` | Takoradi Technical University |
| `short_name` | TTU |
| `academic_year` | 2024/2025 |
| `campus` | Main Campus |
| `contact_email` | info@ttu.edu.gh |
| `election_office_email` | elections@ttu.edu.gh |

---

## 2. What migrations already seed (do not duplicate)

These are created by `python manage.py migrate`. Your seeder should **assume they exist**.

| Entity | Table | Values |
|--------|-------|--------|
| `Role` | `accounts_role` | `student`, `candidate`, `admin`, `super_admin` |
| `VotingChannel` | `elections_voting_channel` | `web` (active), `ussd` (active), `sms` (inactive) |
| `InstitutionProfile` | `system_institution_profile` | TTU defaults (singleton) |
| `SystemSetting` | `system_setting` | ~70 keys (`election_policies.*`, `authentication.*`, etc.) |
| `FeatureFlag` | `system_feature_flag` | 15 flags (all default `enabled=True`) |
| `CommunicationProvider` | `notifications_provider` | Arkesel SMS, SMTP Email, Moolre SMS |
| `NotificationTemplate` | `notifications_template` | 12 templates (`otp_sms`, `svt_issued`, `vote_confirmation`, …) |

---

## 3. Seeding dependency order

Create records in this order. Each step depends on the rows above it.

```
1. Role                    ← from migration
2. User                    ← needs Role
3. Election                ← needs User (created_by)
4. Position                ← needs Election
5. Candidate               ← needs Election + Position
6. VoterEligibility        ← needs Election + User (students)
7. SVTToken                ← needs User + Election (for voting flow)
8. PreVotePresenceCapture  ← needs User + Election + svt_id (web only)
9. Vote                    ← needs Election, Position, Candidate, User, VotingChannel
10. BallotSeal             ← needs Vote + Election + User + svt_id
11. ElectionResult         ← needs Election (OneToOne; after close)
12. ElectionSeal           ← needs Election + ElectionResult (after certify)
13. InAppNotification      ← needs User
14. [Advanced] SecurityAlert → FraudCase, USSDSession, TrustedDevice, etc.
```

---

## 4. Users

### 4.1 Roles (fixed — do not invent new role names)

| Role DB value | UI label | Login method |
|---------------|----------|--------------|
| `super_admin` | Super Admin | Staff access → email/username + password + OTP |
| `admin` | Admin / Election Officer | Staff access → email/username + password + OTP |
| `candidate` | Candidate | Index number + OTP (student-like) |
| `student` | Student | Index number + OTP |

**Index number format:** `BC/{PROGRAMME}/24/{NNN}` — e.g. `BC/ITS/24/047`

### 4.2 Staff accounts

| # | role | email | username | first_name | last_name | phone_number | password (dev) | is_staff | is_superuser |
|---|------|-------|----------|------------|-----------|--------------|----------------|----------|--------------|
| 1 | super_admin | superadmin@ttu.edu.gh | superadmin | Akua | Mensah | | | true | true |
| 2 | admin | admin@ttu.edu.gh | admin | Kofi | Asante | | | true | false |
| 3 | admin | registrar@ttu.edu.gh | registrar | Abena | Owusu | | | true | false |
| 4 | admin | electionofficer@ttu.edu.gh | electionofficer | Yaw | Mensah | | | true | false |

_Add / remove rows as needed. Password column is dev-only — never use in production._

### 4.3 Student accounts

| # | role | index_number | student_id | email | first_name | last_name | phone_number | is_verified |
|---|------|--------------|------------|-------|------------|-----------|--------------|-------------|
| 1 | student | BC/ITS/24/047 | BC/ITS/24/047 | kwame.mensah@ttu.edu.gh | Kwame | Mensah | | true |
| 2 | student | BC/ITD/24/031 | BC/ITD/24/031 | ama.osei@ttu.edu.gh | Ama | Osei | | true |
| 3 | candidate | BC/ITN/24/112 | BC/ITN/24/112 | kofi.boateng@ttu.edu.gh | Kofi | Boateng | | true |
| 4 | student | | | | | | | |
| 5 | student | | | | | | | |

**Notes:**
- `index_number` and `student_id` are typically the same for students.
- `candidate` role users are still voters — they log in with index number like students.
- `email` and `username` must be unique. Default username = email local-part.
- All students should have `is_verified: true` for demo login.

### 4.4 Extra students (full dashboard profile)

Add rows here if profile **C** or custom — current `seed_demo_data` uses 18 more:

| first_name | last_name | index_number | email |
|------------|-----------|--------------|-------|
| Abena | Boateng | BC/ICT/24/056 | abena.boateng@ttu.edu.gh |
| Yaw | Darko | BC/MEE/24/018 | yaw.darko@ttu.edu.gh |
| Efua | Adjei | BC/ACC/24/092 | efua.adjei@ttu.edu.gh |
| _…add more…_ | | | |

---

## 5. Elections

### 5.1 Election records

| # | title | election_type | status | start_date | end_date | allow_web | allow_ussd | allow_sms | demo_seed | created_by |
|---|-------|---------------|--------|------------|----------|-----------|------------|-----------|-----------|------------|
| 1 | SRC General Elections 2026 | student_union | open | now | now + 24h | true | true | false | true | admin |

**`election_type` choices:** `general` | `student_union` | `faculty` | `departmental` | `special`

**`status` lifecycle:** `draft` → `scheduled` → `open` → `paused` | `closed` → `archived`

### 5.2 Additional elections (full dashboard only)

| # | title | status | purpose |
|---|-------|--------|---------|
| 2 | | archived | Historical record |
| 3 | | paused | Pause/resume demo |
| 4 | | closed | Results pipeline demo |
| 5 | | draft | Setup workflow demo |

---

## 6. Positions (per election)

For election **#1** — default SRC roster (7 positions):

| display_order | title | max_votes_allowed | is_votable | is_active |
|---------------|-------|-------------------|------------|-----------|
| 0 | President | 1 | true | true |
| 1 | General Secretary | 1 | true | true |
| 2 | Financial Secretary | 1 | true | true |
| 3 | Women's Commissioner | 1 | true | true |
| 4 | Sports Secretary | 1 | true | true |
| 5 | Entertainment Secretary | 1 | true | true |
| 6 | Organising Secretary | 1 | true | true |

**Constraint:** `title` unique per election.

---

## 7. Candidates (per position)

Each row is a **contestant record** (`candidates_candidate`). When the contestant is an existing TTU student, set **`user_uuid`** (maps to `Candidate.user`) so login, eligibility, and candidacy stay aligned.

| position_title | full_name | department | manifesto (short) | status | linked_index (→ user_uuid) |
|----------------|-----------|------------|-------------------|--------|-------------------------|
| President | Kofi Boateng | Information Technology | | approved | BC/ITN/24/112 |
| President | Ama Serwaa | Computer Science | | approved | |
| President | Kwame Ansah | Information Technology | | approved | |
| General Secretary | Efua Adjei | Accounting | | approved | |
| General Secretary | Daniel Owusu | Computer Science | | approved | |
| General Secretary | Selina Agyeman | Accounting | | approved | |
| _…fill per position…_ | | | | approved | |

**`status` choices:** `pending` | `approved` | `rejected` | `withdrawn`

**Constraint:** `full_name` unique per election.

**Target count (live demo):** 3 candidates × 7 positions = **21 candidates**

---

## 8. Voter eligibility

| election | rule | verified_by |
|----------|------|-------------|
| SRC General Elections 2026 | All active `student` + `candidate` role users | admin |

Per-row override (optional):

| election | user (index_number) | is_eligible | eligibility_reason |
|----------|---------------------|-------------|-------------------|
| | BC/ITS/24/047 | true | |
| | | false | Not registered for semester |

**Constraint:** one row per `(election, user)`.

---

## 9. Voting data (optional)

Skip for **profile B** (live demo with 0 votes). Fill for **profile C**.

### 9.1 Vote generation rules

| Setting | Value |
|---------|-------|
| Target election | SRC General Elections 2026 |
| Total vote rows | ~150 |
| Channel mix | 75% `web`, 25% `ussd` |
| Time distribution | Spread over last 24 hours |
| Rule | No rankings visible while election is `open` |

### 9.2 Per-vote requirements

Each `Vote` row needs:

| Field | Source |
|-------|--------|
| `election` | FK |
| `position` | FK |
| `candidate` | FK (one per position per user) |
| `user` | FK (eligible student) |
| `channel` | FK → `VotingChannel` (`web` or `ussd`) |
| `svt_id` | UUID from `SVTToken` used for that ballot |
| `vote_hash` | `Vote.compute_vote_hash(...)` — do not hand-write |

**Constraint:** unique `(user, position, candidate)`.

### 9.3 SVT tokens (if seeding votes)

| user (index) | election | status | notes |
|--------------|----------|--------|-------|
| BC/ITS/24/047 | SRC 2026 | used | Ballot completed |
| BC/ITD/24/031 | SRC 2026 | issued | Ready to vote (live demo) |

**`status` choices:** `issued` | `validated` | `used` | `expired` | `revoked`

---

## 10. Results (optional — closed election only)

For election with `status: closed`:

| election | result_status | certified_by | published_by | notes |
|----------|---------------|--------------|--------------|-------|
| | pending_generation → generated → certified → published | super_admin | super_admin | |

**`ElectionResult.status` choices:** `pending_generation` | `generated` | `pending_certification` | `certified` | `published` | `archived`

**Fields computed by services (do not hand-seed rankings for open elections):**
- `standings` (JSON)
- `result_hash`
- `turnout_percentage`
- `integrity_report`

---

## 11. Notifications (optional)

| user (index) | template_code | title | category | is_read |
|--------------|---------------|-------|----------|---------|
| BC/ITS/24/047 | election_opening | SRC Elections are open | election | false |
| BC/ITD/24/031 | welcome | Welcome to VoteBridge | system | false |

**Template codes:** `otp_sms`, `otp_email`, `welcome`, `election_opening`, `election_closing`, `svt_issued`, `vote_confirmation`, `results_published`, `security_alert`, `fraud_alert`, `test_message`, `election_pin`

---

## 12. Advanced entities (optional — not prototype-critical)

Check what to include:

| Include? | Entity | Table | Depends on | Demo purpose |
|----------|--------|-------|------------|--------------|
| [ ] | `SecurityAlert` | `security_alerts` | User, Election, DeviceLog, LocationLog | Fraud dashboard |
| [ ] | `FraudCase` | `fraud_cases` | SecurityAlert (1:1) | Investigation UI |
| [ ] | `AuditLog` | `audit_logs` | User, Election | Audit trail |
| [ ] | `USSDSession` | `ussd_session` | User (optional) | USSD channel demo |
| [ ] | `ElectionVoterPin` | `elections_voter_pin` | Election, User | USSD PIN flow |
| [ ] | `BallotSeal` | `strongroom_ballot_seal` | Election, User, svt_id | Integrity |
| [ ] | `ElectionSeal` | `strongroom_election_seal` | Election, ElectionResult | Post-certification |
| [ ] | `StrongroomCommittee` | `strongroom_committee` | Election (1:1) | Governance |
| [ ] | `StrongroomCommitteeMember` | `strongroom_committee_member` | Committee, User | Custodians |
| [ ] | `VaultAccessRequest` | `strongroom_vault_access_request` | Election, User | Vault workflow |
| [ ] | `BiometricProfile` | `biometrics_profile` | User (staff) | Staff step-up |
| [ ] | `TrustedDevice` | `trusted_device` | User (admin) | Device trust |
| [ ] | `DeliveryLog` | `notifications_delivery_log` | User, Template, Provider | Comms monitor |

---

## 13. Integrity rules (seeder must respect)

1. **No published/certified results for OPEN elections** in UI-facing seed data.
2. **One `ElectionResult` per election** (OneToOne).
3. **One `FraudCase` per `SecurityAlert`** max.
4. **`Position.title` unique per election**; **`Candidate.full_name` unique per election**.
5. **Compute hashes via model methods** — `Vote.compute_vote_hash()`, `ElectionResult.compute_result_hash()`.
6. **PINs hashed** — use `ElectionVoterPin.hash_pin()`, never store plaintext.
7. **Passwords** — document dev credentials only in management command output, not in this file for production.

---

## 14. Command mapping (implementation reference)

| Command | Purpose |
|---------|---------|
| `seed_presentation_demo --force` | **Recommended** — reset operational data + TTU SRC (open) + FASSA (published) |
| `seed_demo_users` | Legacy — 8 TTU users only |
| `seed_demo_data` | Legacy — full multi-election dashboard demo |
| `seed_active_election` | Legacy — single OPEN election only |
| `reset_votebridge_dev --force` | Wipe + bootstrap superadmin/admin only (preserves platform config) |

**Dev passwords (existing commands):**

| Command | Password |
|---------|----------|
| `seed_presentation_demo --force` | `[REDACTED]` (staff); students use index login |
| `seed_demo_users` / `seed_demo_data` | `[REDACTED]` |
| `reset_votebridge_dev --force` | `[REDACTED]` (superadmin + admin only) |

**Demo OTP / SVT fallbacks (development only):** `111111` for staff (`superadmin`, `admin`) and all `demo_seed` students when SMS is delayed. Students also accept SVT fallback `111111` after requesting a voting code.

**Wipe before re-seed:** `seed_presentation_demo --force` or `reset_votebridge_dev --force` clears users + operational data but keeps roles, settings, templates.

---

## 15. Entity quick reference

### Core prototype tables

| Model | App | Table | Key FKs |
|-------|-----|-------|---------|
| `Role` | accounts | `accounts_role` | — |
| `User` | accounts | `accounts_user` | `role` |
| `Election` | elections | `elections_election` | `created_by` |
| `Position` | elections | `elections_position` | `election` |
| `VoterEligibility` | elections | `elections_voter_eligibility` | `election`, `user` |
| `VotingChannel` | elections | `elections_voting_channel` | — |
| `Candidate` | candidates | `candidates_candidate` | `election`, `position` |
| `Vote` | voting | `voting_vote` | `election`, `position`, `candidate`, `user`, `channel` |
| `ElectionResult` | results | `results_election_result` | `election` (1:1) |
| `InAppNotification` | notifications | `notifications_in_app` | `user` |

### Voting session tables

| Model | App | Table | When needed |
|-------|-----|-------|-------------|
| `SVTToken` | security | `svt_tokens` | Before ballot submit |
| `PreVotePresenceCapture` | voting | `voting_pre_vote_presence_capture` | Web voting only |
| `OTPRequest` | accounts | `accounts_otp_request` | Login (usually runtime, not seeded) |
| `Session` | accounts | `accounts_session` | JWT refresh (runtime) |

---

## 16. Your custom notes

```
<!-- Add any special requirements here:
  - Specific vote turnout %
  - Which election should be OPEN vs CLOSED
  - Phone numbers for SMS testing
  - Faculty/programme metadata
  - Candidate photos (file paths)
-->
```

---

## Related docs

- [ERD.md](./ERD.md) — full entity relationships
- [ELECTION-LIFECYCLE.md](./ELECTION-LIFECYCLE.md) — status transitions
- [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) — who can do what
- [SYSTEM-DOCUMENTATION-INDEX.md](../SYSTEM-DOCUMENTATION-INDEX.md)
