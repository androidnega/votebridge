# VoteBridge — Election Officer Guide

**Audience:** Users with the **Admin** role (election officers)  
**Version:** 1.0 RC1

This guide walks through the complete election lifecycle inside the **Election workspace** — one place for setup, monitoring, and handover.

---

## 1. Logging in

1. Open VoteBridge and enter your **email or username** on the sign-in page (same unified login as students).
2. Enter your **password** when prompted.
3. Complete **OTP** verification.
4. You land on the **Admin dashboard** showing open elections, turnout, and tasks.

---

## 2. Election workspace overview

**Sidebar → Election workspace** → `/elections`

| Action | How |
|--------|-----|
| Browse elections | Table on list page |
| Create election | **Create election** → `/elections/create` |
| Open workspace | Click a row → `/elections/:uuid` |

### Workspace tabs

| Tab | Purpose |
|-----|---------|
| **Overview** | Status, countdown, lifecycle actions, quick links |
| **Positions** | Offices being contested |
| **Candidates** | Nominations and approval |
| **Eligibility** | Voter roll |
| **Readiness** | Pre-open checklist |
| **Monitor** | Live turnout (visible when election is open or paused) |

---

## 3. Creating an election

1. **Election workspace → Create election**
2. Fill in: title, description, type, start/end dates, voting channels (web, USSD, SMS notifications).
3. Submit — you are redirected to the new election workspace.

Edit draft or scheduled elections from **Overview → Edit election**.

---

## 4. Configuring positions

1. Open workspace → **Positions** tab.
2. Add each position: title, description, max selections, order.
3. Edit or remove positions while the election is not closed/archived.

---

## 5. Managing candidates

1. **Candidates** tab.
2. Add candidates per position (name, manifesto, photo).
3. **Approve** or **reject** pending candidates.
4. Use **Preview** to see the student-facing profile.
5. Edit or remove as needed before and during setup.

---

## 6. Configuring eligibility

1. **Eligibility** tab.
2. Search students by **index number** or **name**.
3. Filter by programme code in the index (e.g. `BC/ITS/24/047`).
4. Add individuals or **bulk add** selected students.
5. Remove ineligible voters from the roll.

No technical UUID entry is required.

---

## 7. Scheduling

From **Overview**, use the lifecycle bar:

1. Ensure positions, approved candidates, and eligibility are complete.
2. Click **Schedule** (draft → scheduled).

---

## 8. Readiness check

1. Open **Readiness** tab.
2. Review blocking and warning items (positions, candidates, voters, integrations, strong room).
3. Resolve all blocking issues before opening.

---

## 9. Opening the election

1. On **Overview**, click **Open** when readiness passes.
2. The system validates ballot structure and infrastructure.
3. **Monitor** tab appears when status is open or paused.

---

## 10. Monitoring

- **Monitor** tab — live turnout widget (no candidate rankings exposed).
- **Admin dashboard** — aggregate turnout for your elections.
- **Reports → Turnout** — historical charts after data accumulates.

---

## 11. Pause and resume

- **Pause** — temporarily stops voting (students cannot submit ballots).
- **Resume** — returns election to open status.

---

## 12. Closing and results handover

1. Click **Close** on the lifecycle bar (confirm dialog).
2. You are redirected to **Results**.
3. Super admin certifies and publishes results (see Super Admin Guide).

---

## 13. Tips

- Complete the entire setup without leaving the workspace.
- Use **Readiness** before every open — it prevents failed opens.
- After close, do not edit positions or candidates; hand over to Results.

---

## Related documents

- [Student Guide](STUDENT_GUIDE.md) — what voters experience
- [UAT script](../uat/ELECTION_OFFICER_UAT.md) — acceptance testing checklist
- [Demo script](../DEMO_SCRIPT.md) — demonstration walkthrough
