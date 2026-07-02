# VoteBridge — Demonstration Script

**Version:** 1.0 RC1  
**Duration:** ~45 minutes  
**Audience:** Stakeholders, electoral commission, IT leadership

Use a **staging environment** with `seed_demo_data`. Demo credentials are in the `seed_demo_users` management command docstring (development only).

---

## Cast

| Role | Account type |
|------|--------------|
| Presenter | Super admin |
| Election officer | Admin |
| Voter A | Student 1 |
| Voter B | Student 2 (USSD) |

---

## 1. Login (5 min)

**Show:** Unified sign-in — student-first copy, no role selector.

1. Open VoteBridge URL.
2. Log in as **super admin**: **Staff access** → email/username → password → OTP → biometric (if enabled).
3. Highlight **Election command center** dashboard — 5 focus cards.
4. Briefly log out; log in as **student** with index number on the default form → OTP.
5. Show student dashboard — elections and history.

**Talking point:** One sign-in page for everyone; student-first copy (index number only). Staff use **Staff access** — backend determines permissions.

---

## 2. Create election (5 min)

**Actor:** Election officer (admin)

1. **Election workspace → Create election**
2. Title: "SRC General Elections 2025 — Demo"
3. Enable web + USSD voting.
4. Save → workspace opens.

**Talking point:** Single workspace replaces fragmented pages.

---

## 3. Configure election (8 min)

**Actor:** Election officer

1. **Positions** — add President, General Secretary.
2. **Candidates** — add 2 per position; approve; show photo upload + preview.
3. **Eligibility** — search student by index; bulk add demo students.
4. **Readiness** — walk through checklist.

**Talking point:** Officer never leaves the workspace.

---

## 4. Open election (3 min)

1. **Schedule** → **Open** from lifecycle bar.
2. Show **Monitor** tab appearing.
3. Note countdown timer on overview.

---

## 5. Student voting — web (7 min)

**Actor:** Voter A (student)

1. Student login on second browser/device.
2. Elections → open demo election.
3. Browse candidate profiles.
4. **Vote** → select candidates → confirm.
5. Show **confirmation** page with reference.
6. Attempt second vote — show rejection.

**Talking point:** SVT-secured ballot; no rankings visible while open.

---

## 6. USSD voting (5 min)

**Actor:** Voter B

1. Dial USSD code (or simulate via curl callback).
2. Index + PIN → select election → vote.
3. Show confirmation SMS (if configured).
4. Show session in **USSD dashboard** (super admin URL).

**Talking point:** Same integrity rules as web.

---

## 7. Monitor election (3 min)

**Actor:** Election officer

1. **Monitor** tab — live turnout.
2. Admin dashboard turnout widget.
3. Reports → Turnout (aggregate only).

**Talking point:** Officers see turnout; students never see standings.

---

## 8. Close election (2 min)

**Actor:** Election officer

1. **Close** from lifecycle bar.
2. Redirect to Results.

---

## 9. Strong room & certification (5 min)

**Actor:** Super admin

1. **Strong room** overview.
2. Quick tour: Investigations (fraud, audit, security).
3. **Certification** → certify demo election.
4. Show integrity hash on strong room election view.

**Talking point:** Separation of duties — officer runs election, super admin certifies.

---

## 10. Publish results (2 min)

**Actor:** Super admin

1. **Results → Publication** — publish.
2. Log in as student — show published results.
3. Optional: public verify at `/verify`.

---

## Closing talking points

- Election integrity enforced at API, WebSocket, and USSD layers
- Full audit trail (operations, biometrics, votes)
- Production readiness score: 82/100 (see Phase 26 report)
- Documentation package complete for v1.0 RC1

---

## Backup slides / if something fails

| Issue | Fallback |
|-------|----------|
| OTP not received | Use pre-authenticated session |
| USSD unavailable | Show recorded callback log in audit trail |
| Biometric fails | Use student role or disable biometrics flag in staging |

---

## Related documents

- [Election Officer Guide](guides/ELECTION_OFFICER_GUIDE.md)
- [UAT scripts](uat/)
- [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
