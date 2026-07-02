# VoteBridge System Documentation

VoteBridge is a **secure campus e-voting platform** built for institutions like universities. Students vote online (or via USSD on their phone), staff run elections, and super admins control the whole platform.

This folder contains plain-language guides and technical diagrams. Start here if you are new.

> **Source of truth for roles:** [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) is maintained against the live permission classes and router guards. Other documents summarize it for diagrams and flows.  
> **Last reviewed against codebase:** July 2026 (presentation-clean prototype + role permission alignment).

---

## Prototype demo flows (presentation)

The primary UI emphasizes these journeys. Advanced modules (Strong Room vault, platform operations center, infrastructure dashboards) remain in the codebase but are **not** in main navigation.

### Student / candidate
```
Sign in (index number) → OTP → Dashboard → Elections → Vote (SVT + presence) → Confirmation → Published results
```

### Admin (election officer)
```
Staff access → password → OTP → Dashboard → Elections → [workspace: positions, candidates, eligibility, readiness, monitor] → Close → Results / Reports
```

### Super Admin (governance)
```
Staff access → password → OTP → Dashboard → Certify/publish results → Settings (institution, integrations, governance)
```

Unified login shows **index number** copy only; **Staff access** (subtle link) reveals email/username for privileged accounts.

---

## Documents in this folder

| Document | What it explains |
|----------|------------------|
| [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) | **Source of truth** — roles, permissions, WebSocket access |
| [USE-CASE-DIAGRAM.md](./USE-CASE-DIAGRAM.md) | What each type of user can do (use case view) |
| [ERD.md](./ERD.md) | Database tables and how they connect |
| [FLOWCHARTS.md](./FLOWCHARTS.md) | Step-by-step flows (login, voting, results) |
| [SYSTEM-ARCHITECTURE.md](./SYSTEM-ARCHITECTURE.md) | How the pieces fit together (Vue, Django, Redis, etc.) |
| [TECH-STACK.md](./TECH-STACK.md) | Technologies used and why |
| [ELECTION-LIFECYCLE.md](./ELECTION-LIFECYCLE.md) | Full election journey from setup to published results |

---

## The big picture (layman's summary)

Imagine a university running **SRC (Student Representative Council) elections**:

1. **Super Admin** sets up the institution name, logo, SMS provider, and security rules.
2. **Admin (Election Officer)** creates an election, adds positions (President, Secretary…), registers candidates, and uploads the voter list.
3. When voting opens, **Students** log in with their **index number** (dedicated student portal), get a **one-time voting code (SVT)** on their phone, take a quick **presence photo** (web only), then cast their ballot.
4. Votes are stored securely. While voting is **open**, nobody sees who is winning — that protects fairness.
5. When voting **closes**, the system calculates results. A **Super Admin** certifies and **publishes** results.
6. Students can then view **published** results. A **Strongroom** process seals ballots for audit and integrity.

---

## Four user types

| Role | Who they are | Simple description |
|------|--------------|-------------------|
| **Student** | Registered voter | Logs in with index number, votes if eligible |
| **Candidate** | Student who is also contesting | Same voting power as a student, plus candidacy visibility for their races |
| **Admin** | Election officer | Creates and runs elections within scope; does not own the platform |
| **Super Admin** | Platform owner | Settings, certification, vault governance, operations center |

There is no separate “election officer” account type in the database — that is the **Admin** role in the UI.

There is also **no `auditor` login role**. External oversight uses **Strong Room committee** workflows and audit logs, not a fifth database role.

---

## Settings structure (Super Admin)

Platform settings are grouped into **six hubs** (Phase 63):

1. **Institution** — profile, branding  
2. **Security** — authentication, identity assurance, policies, API, audit  
3. **Integrations** — SMS, email, USSD, notifications  
4. **Election Governance** — election administrators, strong room policies, platform defaults  
5. **Operations** — maintenance, backup, storage, **operational data reset**  
6. **Advanced** — feature flags, environment, runtime, license  

Day-to-day election work (positions, candidates, control room) stays in the **Admin election workspace**, not in Settings.

---

## How data moves (simple version)

```
Student's browser (Vue app)
        ↓  HTTPS (REST API)
Django backend (business logic in Services)
        ↓
PostgreSQL (permanent storage: users, votes, elections)
        ↓
Redis (fast cache + live updates)
        ↓
WebSocket (real-time dashboards for admins)
```

- **PostgreSQL** = the filing cabinet (everything important is saved here).
- **Redis** = short-term memory (caching settings, live message bus for WebSockets).
- **Vue** = what users see and click in the browser.
- **Django** = the brain that enforces rules (who can vote, when, how).

---

## Election integrity rules (important)

While an election is **OPEN**:

- No candidate rankings
- No vote totals
- No winners

This applies to the website, mobile views, APIs, and live WebSocket feeds. Results appear only after the election is **closed** and **published**.

---

## Suggested reading order

1. **README** (this file) — overview  
2. **PRIVILEGES-AND-ROLES** — who does what  
3. **ELECTION-LIFECYCLE** — end-to-end election story  
4. **FLOWCHARTS** — visual step-by-step flows  
5. **USE-CASE-DIAGRAM** — actor capabilities  
6. **SYSTEM-ARCHITECTURE** + **TECH-STACK** — how it is built  
7. **ERD** — database design  

---

## Repository

- Master index: [../SYSTEM-DOCUMENTATION-INDEX.md](../SYSTEM-DOCUMENTATION-INDEX.md)
- GitHub: `https://github.com/androidnega/votebridge.git`
- API base: `/api/v1/`
- WebSocket base: `/ws/realtime/`
