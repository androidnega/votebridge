# VoteBridge — Technology Stack

What technologies VoteBridge uses, what each one does, and **why** it was chosen.

---

## Stack overview

| Layer | Technology | Version (approx.) |
|-------|------------|-------------------|
| Frontend framework | Vue.js | 3.5 |
| Build tool | Vite | 6 |
| State management | Pinia | 3 |
| Routing | Vue Router | 4 |
| HTTP client | Axios | 1.x |
| CSS | Tailwind CSS | 3.4 |
| Charts | ECharts | 6 |
| Face detection (browser) | MediaPipe Tasks Vision | 0.10 |
| Backend framework | Django | 5.x |
| API | Django REST Framework | 3.15+ |
| Authentication | SimpleJWT | — |
| Database | PostgreSQL | 16 |
| Cache / message bus | Redis | 7 |
| Real-time | Django Channels + channels-redis | 4 |
| ASGI server (dev) | Uvicorn | — |
| WSGI/ASGI (prod) | Gunicorn | — |
| Static files | WhiteNoise + django-vite | — |
| Images | Pillow | — |
| API docs | drf-spectacular (OpenAPI) | — |

**Not used:** Celery (no background worker in repo — jobs run synchronously or via cache).

---

## Frontend — Vue.js

### What it is
Vue is a JavaScript framework for building the user interface in the browser.

### What it does in VoteBridge
- Student dashboard and voting wizard (`StudentAppShell` — dedicated student portal)
- Admin election workspace and control room
- Super admin settings (six hubs) and strongroom terminal
- Login, OTP, and presence capture screens
- Shared list pagination via `VPagination` + `useClientListPagination` / `useServerListPagination`

### Why Vue?
- **Component-based** — reusable cards, tables, forms
- **Fast** with Vite hot reload during development
- **Good fit for SPAs** — single-page app feel without full page reloads
- **Pinia** keeps voting state (selections, SVT session) organized

### How it talks to the backend
```
Vue component → Pinia store / composable → Axios → Django REST API → JSON response
```

---

## Backend — Django

### What it is
Django is a Python web framework for building secure server applications.

### What it does in VoteBridge
- All business rules (who can vote, when, how)
- Database models and migrations
- REST API endpoints
- WebSocket consumers
- Admin audit logging

### Why Django?
- **Mature ORM** — maps Python classes to PostgreSQL tables (see [ERD.md](./ERD.md))
- **Security built-in** — CSRF, SQL injection protection, password hashing
- **Ecosystem** — DRF for APIs, Channels for WebSockets
- **Institutional fit** — well understood for enterprise/government-style apps

### Architecture pattern
```
API View (thin) → Service (logic) → Repository (data) → PostgreSQL
```

Never put business logic in Vue components or API views.

---

## Database — PostgreSQL

### What it is
A powerful open-source relational database.

### What it stores
- Users, roles, elections, candidates, votes
- SVT tokens, audit logs, results, strongroom seals
- Everything that must survive server restarts

### Why PostgreSQL (not SQLite or MongoDB)?

| Reason | Explanation |
|--------|-------------|
| **ACID transactions** | When a student submits a ballot, all votes save together or none do |
| **Foreign keys** | A vote must link to a real user, election, and candidate |
| **Concurrent voting** | Many students voting at once without corrupting data |
| **JSON support** | Result standings and audit metadata stored flexibly |
| **Production proven** | Standard choice for serious web applications |

**Layman analogy:** PostgreSQL is the **official ledger** — permanent, structured, and trustworthy.

---

## Redis

### What it is
An in-memory data store — very fast, but not the primary permanent database.

### Two jobs in VoteBridge

#### 1. Cache
Stores frequently read data for a short time:
- Feature flags (is biometrics on?)
- Maintenance mode status
- Analytics overview numbers
- OTP rate-limit counters

**Why?** Reading from memory is faster than querying PostgreSQL every time.

#### 2. WebSocket message bus (Channels)
When something happens (vote cast, alert raised), Django publishes a message to Redis. WebSocket workers pick it up and push to connected browsers.

**Why?** Multiple server processes can share live updates through Redis.

**Layman analogy:** Redis is the **notice board** — quick messages and reminders, not the permanent record.

---

## WebSockets (Django Channels)

### What it is
A persistent connection between browser and server (unlike HTTP which is request-response).

### What it does in VoteBridge
- Admin dashboard updates when votes are cast
- Security alerts appear instantly
- Notification bell updates without refresh
- Election monitor shows live activity

### How it works
```
1. Admin opens dashboard
2. Vue connects to wss://.../ws/realtime/dashboard/?token=JWT
3. Django Channels authenticates JWT
4. Consumer joins role-appropriate Redis groups
5. On vote submit, service broadcasts to election/admin groups
6. Admin UI updates (without vote totals while election is OPEN)
```

**Feed access by role:**

| Feed | Admin | Super Admin |
|------|-------|-------------|
| Admin dashboard, per-election monitor, security/fraud | ✓ | ✓ |
| Strong Room, Communications, USSD, platform Operations | ✗ | ✓ |

See [PRIVILEGES-AND-ROLES.md](./PRIVILEGES-AND-ROLES.md) for the full WebSocket matrix.

### Why WebSockets?
Polling (asking every 5 seconds) wastes resources. WebSockets push updates only when needed.

**Security:** JWT required; role checked; open-election payloads sanitized (no winners leaked).

---

## MediaPipe (browser)

### What it is
Google's machine learning library running **in the student's browser** (not on the server).

### What it does in VoteBridge
- **Pre-vote presence:** Detect if a human face is visible before taking photo
- **Staff biometrics:** Liveness challenges for admin login (separate flow)

### What it does NOT do for students
- Does not compare face to stored photo
- Does not identify the student
- Does not store embeddings for voters

**Why client-side?** Reduces server load; camera frames stay local until the student clicks "Take Photo."

---

## Django REST Framework (DRF)

### What it is
Toolkit for building REST APIs on top of Django.

### What it provides
- Serializers (JSON ↔ Python objects)
- Permission classes (role checks)
- Throttling (rate limits on SVT requests and vote casting)
- OpenAPI schema for API documentation

---

## JWT (JSON Web Tokens)

### What it is
A signed token proving the user is logged in.

### Flow
1. User completes OTP login
2. Server returns access token + refresh token
3. Vue stores tokens and sends `Authorization: Bearer ...` on each API call
4. WebSocket uses same token in query string

**Why?** Stateless API — server validates token without storing session in every request (refresh tokens tracked in `Session` model).

---

## SMS / USSD integrations

| Channel | Technology | Users |
|-------|------------|-------|
| SMS | Arkesel (configurable provider) | SVT codes, OTP |
| USSD | Arkesel callback API | Phone menu voting |
| Web | Vue + Django | Primary student experience |

USSD uses the same vote tables as web but skips presence photo capture.

---

## Development vs production

| Aspect | Development | Production |
|--------|-------------|------------|
| Cache | Local memory (LocMem) | Redis |
| Database | PostgreSQL (Docker) | PostgreSQL |
| HTTPS | Optional | Required (SSL) |
| Debug | Verbose errors | Hidden from users |
| Static files | Vite dev server | WhiteNoise + built assets |
| OTP fallback | `DEV_OTP_FALLBACK_*` for named dev accounts (development settings only) | Disabled |
| Demo data reset | `python manage.py reset_votebridge_dev --force` | Not for production use |

**Development OTP fallback:** When `DEV_OTP_FALLBACK_ENABLED` is true (development settings), named usernames can log in with a fixed OTP code instead of SMS — speeds up local testing. Never enable in production.

---

## Docker Compose (local)

```yaml
services:
  postgres:16-alpine   # port 5432
  redis:7-alpine       # port 6379
```

Run database and cache locally without installing them on the host.

---

## How the stack works together (one paragraph)

A student opens the **Vue** app in the browser. They log in; **Django** validates OTP and returns a **JWT**. They request a vote; **Django** creates an **SVT** in **PostgreSQL** and sends SMS via the provider. They verify, take a presence photo (**MediaPipe** in browser, image saved via **Django**), and submit selections. **PostgreSQL** stores immutable **Vote** rows in a transaction. **Redis** carries a live event to the admin's **WebSocket** connection. When the election closes, **Django** generates results; a Super Admin certifies; students see published standings — all served through the same **Vue + Django + PostgreSQL** stack.

---

## Related documents

- [SYSTEM-ARCHITECTURE.md](./SYSTEM-ARCHITECTURE.md) — diagrams and modules
- [ERD.md](./ERD.md) — database design
- [README.md](./README.md) — start here
