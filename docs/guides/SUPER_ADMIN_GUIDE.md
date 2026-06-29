# VoteBridge — Super Admin Guide

**Audience:** Platform owners with the **Super Admin** role  
**Version:** 1.0 RC1

---

## 1. Role overview

Super admins have full platform access:

- Election workspace (same as officers)
- **Strong room** — integrity, investigations, custody
- **Settings** — all configuration hubs
- **Results** — certification, publication, archive
- **Operations** — system health (via dashboard deep link)

---

## 2. Dashboard

**Election command center** (`/`)

| Focus | Action |
|-------|--------|
| Open elections | Monitor active votes |
| Students voted | Turnout snapshot |
| Certifications waiting | Go to Results → Certification |
| Security issues | Review Strong room investigations |
| Platform health | Open Operations health |

---

## 3. Strong room

**Sidebar → Strong room** (`/strongroom`)

### Top-level sections

| Section | Route | Purpose |
|---------|-------|---------|
| Overview | `/strongroom` | Integrity summary, election picker |
| Certification | `/results/certification` | Certify closed election results |
| Investigations | `/strongroom/investigations` | Fraud, audit, security, identity, devices |
| Election integrity | `/strongroom/integrity` | Chain of custody, verification |

### Investigations sub-tabs

| Tab | Purpose |
|-----|---------|
| Fraud | Live fraud cases and integrity metrics |
| Audit trail | Operations, communications, USSD logs |
| Security timeline | Live security alerts |
| Identity investigations | Biometric verification history |
| Trusted devices | Administrator device trust |

### Per-election strong room

`/strongroom/:electionUuid` — seal status, integrity verification, contextual export actions.

---

## 4. Certification workflow

1. Election officer **closes** the election.
2. **Results → Certification** (`/results/certification`).
3. Review generated results and integrity hash.
4. **Certify** each election in the queue.
5. **Publication** (`/results/publication`) — publish to students.
6. **Archive** (`/results/archive`) — long-term storage.

Certification exists only in Results — Strong room links here rather than duplicating.

---

## 5. Settings

See [Administrator Guide](ADMINISTRATOR_GUIDE.md) §5 for hub structure.

Sensitive categories (authentication, identity configuration, security policies) require super admin role.

---

## 6. Investigations playbook

| Scenario | Where to look |
|----------|---------------|
| Suspicious vote pattern | Fraud → case detail |
| Failed login spike | Security timeline |
| Biometric mismatch | Identity investigations |
| USSD anomaly | Audit trail → USSD tab |
| Device impersonation | Trusted devices |

---

## 7. Trusted devices & biometrics

- Enroll biometrics: Settings → Security → Identity configuration, or `/biometrics/enroll`
- Review verification events: Strong room → Identity investigations
- Manage trusted devices: Strong room → Trusted devices

---

## 8. Operations (technical)

Reachable via dashboard health card or direct URL (not in sidebar):

| Route | Purpose |
|-------|---------|
| `/operations` | Overview |
| `/operations/health` | CPU, Redis, DB status |
| `/operations/activity` | Live activity feed |
| `/platform/logs` | Unified audit logs |

---

## Related documents

- [Administrator Guide](ADMINISTRATOR_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [UAT script](../uat/SUPER_ADMIN_UAT.md)
