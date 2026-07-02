# VoteBridge System Documentation

VoteBridge is a **secure campus e-voting platform** for institutions such as universities. Students vote online (or via USSD on their phone), election officers run elections, and super admins handle platform governance.

This folder is the **main system documentation** for the presentation-ready prototype. Start here if you are new.

> **Source of truth for roles:** [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md)  
> **Master index:** [../SYSTEM-DOCUMENTATION-INDEX.md](../SYSTEM-DOCUMENTATION-INDEX.md)

---

## Prototype demo flows

The primary UI emphasizes these journeys. Advanced modules (Strong Room vault, platform operations center, infrastructure dashboards) remain in the codebase but are **not in main navigation**.

### Student / candidate
```
Sign in (index number) → OTP → Dashboard → Elections → Vote (SVT + presence) → Confirmation → Published results
```

### Admin (election officer)
```
Staff access → password → OTP → Dashboard → Elections → workspace (positions, candidates, eligibility, readiness, monitor) → Close → Results / Reports
```

### Super Admin (governance)
```
Staff access → password → OTP → Dashboard → Certify / publish results → Settings (institution, integrations, governance)
```

**Login:** One page at `/auth/login`. Public copy says **Enter your index number** only. A subtle **Staff access** link reveals email/username sign-in for privileged accounts.

---

## The big picture

Imagine a university running **SRC elections**:

1. **Super Admin** configures the institution, SMS provider, and platform settings.
2. **Admin** creates an election, adds positions and candidates, and builds the voter roll.
3. **Students** sign in with their **index number**, receive a **one-time voting code (SVT)** by SMS, take a quick **presence photo** (web), and cast their ballot.
4. While voting is **open**, nobody sees vote counts or winners.
5. When voting **closes**, results are generated. **Super Admin** certifies and **publishes** them.
6. Students view **published** results. Strong Room sealing and vault governance support audit integrity but are **advanced** — not part of the main demo navigation.

---

## Four user types

| Role | Who they are | In the prototype UI |
|------|--------------|---------------------|
| **Student** | Registered voter | Dashboard, Elections, Results, Notifications |
| **Candidate** | Student who is also contesting | Same as student — no separate power dashboard |
| **Admin** | Election officer | Dashboard, Elections, Results, Reports |
| **Super Admin** | Platform owner | Dashboard, Results, Settings |

There is no `election_officer` database role — that is **Admin** in the UI.

There is no **`auditor` login role**. Oversight uses Strong Room committee workflows and audit logs.

---

## Settings (Super Admin)

Platform settings are grouped into six areas accessible from **Settings** in the sidebar:

1. **Institution** — profile, branding  
2. **Security** — authentication, identity assurance, policies  
3. **Integrations** — SMS, email, USSD, notifications  
4. **Election Governance** — election administrators, strong room policies  
5. **Operations** — maintenance, backup, storage, operational data reset  
6. **Advanced** — feature flags, environment, runtime  

Day-to-day ballot work stays in the **Admin election workspace**, not Settings.

---

## How data moves

```
Vue app (browser)
    ↓  HTTPS REST API
Django services (business logic)
    ↓
PostgreSQL (users, votes, elections)
    ↓
Redis (cache + WebSocket pub/sub)
    ↓
WebSocket (live election monitoring for admins)
```

---

## Election integrity rules

While an election is **OPEN**:

- No candidate rankings  
- No vote totals  
- No winners  

Enforced in services, APIs, WebSocket sanitization, and the Vue UI. Results appear only after **close**, **certification**, and **publication**.

---

## Documents in this folder

| Document | What it explains |
|----------|------------------|
| [ELECTION-LIFECYCLE.md](./ELECTION-LIFECYCLE.md) | Full election journey |
| [USE-CASE-DIAGRAM.md](./USE-CASE-DIAGRAM.md) | Actor goals — core vs advanced |
| [FLOWCHARTS.md](./FLOWCHARTS.md) | Step-by-step flows |
| [ERD.md](./ERD.md) | Database tables |
| [SYSTEM-ARCHITECTURE.md](./SYSTEM-ARCHITECTURE.md) | Technical architecture |
| [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) | Roles and permissions |
| [TECH-STACK.md](./TECH-STACK.md) | Technologies used |

---

## Suggested reading order

1. **README** (this file)  
2. **Election lifecycle**  
3. **Use case diagram**  
4. **Flowcharts**  
5. **ERD**  
6. **System architecture**  
7. **Privileges & roles**  
8. **Tech stack**

---

## Repository

- API base: `/api/v1/`  
- WebSocket base: `/ws/realtime/`  
- GitHub: `https://github.com/androidnega/votebridge.git`
