# Election Officer — User Acceptance Test Script

**Version:** 1.0 RC1

## Objective

Verify an election officer can complete the full election lifecycle within the Election workspace without broken workflows.

## Preconditions

- Admin account with election management permissions
- No blocking feature flags
- Super admin has configured institution branding (optional)

## Test steps

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| 1 | Login as admin | Admin dashboard loads | ☐ | ☐ |
| 2 | Election workspace → Create election | Form saves; redirect to workspace | ☐ | ☐ |
| 3 | Positions tab — add 2 positions | Positions listed | ☐ | ☐ |
| 4 | Candidates tab — add + approve candidates | Approved count updates | ☐ | ☐ |
| 5 | Candidates — upload photo + preview | Photo visible in preview | ☐ | ☐ |
| 6 | Eligibility — search by index, add student | Student on roll | ☐ | ☐ |
| 7 | Eligibility — bulk add | Multiple students added | ☐ | ☐ |
| 8 | Readiness tab | Checklist loads; note blocking items | ☐ | ☐ |
| 9 | Schedule election (lifecycle bar) | Status → scheduled | ☐ | ☐ |
| 10 | Open election | Status → open; Monitor tab appears | ☐ | ☐ |
| 11 | Monitor tab | Turnout widget loads (no rankings) | ☐ | ☐ |
| 12 | Pause election | Status → paused; students cannot vote | ☐ | ☐ |
| 13 | Resume election | Status → open | ☐ | ☐ |
| 14 | Close election | Status → closed; redirect to Results | ☐ | ☐ |
| 15 | Edit election (draft only) | Edit modal saves changes | ☐ | ☐ |

## Permission tests

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| P1 | Admin opens `/strongroom` | Forbidden | ☐ | ☐ |
| P2 | Admin opens `/settings` | Forbidden | ☐ | ☐ |
| P3 | Admin opens `/results/certification` | Forbidden | ☐ | ☐ |

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | Pass / Fail |
