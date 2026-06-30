# VoteBridge — USSD Guide

**Audience:** Super administrators and DevOps  
**Version:** 1.0 RC1

---

## 1. Overview

VoteBridge supports **Arkesel USSD** for voting without smartphones. The flow mirrors web voting: authenticate → select election → ballot → confirm → SVT-sealed submission.

**Callback endpoint:** `POST /api/v1/ussd/callback/`

---

## 2. Architecture

```
Mobile network → Arkesel USSD gateway → VoteBridge callback
                                              ↓
                                    UssdControllerService
                                              ↓
                                    UssdFlowService (state machine)
                                              ↓
                              Auth / Ballot / vote_service.submit_ballot
```

Sessions persist in `USSDSession` with a configurable timeout (default 5 minutes).

---

## 3. Environment variables

```bash
PUBLIC_BASE_URL=https://votebridge.example.edu
ARKESEL_USSD_USER_ID=VOTEBRIDGE
ARKESEL_USSD_CALLBACK_SECRET=<strong-random-secret>   # REQUIRED in production
USSD_SESSION_TIMEOUT_MINUTES=5
USSD_RATE_LIMIT_PER_MSISDN=30
```

`PUBLIC_BASE_URL` is the externally reachable HTTPS origin used to generate callback URLs for Arkesel and the Voting Channels settings UI. Do not hardcode callback URLs in application code.

Also configure SMS for confirmations:

```bash
ARKESEL_API_KEY=
ARKESEL_SENDER_ID=
ARKESEL_SMS_URL=https://sms.arkesel.com/api/v2/sms/send
```

---

## 4. Deployment

### 4.1 Public HTTPS URL

Arkesel must reach your callback over HTTPS. Set `PUBLIC_BASE_URL` and register:

```
{PUBLIC_BASE_URL}/api/v1/ussd/callback/
```

Example production value:

```
PUBLIC_BASE_URL=https://votebridge.example.edu
```

### 4.2 Development with Cloudflare Tunnel

1. Start VoteBridge locally (`uvicorn` on port 8000).
2. Run Cloudflare Quick Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

3. Copy the printed `https://<subdomain>.trycloudflare.com` URL into `.env`:

```bash
PUBLIC_BASE_URL=https://<subdomain>.trycloudflare.com
```

4. Restart Django so settings reload.
5. Open **Settings → Voting channels** and confirm the generated callback URL.
6. Register that callback URL in the Arkesel USSD dashboard.

Development settings automatically allow `.trycloudflare.com` hosts when using `config.settings.development`.

### 4.3 Production DNS / TLS

1. Point DNS to your origin or use Cloudflare Tunnel for staging.
2. Ensure `DJANGO_ALLOWED_HOSTS` includes your domain.
3. Set `SECURE_PROXY_SSL_HEADER` (configured in production settings).
4. Whitelist Arkesel IPs if using firewall rules.

### 4.4 Callback authentication

When `ARKESEL_USSD_CALLBACK_SECRET` is set, requests must include header:

```
X-Arkesel-Secret: <your-secret>
```

**Never deploy production without this secret.**

---

## 5. Session flow

| Step | User sees | Backend state |
|------|-----------|---------------|
| 1 | Welcome menu | `WELCOME` |
| 2 | Main menu (vote, verify, help) | `MAIN_MENU` |
| 3 | Index + PIN entry | `AUTH` |
| 4 | Election list | `ELECTION_SELECT` |
| 5 | Per-position candidate pick | `BALLOT` |
| 6 | Review & confirm | `CONFIRM` |
| 7 | Success message | `END` |

**Session recovery:** State stored in `USSDSession.state_data`. Timeout returns user to welcome.

**Duplicate vote prevention:** Same `vote_service` as web — one vote per user per election.

---

## 6. Supported payload formats

Arkesel **form-encoded** (sessionId, phoneNumber, text) and **JSON** (sessionID, msisdn, userData, newSession) are both handled by `UssdControllerService`.

---

## 7. Testing

### 7.1 Automated tests

```bash
cd backend
python manage.py test apps.ussd
python manage.py test tests.integration.test_phase22_workflows
```

### 7.2 Manual callback test

```bash
curl -X POST https://localhost:8000/api/v1/ussd/callback/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-Arkesel-Secret: your-secret" \
  -d "sessionId=test-001&phoneNumber=233241234567&text="
```

### 7.3 Monitoring UI

- **USSD dashboard:** `/ussd` (super admin, direct URL)
- **Sessions:** `/ussd/sessions`
- **Logs:** Strong room → Audit trail → USSD tab, or `/platform/logs?tab=ussd`

WebSocket: `ws/realtime/ussd/`

### 7.4 Callback verification

1. Set `PUBLIC_BASE_URL` in `.env`.
2. Open **Settings → Voting channels** (Super Admin).
3. Confirm the **USSD callback configuration** card shows the full HTTPS callback URL.
4. Review **USSD callback health** — reachability, last callback timestamp, HTTP status, and duration.
5. Send a manual `curl` request (see §7.2) and confirm the health card updates.
6. Verify Arkesel receives `application/json` with `sessionID`, `userID`, `msisdn`, `message`, and `continueSession`.

Operational API: `GET /api/v1/ussd/integration/`

---

## 8. Production configuration checklist

- [ ] `PUBLIC_BASE_URL` configured
- [ ] HTTPS callback URL registered with Arkesel
- [ ] `ARKESEL_USSD_CALLBACK_SECRET` set
- [ ] Election has `allow_ussd_voting` enabled
- [ ] Student PINs provisioned (USSD auth uses index + PIN, not OTP)
- [ ] SMS provider configured for confirmation messages
- [ ] Redis available (rate limiting and session cache in production)
- [ ] Load test callback endpoint under expected concurrent sessions

---

## 9. Troubleshooting

| Symptom | Check |
|---------|-------|
| Empty menu | Election not open or no eligible elections |
| Auth failed | Index/PIN mismatch; user inactive |
| Session expired | Increase timeout or shorten ballot |
| 403 on callback | Missing or wrong `X-Arkesel-Secret` |
| Vote not recorded | Check USSD logs and strongroom seal |

---

## Related documents

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [UAT script](../uat/USSD_UAT.md)
- Phase 22 report: `docs/PHASE-22-USSD-SMS-REPORT.md`
