# VoteBridge — Deployment Guide

**Version:** 1.0 RC1

---

## 1. Prerequisites

| Component | Version |
|-----------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 14+ |
| Redis | 6+ |
| Nginx (recommended) | 1.18+ |

---

## 2. Environment variables

Copy `.env.example` to `.env` at project root.

### Django

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<long-random-secret>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=votebridge.example.com,.votebridge.example.com
```

### Database

```bash
POSTGRES_DB=votebridge
POSTGRES_USER=votebridge
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

### Redis & Channels

```bash
REDIS_URL=redis://127.0.0.1:6379/0
CHANNELS_REDIS_URL=redis://127.0.0.1:6379/1
```

### JWT & sessions

```bash
JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7
AUTH_SESSION_LIFETIME_DAYS=7
```

### OTP & SVT

```bash
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=10
SVT_EXPIRY_MINUTES=30
```

### Arkesel (SMS & USSD)

```bash
ARKESEL_API_KEY=
ARKESEL_SENDER_ID=
ARKESEL_SMS_URL=https://sms.arkesel.com/api/v2/sms/send
ARKESEL_USSD_USER_ID=VOTEBRIDGE
ARKESEL_USSD_CALLBACK_SECRET=<required-for-production>
USSD_SESSION_TIMEOUT_MINUTES=5
```

### Email

```bash
DEFAULT_FROM_EMAIL=noreply@your-institution.edu.gh
```

---

## 3. Infrastructure setup

### 3.1 Docker (PostgreSQL + Redis)

```bash
docker compose up -d
```

### 3.2 Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/production.txt
```

### 3.3 Database migrations

```bash
cd backend
python manage.py migrate
python manage.py seed_demo_data   # development/staging only
```

### 3.4 Static files

```bash
cd frontend && npm ci && npm run build
cd ../backend
python manage.py collectstatic --noinput
```

WhiteNoise serves `staticfiles/` including `frontend/dist`.

### 3.5 Media files

Candidate photos and uploads go to `media/`. In production (`DEBUG=False`), serve via Nginx:

```nginx
location /media/ {
    alias /var/www/votebridge/media/;
}
```

Or use S3-compatible object storage (configure in Settings → Advanced → Storage).

---

## 4. ASGI (WebSockets)

VoteBridge requires ASGI for real-time dashboards and live feeds.

```bash
cd backend
export DJANGO_SETTINGS_MODULE=config.settings.production
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
```

**Important:** Default `manage.py` uses development settings. Always set `DJANGO_SETTINGS_MODULE` for production ASGI.

WebSocket paths: `/ws/realtime/*` (JWT authenticated).

---

## 5. Nginx reverse proxy

```nginx
upstream votebridge {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl http2;
    server_name votebridge.example.com;

    ssl_certificate     /etc/ssl/certs/votebridge.crt;
    ssl_certificate_key /etc/ssl/private/votebridge.key;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/votebridge/staticfiles/;
    }

    location /media/ {
        alias /var/www/votebridge/media/;
    }

    location /ws/ {
        proxy_pass http://votebridge;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://votebridge;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 6. Cloudflare

1. Proxy DNS through Cloudflare (orange cloud).
2. SSL mode: **Full (strict)** with origin certificate.
3. Add `.trycloudflare.com` to `ALLOWED_HOSTS` only for dev tunnels.
4. WebSockets: enable in Cloudflare network settings.
5. Rate limiting: optional WAF rules on `/api/v1/accounts/auth/login/`.

See `README.md` for Quick Tunnel development instructions.

---

## 7. HTTPS

Production settings enable:

- `SECURE_SSL_REDIRECT`
- Secure session and CSRF cookies
- HSTS headers

Ensure Nginx passes `X-Forwarded-Proto: https`.

---

## 8. Celery (optional)

VoteBridge queues notifications synchronously by default. For production scale:

1. Install Celery + Redis broker.
2. Schedule `POST /api/v1/notifications/queue/process/` via cron, or implement Celery worker calling `CommunicationService.process_queue()`.

Not included in RC1 — document as operational follow-up.

---

## 9. Backups

| Asset | Method |
|-------|--------|
| PostgreSQL | `pg_dump` daily; Settings → Advanced → Backup UI |
| Media | Filesystem snapshot or S3 replication |
| Redis | Ephemeral — no backup required for cache |
| Configuration | Export system settings revisions via API |

---

## 10. Health & monitoring

| Endpoint | Purpose |
|----------|---------|
| `GET /health/` | Basic liveness |
| `GET /api/v1/operations/health/` | Detailed system health (super admin) |

Configure external monitoring to poll `/health/` and alert on non-200.

---

## 11. Post-deploy verification

```bash
python manage.py check
python manage.py test
curl -s https://votebridge.example.com/health/
curl -s https://votebridge.example.com/api/schema/ | head
```

See [RELEASE_CHECKLIST.md](../RELEASE_CHECKLIST.md) and [PRODUCTION_CHECKLIST.md](../PRODUCTION_CHECKLIST.md).

---

## 12. API documentation

- Swagger UI: `https://your-domain/api/docs/`
- ReDoc: `https://your-domain/api/redoc/`
- OpenAPI schema: `https://your-domain/api/schema/`

See [API.md](../API.md).
