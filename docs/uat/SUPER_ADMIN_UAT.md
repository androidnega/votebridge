# Super Admin — User Acceptance Test Script

**Version:** 1.0 RC1

## Objective

Verify super admin oversight: dashboard, strong room, certification, settings, and investigations.

## Preconditions

- Super admin account
- At least one **closed** election with generated results in certification queue
- Biometrics feature flag enabled (if testing identity investigations)

## Test steps

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| 1 | Login (Staff access → email/username → password → OTP; biometric if required) | Command center dashboard | ☐ | ☐ |
| 2 | Dashboard — 5 focus cards | All cards show data or zero | ☐ | ☐ |
| 3 | Platform health link | Operations health loads | ☐ | ☐ |
| 4 | Strong room overview | Dashboard loads | ☐ | ☐ |
| 5 | Investigations → Fraud | Fraud feed loads | ☐ | ☐ |
| 6 | Investigations → Audit trail | Log tabs switch (ops/comms/USSD) | ☐ | ☐ |
| 7 | Investigations → Security timeline | Alert feed loads | ☐ | ☐ |
| 8 | Investigations → Identity | Biometric history loads | ☐ | ☐ |
| 9 | Investigations → Trusted devices | Device list loads | ☐ | ☐ |
| 10 | Election integrity → Chain of custody | Custody hub loads | ☐ | ☐ |
| 11 | Strong room → Certification link | Redirects to Results certification | ☐ | ☐ |
| 12 | Certify closed election | Status moves to certified | ☐ | ☐ |
| 13 | Publication center | Publish results | ☐ | ☐ |
| 14 | Student views published results | Results visible to student | ☐ | ☐ |
| 15 | Settings → Institution hub | Branding page opens | ☐ | ☐ |
| 16 | Settings → Security hub | Identity configuration opens | ☐ | ☐ |
| 17 | Reports → Explore security | Super admin analytics loads | ☐ | ☐ |

## Realtime tests

| # | Step | Expected result | Pass | Fail |
|---|------|-----------------|------|------|
| R1 | Open fraud investigation | WebSocket indicator connected | ☐ | ☐ |
| R2 | Navigate away | WebSocket disconnects (no leak) | ☐ | ☐ |

## Sign-off

| Tester | Date | Result |
|--------|------|--------|
| | | Pass / Fail |
