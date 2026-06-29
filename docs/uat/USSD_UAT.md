# USSD — User Acceptance Test Script

**Version:** 1.0 RC1

## Objective

Verify USSD authentication, ballot retrieval, vote casting, confirmation, and duplicate prevention.

## Preconditions

- Election open with `allow_ussd_voting=True`
- Student on eligibility with USSD PIN configured
- `ARKESEL_USSD_CALLBACK_SECRET` set in test environment
- Arkesel sandbox or curl simulation available

## Test steps

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| 1 | Send empty callback (new session) | CON welcome menu | ☐ | ☐ |
| 2 | Select vote option | Prompt for index number | ☐ | ☐ |
| 3 | Enter valid index + PIN | Election list shown | ☐ | ☐ |
| 4 | Select election | Position/candidate menus | ☐ | ☐ |
| 5 | Complete all positions | Review screen | ☐ | ☐ |
| 6 | Confirm vote | END success message | ☐ | ☐ |
| 7 | SMS confirmation (if configured) | SMS received | ☐ | ☐ |
| 8 | Attempt second vote same session | Already voted message | ☐ | ☐ |
| 9 | New session — vote again same election | Rejected — duplicate | ☐ | ☐ |
| 10 | USSD dashboard (super admin) | Session appears in monitor | ☐ | ☐ |
| 11 | Audit trail USSD tab | Request logged | ☐ | ☐ |

## Session & security tests

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| S1 | Wait past session timeout | Session expired; restart welcome | ☐ | ☐ |
| S2 | Callback without secret header | 403 Forbidden | ☐ | ☐ |
| S3 | Invalid PIN | Auth failure message; no ballot | ☐ | ☐ |

## Automated regression

```bash
cd backend
python manage.py test apps.ussd tests.integration.test_phase22_workflows
```

| Result | Pass | Fail |
|--------|------|------|
| All tests pass | ☐ | ☐ |

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | Pass / Fail |
