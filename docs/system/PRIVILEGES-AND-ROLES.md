# VoteBridge — Privileges & Roles

This document is the **source of truth** for VoteBridge governance roles, permission boundaries, and live-feed access. It reflects the predefined role model in the database and the permission classes enforced by the API.

---

## Role model overview

VoteBridge uses **four predefined database roles**. There is no dynamic custom-role system; Super Admins manage **role assignments** within this fixed set.

| Role | Database value | What it represents |
|------|----------------|-------------------|
| **Student** | `student` | Eligible voter account |
| **Candidate** | `candidate` | Student voter account with **election candidacy** attached (not a separate power tier) |
| **Admin** | `admin` | Election officer — day-to-day election operations within scope |
| **Super Admin** | `super_admin` | Platform / ICT administrator — governance, certification, and platform control |

**UI note:** “Election Officer” in the interface maps to the **`admin`** database role. There is no `election_officer` role value.

### Candidate is not a governance role

`candidate` is **not** a peer of Admin or Super Admin. A candidate account is:

- A **student voter** with the same base platform privileges as `student`
- Still allowed to **vote when eligible**
- Granted **extra candidate-facing visibility only** for elections where they are registered as a candidate:
  - contested position
  - candidacy status (draft / pending / approved / rejected)
  - manifesto / profile preview
  - election notices related to their candidacy

Candidate-specific data is exposed through **election and candidate APIs**, not through elevated global permissions.

### Auditor — governed workflow, not a database role

VoteBridge does **not** define a standalone `auditor` role in the database (`Role.Name` has only `student`, `candidate`, `admin`, `super_admin`).

Audit and oversight are handled through **governed workflows and approved privileged participants**, including:

- Strong Room **committee** membership and multi-custodian vault sessions
- Strong Room **access requests** reviewed and approved under policy
- Platform **audit logs** and governance dashboards (Super Admin)
- Election-scoped security and fraud investigation tools (Admin within scope; platform-wide investigation Super Admin)

External auditors participate through **approved committee / access-request context**, not a separate login role.

---

## Authentication by role

| Role | Login method | Extra security |
|------|--------------|----------------|
| Student / Candidate | Index number (no password) → OTP (SMS or email) | — |
| Admin | Email + password → OTP | Biometric step-up when policy requires |
| Super Admin | Email + password → MFA OTP | Biometric step-up; bypasses maintenance mode |

---

## Student privileges

### Can do
- Log in with index number
- View own profile; update **limited contact fields** only (`first_name`, `last_name`, `phone_number`)
- See eligible elections on the student dashboard
- Request **Secure Voting Token (SVT)** by SMS
- Enter SVT, complete **pre-vote presence photo** (web), cast ballot
- Continue an incomplete ballot (within session time limit)
- View **published** election results only
- View own vote history and confirmation receipt
- Receive in-app notifications
- View personal analytics

### Cannot do
- Change institutional / eligibility-defining identity fields (`index_number`, `student_id`, faculty/programme linkage, role, or other eligibility metadata)
- Create or manage elections
- See vote counts or winners while an election is open
- Certify or publish results
- Access admin settings, Strong Room vault, or platform operations
- Manage other users

---

## Candidate privileges

### Base (same as Student)
All **Student** can/cannot rules apply. Candidates vote and access results under the same rules.

### Additional visibility (election-scoped)
When the user has an active candidacy record for an election:

- View contested **position** and **candidacy status**
- Preview own **manifesto / candidate profile**
- Receive **election notices** tied to their candidacy

### Cannot do
- Anything an Admin or Super Admin can do
- Change institutional identity or eligibility fields on self-service profile
- Access Strong Room vault outside an approved committee / access-request session

---

## Admin privileges (Election Officer)

Admin power is **election-scoped**. Admins run elections; they do **not** own the platform.

### Can do
- Manage own profile (contact fields only, same self-service rule as students)
- **Create, edit, schedule, open, pause, close** elections
- Manage **positions**, **candidates**, and **voter eligibility** (register / import / assign)
- Use election **control room / monitor** (turnout, activity) per election workspace
- View **election-scoped** result statuses (including draft) and export election reports
- **Preview** results (not certify or publish)
- List, **revoke, reissue** SVT tokens for assigned elections
- View **election-related** security monitoring and investigate fraud cases within operational scope
- View **election-related** communication delivery status (read-only; not platform queue control)
- View **election-focused** operational monitoring (`operations/elections/` API; election workspace dashboards)
- **Nominate** Strong Room committee members for an election; **submit** committee for approval (cannot approve)
- Participate in Strong Room **only** as an approved committee custodian during a governed vault session
- **Look up** student, candidate, and election-administrator user records (for eligibility search and committee nomination)
- View biometric verification history when module enabled
- Manage own trusted devices when policy allows

### Cannot do
- Manage **platform-wide privileged users** or assign **Super Admin**
- Create, update, deactivate, or delete arbitrary platform user accounts (Super Admin only)
- Certify, publish, or archive official results
- Approve Strong Room committee or open vault sessions without Super Admin governance
- Access casual / always-open Strong Room dashboards or Strong Room realtime feed
- Change voting channel configuration (USSD / web / SMS writes)
- Manage role assignments or predefined role catalogue (Super Admin only)
- Process notification **queue retries**, provider tests, or platform-wide communications control
- Access **platform-wide** Operations Center (health, infrastructure, queues, sessions, logs)
- Enroll staff biometrics or change biometric policy
- Access full **System Control / Settings** (institution, providers, maintenance, data reset)
- Assign university-managed devices to other users
- Bypass maintenance mode

---

## Super Admin privileges

### Can do
- **Everything Admin can do** within elections, plus platform governance:
- Full **Settings / System Control** (institution, security, integrations, election governance, operations, advanced)
- **Create and manage platform user accounts** and **assign roles** within the predefined role model (`student`, `candidate`, `admin`, `super_admin`)
- **Certify, publish, archive** election results
- Configure and approve Strong Room **policy**; approve committees; **request, review, and run vault sessions**
- Lock elections; verify Strong Room integrity
- Full **communications** management (providers, templates, queue processing, retries)
- **Platform-wide Operations Center** (health, infrastructure, queues, sessions, performance, logs)
- Enroll biometric profiles for privileged staff; configure biometric and trusted-device policies
- Revoke any user's trusted device; assign university devices
- Write voting channel configuration
- View platform audit logs and governance dashboards
- Access Strong Room, USSD, communications, and operations **realtime feeds**

### Cannot do
- Vote as a student without a valid student/candidate account and eligibility
- Create arbitrary custom roles outside the predefined `Role.Name` set

---

## Self-service profile edit rule

Students and candidates (and all roles on `/auth/me/`) may update **only**:

| Field | Self-service edit |
|-------|-------------------|
| `first_name` | ✓ |
| `last_name` | ✓ |
| `phone_number` | ✓ (blocked during an open election for the user) |
| `index_number` | ✗ |
| `student_id` | ✗ |
| `email` | ✗ (institutional identity — changed by administrators) |
| `role` / `role_name` | ✗ |
| faculty / department / programme / voter classification | ✗ (managed via institutional import and eligibility records) |

Super Admins update institutional and privileged fields through the **user management API**, not self-service profile.

---

## Strong Room governance

| Concern | Who owns it |
|---------|-------------|
| Strong Room **policy / configuration** | Super Admin (Settings → Election Governance) |
| Committee **nomination & submit** | Admin (per election) |
| Committee **approval** | Super Admin |
| Vault **access requests & sessions** | Super Admin (governed workflow) |
| Vault **participation** | Approved committee custodians only (multi-custodian authentication) |
| Casual Strong Room dashboard / feed | **Not** available to Admin |

Admin must not treat Strong Room as a normal always-open tool. Operational vault access requires an **approved access request** and active **vault session**.

---

## Operations & communications boundaries

| Capability | Admin | Super Admin |
|------------|-------|-------------|
| Election workspace monitor | ✓ | ✓ |
| Operations API `elections/` (election monitor) | ✓ | ✓ |
| Operations API platform overview, health, infrastructure, queues, sessions, logs | ✗ | ✓ |
| Communications delivery log **read** (election-related visibility) | ✓ | ✓ |
| Queue process / retry / provider test | ✗ | ✓ |
| Platform Operations Center UI & websocket | ✗ | ✓ |

---

## Permission classes (backend gates)

Django REST Framework permission classes applied to API endpoints.

| Permission class | Who passes |
|------------------|------------|
| `CanVote` | Student, Candidate |
| `CanRequestSVT` | Student, Candidate |
| `CanManageSVT` | Admin, Super Admin |
| `CanManageElections` | Admin (write); authenticated read |
| `CanManageCandidates` | Admin (write) |
| `CanManagePositions` | Admin (write) |
| `CanManageVoterEligibility` | Admin |
| `CanManageVotingChannels` | Super Admin (write); Admin (read) |
| `CanViewPublishedResults` | All authenticated; students/candidates see **published** only |
| `CanCertifyResults` | Super Admin |
| `CanPublishResults` | Super Admin |
| `CanArchiveResults` | Super Admin |
| `CanViewStrongroom` | Super Admin |
| `CanManageStrongroom` | Super Admin |
| Committee nominate/submit (`IsAdminOrSuperAdmin`) | Admin, Super Admin |
| Committee approve | Super Admin |
| `CanAccessSystemControlCenter` | Super Admin |
| `CanManageUsers` | Super Admin (full); Admin (**read** student/candidate/admin lookup only); Student/Candidate (own profile) |
| `CanManageRoles` | Super Admin only (role assignment catalogue) |
| `CanViewSecurityMonitoring` | Admin, Super Admin |
| `CanManageSecurityAlerts` | Admin, Super Admin |
| `CanViewFraudCases` | Admin, Super Admin |
| `CanManageFraudCases` | Admin, Super Admin |
| `CanAccessElectionOperations` | Admin, Super Admin |
| `CanAccessPlatformOperationsCenter` | Super Admin |
| `CanViewCommunications` | Admin, Super Admin |
| `CanManageCommunicationSettings` | Super Admin |
| `CanManageCommunications` | Super Admin |
| `CanAccessAnalytics` | Admin, Super Admin |
| `CanAccessPersonalAnalytics` | Student, Candidate, Admin, Super Admin |
| `CanEnrollBiometrics` | Super Admin |
| `CanManageBiometrics` | Admin, Super Admin |
| `CanAccessBiometricSettings` | Super Admin |
| `CanRevokeAnyDevice` | Super Admin |

---

## WebSocket (live feed) access

| Feed | Student / Candidate | Admin | Super Admin |
|------|---------------------|-------|-------------|
| Student dashboard | ✓ | — | — |
| Election live (if eligible / officer) | ✓ | ✓ | ✓ |
| In-app notifications | ✓ | ✓ | ✓ |
| Admin dashboard | — | ✓ | ✓ |
| Security / Fraud (investigation) | — | ✓ | ✓ |
| Results queue | — | ✓ | ✓ |
| Analytics (scoped) | personal only | election + security/fraud/results | full platform |
| Strong Room | — | — | ✓ |
| Communications / USSD | — | — | ✓ |
| Operations (platform) | — | — | ✓ |

Admin election monitoring uses the **per-election** websocket and election workspace dashboards, not the platform Operations or Strong Room feeds.

---

## Frontend vs backend

The Vue app hides platform routes (Settings, Operations Center, Strong Room root, Communications queue, USSD) from Admin in the **router** (`meta.roles`). The API enforces the same boundaries via permission classes. Direct API calls cannot bypass Super Admin gates for platform operations, user management, or Strong Room vault control.

---

## Biometric step-up (privileged staff)

When enabled, these actions may require a live face check for Admin / Super Admin:

- Strong Room vault session authentication
- Result certification
- Election deletion
- API key / JWT secret changes
- SMS or USSD provider changes
- System control access

**Students and candidates are never subject to biometric identity matching for voting** — only a simple presence photo before the ballot (web).

---

## Quick hierarchy

```
Super Admin  — platform governance, certification, operations
 └── Admin (Election Officer)  — election operations within scope
      └── Candidate ≈ Student (+ election candidacy visibility)
           └── Student  — voter
```

**Audit / oversight** sits beside this hierarchy via Strong Room committee workflows and platform audit logs — not via a separate `auditor` login role.
