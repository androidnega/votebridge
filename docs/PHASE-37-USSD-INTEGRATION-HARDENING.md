# Phase 37 — USSD Integration Hardening & Endpoint Configuration

**Type:** USSD operational hardening (no flow changes)  
**Date:** June 2026  
**Baseline:** Arkesel callback JSON alignment (`2bae678`)

---

## A. Completion Report

Phase 37 improves USSD integration operability: configurable public callback URLs, health visibility, callback audit enrichment, and response validation — without changing the USSD voting flow.

### Delivered

| Area | Status |
|------|--------|
| `PUBLIC_BASE_URL` environment variable | ✅ |
| `core/public_urls.py` URL builder | ✅ |
| `UssdConfigService` (callback URL, environment, health) | ✅ |
| `UssdAuditService` (callback audit enrichment) | ✅ |
| Response validation before Arkesel JSON return | ✅ |
| `GET /api/v1/ussd/integration/` | ✅ |
| Voting Channels settings UI (config + health cards) | ✅ |
| USSD dashboard callback URL from config | ✅ |
| Migration `0002_callback_audit_fields` | ✅ |
| Documentation updates | ✅ |

---

## B. Architecture Compliance

**No USSD business logic or voting flow changes.**

| Layer | Phase 37 changes |
|-------|------------------|
| Views | `UssdCallbackView` audit wrapper; `UssdIntegrationView` |
| Services | `ussd_config_service`, `ussd_audit_service`; controller validation |
| Repositories | Reused `USSDRequestLogRepository` |
| Models | Extended `USSDRequestLog` audit fields |

Flow remains: **Callback View → Controller → Flow Service → domain services**.

---

## C. Database Changes

Migration `ussd.0002_callback_audit_fields`:

| Field | Purpose |
|-------|---------|
| `request_payload` | Full inbound callback payload |
| `response_payload` | Arkesel JSON response body |
| `http_status` | HTTP status returned to gateway |
| `provider_user_id` | Arkesel `userID` from request |

---

## D. APIs

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/ussd/callback/` | Unchanged path; enriched audit + validation |
| `GET /api/v1/ussd/integration/` | Callback config + health (Super Admin / Admin read) |
| `GET /api/v1/ussd/dashboard/` | Now includes `callback_url`, `health` |

---

## E. Vue Components

- `VotingChannelsSettingsView` — USSD callback configuration + health cards
- `UssdDashboardView` — displays configured callback URL and health status
- `ussdApi.getIntegration()` — fetches integration metadata

---

## F. Security Impact

- Callback secret enforcement unchanged (`ARKESEL_USSD_CALLBACK_SECRET`)
- Audit payloads stored server-side only; not exposed on public callback
- Integration endpoint requires authenticated Super Admin / Admin (read)

---

## G. Performance Impact

- Health reachability probe: optional GET with 3s timeout when `PUBLIC_BASE_URL` is set
- Audit enrichment: single UPDATE on latest `USSDRequestLog` per callback

---

## H. Responsive Design Notes

- Voting Channels USSD cards stack on mobile; two-column on `xl`
- Callback URL uses `break-all` for long tunnel hostnames

---

## I. Testing Strategy

```bash
python manage.py test apps.ussd.tests
```

New tests:

- `test_integration.py` — config service, audit service, validation, integration API, callback audit

---

## J. Deployment Notes

1. Set `PUBLIC_BASE_URL` to your public HTTPS origin.
2. Run `python manage.py migrate ussd`.
3. Register `{PUBLIC_BASE_URL}/api/v1/ussd/callback/` in Arkesel.
4. Verify via **Settings → Voting channels**.

### Development (Cloudflare Tunnel)

```bash
cloudflared tunnel --url http://localhost:8000
PUBLIC_BASE_URL=https://<subdomain>.trycloudflare.com
```

---

## Configuration

| Variable | Example | Purpose |
|----------|---------|---------|
| `PUBLIC_BASE_URL` | `https://votebridge.example.edu` | External origin for generated URLs |
| `ARKESEL_USSD_USER_ID` | `VOTEBRIDGE` | Arkesel `userID` in responses |

Callback URL is always: `build_public_url("/api/v1/ussd/callback/")`

---

## Callback Verification Process

1. Configure `PUBLIC_BASE_URL`.
2. Open Voting Channels settings — confirm callback URL.
3. Check health card reachability and last callback metrics.
4. Send test POST (JSON or form-urlencoded).
5. Confirm `USSDRequestLog` has `request_payload`, `response_payload`, `http_status`, `duration_ms`.

---

## Response Validation

Before returning to Arkesel, the controller validates:

- `sessionID`, `userID`, `msisdn`, `message`, `continueSession`
- `continueSession` must be boolean

On failure: application error logged; generic `END` system error JSON returned (HTTP 200).
