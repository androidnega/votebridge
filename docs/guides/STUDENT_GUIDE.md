# VoteBridge — Student Guide

**Audience:** Students and candidates  
**Version:** 1.0 RC1

---

## 1. Logging in

1. Open VoteBridge on your phone or computer.
2. Enter your **index number** (e.g. `BC/ITS/24/047`) in the login field.
3. Tap **Continue** and enter the **OTP** sent to your registered phone or email.
4. You arrive at your **Dashboard**.

There is no role selector — the system recognises you as a student automatically.

---

## 2. Dashboard

Your dashboard shows:

- **Active elections** you can vote in
- **Voting history** — elections you have already voted in
- Notifications and profile shortcuts

---

## 3. Finding elections

**Sidebar → Elections** (`/elections`)

- Browse available elections.
- Tap an election to view details: positions, candidates, dates, and status.
- Read **candidate profiles** (photo and manifesto) before voting.

---

## 4. Voting (web)

When an election is **open** and you are **eligible**:

1. From the election page, open the **Vote** tab or tap **Vote now**.
2. For each position, select your preferred candidate(s).
3. Review your choices on the summary screen.
4. Confirm submission — you may need to validate your **Secure Voting Token (SVT)**.
5. You cannot change your vote after submission.

### Rules

| Rule | Detail |
|------|--------|
| One vote per election | Duplicate votes are rejected |
| Eligibility | Only students on the voter roll can vote |
| Timing | Voting only while election is open and within dates |
| Paused elections | Voting is blocked when election is paused |

---

## 5. Vote confirmation

After submitting:

1. You are taken to **Confirmation** (`/elections/:uuid/confirmation`).
2. You see a confirmation reference — keep it for your records.
3. Optional: verify ballot integrity with your SVT code.

If you navigate away without voting, the Vote tab remains available until you submit or the election closes.

---

## 6. Vote history

Voting history appears on your **Dashboard** under past elections — not a separate menu item.

Each entry shows the election name, date voted, and confirmation status. **Vote totals and rankings are never shown while an election is open.**

---

## 7. USSD voting

If your institution enables USSD:

1. Dial the campus USSD code on any phone.
2. Enter your index number and PIN when prompted.
3. Follow menu prompts to select candidates and confirm.

See the [USSD Guide](USSD_GUIDE.md) for technical setup (officers only).

---

## 8. Profile & notifications

- **Profile** — update contact details where permitted.
- **Notifications** — election reminders and system messages.

---

## 9. Getting help

Contact your **electoral commission** or **SRC election officer** if:

- OTP does not arrive
- You are eligible but cannot vote
- You receive an error after confirmation

---

## Related documents

- [UAT script](../uat/STUDENT_UAT.md)
- [Demo script](../DEMO_SCRIPT.md) (sections 5–6)
