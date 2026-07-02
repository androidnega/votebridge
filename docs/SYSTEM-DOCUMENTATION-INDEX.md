# VoteBridge System Documentation Index

VoteBridge is documented as a **clean campus e-voting prototype** with advanced governance modules available in code but not emphasized in the primary presentation UI.

**Start here:** [system/README.md](./system/README.md)

**Roles & permissions (authoritative):** [system/PRIVILEGES-AND-ROLES.md](./system/PRIVILEGES-AND-ROLES.md)

---

## Recommended reading order

Read in this order for the fastest understanding of the working prototype:

| # | Document | Why read it |
|---|----------|-------------|
| 1 | [System overview](./system/README.md) | What VoteBridge is and the three demo journeys |
| 2 | [Election lifecycle](./system/ELECTION-LIFECYCLE.md) | End-to-end election story from setup to published results |
| 3 | [Use case diagram](./system/USE-CASE-DIAGRAM.md) | Who does what — core vs advanced capabilities |
| 4 | [Flowcharts](./system/FLOWCHARTS.md) | Login, voting, results (visual steps) |
| 5 | [ERD](./system/ERD.md) | Database entities — core prototype vs supporting tables |
| 6 | [System architecture](./system/SYSTEM-ARCHITECTURE.md) | Vue, Django, PostgreSQL, Redis, WebSockets |
| 7 | [Privileges & roles](./system/PRIVILEGES-AND-ROLES.md) | Permission boundaries and API gates |
| 8 | [Tech stack](./system/TECH-STACK.md) | Technologies in use |

---

## Documentation layers

### Core prototype documentation

What reviewers and demo audiences should focus on:

| Topic | Document |
|-------|----------|
| Unified login (index number + Staff access) | [Flowcharts §1](./system/FLOWCHARTS.md), [README](./system/README.md) |
| Student / candidate voting | [Flowcharts §2](./system/FLOWCHARTS.md), [Election lifecycle §6](./system/ELECTION-LIFECYCLE.md) |
| Admin election workspace | [Election lifecycle §2–5, §7–9](./system/ELECTION-LIFECYCLE.md), [Use cases — Admin](./system/USE-CASE-DIAGRAM.md) |
| Results certification & publication | [Election lifecycle §10–12](./system/ELECTION-LIFECYCLE.md), [Flowcharts §6](./system/FLOWCHARTS.md) |
| Super Admin settings & governance | [README — Super Admin flow](./system/README.md), [Privileges](./system/PRIVILEGES-AND-ROLES.md) |
| Data model (core tables) | [ERD — prototype core](./system/ERD.md) |

### Advanced / governance / technical documentation

Real capabilities that exist in code but are **demoted from primary navigation** (Settings sub-pages, super-admin-only routes, or API-only):

| Topic | Document |
|-------|----------|
| Strong Room vault & committee | [Privileges — Strong Room](./system/PRIVILEGES-AND-ROLES.md), [Flowcharts §8](./system/FLOWCHARTS.md), [ERD — supporting](./system/ERD.md) |
| Platform Operations Center | [Privileges — Operations](./system/PRIVILEGES-AND-ROLES.md), [Architecture](./system/SYSTEM-ARCHITECTURE.md) |
| Fraud / security investigations | [Privileges](./system/PRIVILEGES-AND-ROLES.md), [Use cases — advanced](./system/USE-CASE-DIAGRAM.md) |
| Biometrics & trusted devices | [Privileges](./system/PRIVILEGES-AND-ROLES.md), [Tech stack](./system/TECH-STACK.md) |
| USSD voting channel | [Flowcharts §7](./system/FLOWCHARTS.md), [Election lifecycle §6b](./system/ELECTION-LIFECYCLE.md) |
| Developer tooling (local only) | [Tech stack — appendix](./system/TECH-STACK.md) |

---

## Core system documents

| Document | Description |
|----------|-------------|
| [README](./system/README.md) | System overview and prototype demo flows |
| [Election Lifecycle](./system/ELECTION-LIFECYCLE.md) | Full election journey in plain language |
| [Use Case Diagram](./system/USE-CASE-DIAGRAM.md) | Actor goals — prototype scope highlighted |
| [Flowcharts](./system/FLOWCHARTS.md) | Step-by-step process diagrams |
| [ERD](./system/ERD.md) | Database entities and relationships |
| [System Architecture](./system/SYSTEM-ARCHITECTURE.md) | Layers, modules, presentation UI surfaces |
| [Privileges & Roles](./system/PRIVILEGES-AND-ROLES.md) | **Authoritative** role and permission matrix |
| [Tech Stack](./system/TECH-STACK.md) | Technologies actually used in the project |

---

## Core capabilities (what the prototype demonstrates)

| Capability | Where documented |
|------------|------------------|
| Unified login — index number + subtle Staff access | README, Flowcharts §1, Privileges |
| Student portal voting (SVT + presence + ballot) | Election lifecycle §6, Flowcharts §2–3 |
| Admin election workspace (positions, candidates, eligibility, monitor) | Election lifecycle §2–5, Use cases |
| Bulk eligibility import | Election lifecycle §3, Use cases |
| Results generate → certify → publish | Election lifecycle §10–12, Flowcharts §6 |
| Admin vs Super Admin permission split | Privileges, Architecture, Use cases |
| Candidate = student voter + candidacy visibility | Privileges, Use cases, README |
| Auditor = workflow only (no `auditor` role) | Privileges |

---

## Advanced reference (not in main demo path)

| Capability | Where documented | Notes |
|------------|------------------|-------|
| Presentation demo seed (`seed_presentation_demo`) | [SEEDER-STRUCTURE.md](./system/SEEDER-STRUCTURE.md) | TTU SRC open + FASSA published |
| Candidate ↔ student user linkage | [ERD](./system/ERD.md), [PRIVILEGES](./system/PRIVILEGES-AND-ROLES.md) | Optional `Candidate.user` FK |
| Strong Room vault sessions | Flowcharts §8, ERD, Privileges | Super Admin governance; not in primary sidebar |
| Platform Operations Center | Privileges, Architecture | Super Admin only; demoted from prototype nav |
| Operational data reset | Election lifecycle appendix, Architecture | Settings → Operations; staging/dev recovery |
| Local dev bootstrap / OTP fallback | Tech stack appendix | Development settings only — not production |

---

## Who should read what?

| Audience | Start with | Then |
|----------|------------|------|
| **Demo / presentation reviewer** | README → Election lifecycle → Flowcharts | ERD if data model matters |
| **Institution election officer** | README → Election lifecycle → Privileges (Admin section) | Flowcharts §4 (admin lifecycle) |
| **Platform / ICT administrator** | README → Privileges (Super Admin) → Election lifecycle §11–12 | Architecture → Settings hubs in README |
| **Developer** | Architecture → Tech stack → ERD | Privileges for API permission classes |
| **Compliance / audit** | Privileges (committee workflows) → ERD → Election lifecycle | Flowcharts §8 (Strong Room) |

---

## Other documentation (outside this index)

| Location | Content |
|----------|---------|
| [guides/](./guides/) | Role-specific how-to guides (Student, Election Officer, Super Admin) |
| [uat/](./uat/) | User acceptance test scripts |
| [DEPRECATED.md](./DEPRECATED.md) | Legacy routes and removed surfaces |
| `PHASE-*.md` | Historical implementation reports — not required for prototype understanding |

---

## Diagram rendering

All diagrams use **Mermaid**. They render on GitHub and in VS Code with a Mermaid extension.
