# VoteBridge System Documentation Index

Complete system documentation for privileges, diagrams, architecture, and election flows.

**Start here:** [system/README.md](./system/README.md)

**Source of truth for roles:** [system/PRIVILEGES-AND-ROLES.md](./system/PRIVILEGES-AND-ROLES.md)

**Last reviewed against codebase:** July 2026 (Phase 63 settings, role permission alignment, pre-vote presence capture, student portal, operational data reset).

---

## Documents

| # | Document | Description |
|---|----------|-------------|
| 1 | [Privileges & Roles](./system/PRIVILEGES-AND-ROLES.md) | **Authoritative** role and permission matrix |
| 2 | [Use Case Diagram](./system/USE-CASE-DIAGRAM.md) | Actor goals and system use cases |
| 3 | [ERD](./system/ERD.md) | Database entities and relationships |
| 4 | [Flowcharts](./system/FLOWCHARTS.md) | Login, voting, results, USSD flows |
| 5 | [System Architecture](./system/SYSTEM-ARCHITECTURE.md) | Vue, Django, Redis, WebSocket layers |
| 6 | [Tech Stack](./system/TECH-STACK.md) | Technologies and why they were chosen |
| 7 | [Election Lifecycle](./system/ELECTION-LIFECYCLE.md) | Full election journey in plain language |

---

## Recent features documented

| Feature | Where documented |
|---------|------------------|
| Pre-vote presence capture (web) | ELECTION-LIFECYCLE Phase 6, FLOWCHARTS §2, ERD |
| Student portal (`StudentAppShell`) | SYSTEM-ARCHITECTURE, TECH-STACK |
| Six settings hubs (Phase 63) | README, ELECTION-LIFECYCLE Phase 1, SYSTEM-ARCHITECTURE |
| Admin vs Super Admin operations split | PRIVILEGES, ELECTION-LIFECYCLE Phase 7, USE-CASE-DIAGRAM |
| Bulk eligibility import | ELECTION-LIFECYCLE Phase 3, USE-CASE-DIAGRAM |
| Operational data reset / election purge | ELECTION-LIFECYCLE, USE-CASE-DIAGRAM, SYSTEM-ARCHITECTURE |
| Dev OTP fallback & `reset_votebridge_dev` | TECH-STACK, ELECTION-LIFECYCLE |
| Candidate ≠ governance role | PRIVILEGES, README, USE-CASE-DIAGRAM |

---

## Who should read what?

| Audience | Recommended reading |
|----------|---------------------|
| New team member | README → Election Lifecycle → Architecture |
| Institution admin | Privileges → Election Lifecycle → Flowcharts |
| Developer | Tech Stack → Architecture → ERD |
| Auditor / compliance | PRIVILEGES (committee workflows) → ERD → Election Lifecycle |

---

## Diagram rendering

All diagrams use **Mermaid** syntax. They render automatically on GitHub and in VS Code with a Mermaid extension.
