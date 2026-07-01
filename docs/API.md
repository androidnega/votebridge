# VoteBridge API Documentation

**Version:** 1.0 RC1  
**Base URL:** `/api/v1/`

---

## Interactive documentation

| Format | URL |
|--------|-----|
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI 3 schema | `/api/schema/` |

Generate a static export:

```bash
cd backend
python manage.py spectacular --file ../docs/openapi-schema.yaml
```

---

## Authentication

VoteBridge uses **JWT Bearer tokens** (SimpleJWT).

### 1. Login

```http
POST /api/v1/accounts/auth/login/
Content-Type: application/json

{
  "identifier": "BC/ITS/24/047",
  "password": "<password>"
}
```

**Response (OTP required):**

```json
{
  "success": true,
  "data": {
    "requires_otp": true,
    "otp_session_id": "<uuid>"
  }
}
```

### 2. Verify OTP

```http
POST /api/v1/accounts/auth/otp/verify/
Content-Type: application/json

{
  "otp_session_id": "<uuid>",
  "code": "123456"
}
```

**Response (success — v1.0 default, biometrics disabled):**

```json
{
  "success": true,
  "data": {
    "tokens": { "access": "<jwt>", "refresh": "<jwt>" },
    "user_uuid": "...",
    "session_uuid": "...",
    "redirect_path": "/dashboard/student"
  }
}
```

**Response (when `BIOMETRIC_AUTH_ENABLED=True` and privileged user requires verification):**

```json
{
  "success": true,
  "data": {
    "requires_biometric": true,
    "pending_auth_token": "...",
    "challenge": { "challenge_id": "...", "challenge_type": "blink_twice" }
  }
}
```

> Biometric authentication has been deferred for VoteBridge v1.0 (`BIOMETRIC_AUTH_ENABLED=False`) and remains available for future activation via environment variable plus the `future_biometrics` feature flag.

**Response (legacy success shape):**

### 3. Authenticated requests

```http
GET /api/v1/elections/
Authorization: Bearer <jwt-access>
```

### 4. Refresh token

```http
POST /api/v1/accounts/auth/token/refresh/
Content-Type: application/json

{ "refresh": "<jwt-refresh>" }
```

---

## API modules

| Prefix | Description | Typical roles |
|--------|-------------|---------------|
| `/accounts/` | Auth, users, roles | All |
| `/elections/` | Elections, positions, candidates, eligibility | Admin+ read; write admin/SA |
| `/voting/` | Ballot, submit, history | Student, candidate |
| `/security/` | SVT, monitoring, audit | Student (SVT); admin (monitoring) |
| `/results/` | Generate, certify, publish | Admin read; SA certify/publish |
| `/strongroom/` | Integrity dashboard | Admin, SA |
| `/fraud/` | Fraud cases | Admin, SA |
| `/notifications/` | Templates, deliveries | Admin, SA |
| `/ussd/` | Callback + monitoring | Public callback; SA monitor |
| `/dashboard/` | Role dashboards | Authenticated |
| `/analytics/` | Reports data | Admin, SA |
| `/operations/` | System operations | Admin, SA |
| `/system/` | Configuration | SA |
| `/biometrics/` | Enrollment, verification | SA, privileged |
| `/trusted-devices/` | Device trust | Admin, SA |

---

## Example: Request SVT and vote

### Request SVT

```http
POST /api/v1/security/elections/<election-uuid>/svt/request/
Authorization: Bearer <access>
```

### Validate SVT

```http
POST /api/v1/security/elections/<election-uuid>/svt/validate/
Authorization: Bearer <access>
Content-Type: application/json

{ "svt_code": "<plain-code-from-request>" }
```

### Get ballot

```http
GET /api/v1/voting/elections/<election-uuid>/ballot/
Authorization: Bearer <access>
```

### Submit vote

```http
POST /api/v1/voting/elections/<election-uuid>/submit/
Authorization: Bearer <access>
Content-Type: application/json

{
  "selections": [
    { "position_uuid": "...", "candidate_uuid": "..." }
  ],
  "svt_code": "<validated-svt>"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "vote_id": "...",
    "confirmation_code": "...",
    "election_title": "SRC General Elections 2025"
  }
}
```

---

## Permissions model

Permissions are enforced server-side via DRF permission classes (`CanVote`, `CanManageElections`, `IsSuperAdmin`, etc.). The OpenAPI schema annotates endpoints; refer to Swagger for per-route requirements.

**Election integrity:** While an election is `open`, student-facing endpoints and WebSocket payloads exclude rankings, vote totals, and winners.

---

## Error responses

```json
{
  "success": false,
  "error": {
    "code": "permission_denied",
    "message": "Admin or Super Admin access required."
  }
}
```

HTTP status codes: 400 validation, 401 unauthenticated, 403 forbidden, 404 not found, 429 throttled.

---

## Rate limits

| Scope | Limit |
|-------|-------|
| Anonymous | 100/hour |
| Authenticated | 1000/hour |
| Login | 5/minute |
| OTP | 3/minute |
| SVT request | 10/hour |
| Vote cast | 20/hour |

---

## WebSocket endpoints

Connect with JWT: `ws://host/ws/realtime/dashboard/?token=<access>`

| Path | Feed |
|------|------|
| `/ws/realtime/dashboard/` | Dashboard aggregates |
| `/ws/realtime/elections/<uuid>/` | Election status |
| `/ws/realtime/security/` | Security alerts |
| `/ws/realtime/fraud/` | Fraud feed |
| `/ws/realtime/results/` | Results queues |
| `/ws/realtime/strongroom/` | Integrity events |

---

## Related documents

- [Deployment Guide](guides/DEPLOYMENT_GUIDE.md)
- [DEPRECATED.md](DEPRECATED.md) — legacy endpoints
