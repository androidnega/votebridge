# VoteBridge — Administrator Guide

**Audience:** Institution administrators with the **Super Admin** role  
**Version:** 1.0 RC1

This guide covers platform oversight: users, settings, reports, and election supervision. For day-to-day election setup, see the [Election Officer Guide](ELECTION_OFFICER_GUIDE.md).

---

## 1. Logging in

1. Open the VoteBridge URL provided by your IT team.
2. On the sign-in page, tap **Staff access** (below the student form).
3. Enter your **email or username**, then **Continue**.
4. Enter your **password** when prompted.
5. Complete **OTP** verification sent to your registered contact.
6. After OTP, you are taken to the dashboard. **Biometric verification** may be required when enabled by policy.

After login you land on the **Election command center** dashboard.

> **Students and candidates** use the default sign-in form: **Enter your index number** → OTP (no password). See the [Student Guide](STUDENT_GUIDE.md).

---

## 2. Dashboard

The super admin dashboard answers:

| Card | Meaning |
|------|---------|
| Open elections | Elections currently open or paused |
| Students voted | Aggregate turnout across active elections |
| Certifications waiting | Results awaiting certification |
| Security issues | Open security alerts |
| Platform health | Link to operations health detail |

Quick actions: **Election workspace**, **Certification**.

---

## 3. Election management (oversight)

Super admins use the same **Election workspace** as election officers:

- **Sidebar → Election workspace** → `/elections`
- Click an election to open `/elections/:uuid` with tabs: Overview, Positions, Candidates, Eligibility, Readiness, Monitor

You can create, edit (draft/scheduled), and run the full lifecycle. Use this for supervision and recovery, not routine officer work.

---

## 4. Reports

**Sidebar → Reports** (`/reports`)

| Tab | Purpose |
|-----|---------|
| Overview | Election KPIs and explore drill-downs |
| Participation | Voter participation trends |
| Turnout & results | Per-election turnout (no rankings while OPEN for students) |
| Historical trends | Cross-election comparisons |
| Export | Download report packages |

Advanced explore routes (`/reports/explore/*`) cover students, departments, faculties, programmes, security, fraud, communications, and USSD (super admin only where marked).

---

## 5. Settings

**Sidebar → Settings** (`/settings`)

Five hub groups:

| Hub | Contents |
|-----|----------|
| **Institution** | Branding, election policies, academic year / institution profile |
| **Voting** | Voting channels, communication providers, notifications, USSD |
| **Security** | Authentication, identity configuration, security policies |
| **Advanced** | Maintenance, backup, integrations, feature flags, system configuration |

Changes save through the existing configuration forms. Validation errors appear inline.

---

## 6. User management

User administration is performed via the REST API and Django admin, or future UI extensions:

| Action | API |
|--------|-----|
| List users | `GET /api/v1/accounts/users/` |
| Create user | `POST /api/v1/accounts/users/` |
| Activate/deactivate | `POST .../activate/`, `.../deactivate/` |
| Roles | `GET /api/v1/accounts/roles/` |

**Roles:** `student`, `candidate`, `admin` (election officer), `super_admin`.

In development, seed users with:

```bash
cd backend && python manage.py seed_demo_users
```

Demo passwords are documented in the management command docstring only.

---

## 7. Strong room & certification

See [Super Admin Guide](SUPER_ADMIN_GUIDE.md) for investigations and certification workflow.

---

## 8. Getting help

- Technical API reference: [API Documentation](../API.md)
- Deployment: [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Production readiness: [PRODUCTION_CHECKLIST.md](../PRODUCTION_CHECKLIST.md)
