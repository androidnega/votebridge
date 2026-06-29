# Student — User Acceptance Test Script

**Version:** 1.0 RC1

## Objective

Verify a student can authenticate, view elections, vote once, receive confirmation, and see vote history.

## Preconditions

- Demo student account exists (run `seed_demo_users` in dev)
- At least one election is **open** with student on eligibility roll
- Web voting enabled on election

## Test steps

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| 1 | Open login page | Single identifier field, no role selector | ☐ | ☐ |
| 2 | Enter index number + password | OTP screen shown | ☐ | ☐ |
| 3 | Enter valid OTP | Redirect to student dashboard | ☐ | ☐ |
| 4 | Sidebar shows Elections, Notifications, Profile | Correct nav for student role | ☐ | ☐ |
| 5 | Open Elections list | Open election visible | ☐ | ☐ |
| 6 | Open election detail | Candidate profiles visible, no vote totals | ☐ | ☐ |
| 7 | Navigate to Vote tab | Ballot wizard loads | ☐ | ☐ |
| 8 | Select candidates for all positions | Selections recorded | ☐ | ☐ |
| 9 | Submit ballot | Success; redirect to confirmation | ☐ | ☐ |
| 10 | Confirmation page shows reference | Confirmation code displayed | ☐ | ☐ |
| 11 | Return to Vote tab | Vote disabled or shows already voted | ☐ | ☐ |
| 12 | Attempt second vote (API or UI) | Rejected — duplicate vote | ☐ | ☐ |
| 13 | Dashboard vote history | Election listed as voted | ☐ | ☐ |
| 14 | Log out and log back in | Session cleared; can log in again | ☐ | ☐ |

## Negative tests

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| N1 | Student opens `/settings` | Forbidden page | ☐ | ☐ |
| N2 | Vote on closed election | Error — election not open | ☐ | ☐ |
| N3 | Vote when not on eligibility roll | Error — not eligible | ☐ | ☐ |

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | Pass / Fail |
