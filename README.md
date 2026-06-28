# VoteBridge

Secure Real-Time Campus E-Voting System.

## Stack

- **Backend:** Django 5, Django REST Framework, Django Channels
- **Database:** PostgreSQL
- **Cache / Pub-Sub:** Redis
- **Frontend:** Vite, Tailwind CSS, Alpine.js
- **Integrations (future):** Arkesel SMS, Arkesel USSD

## Project Structure

```
VoteBridge/
├── backend/                 # Django project
│   ├── config/              # Settings, URLs, ASGI/WSGI
│   ├── apps/                # Domain applications
│   ├── core/                # Shared exceptions & handlers
│   ├── templates/           # Django templates
│   └── manage.py
├── frontend/                # Vite + Tailwind + Alpine.js
├── requirements/            # Python dependencies
├── docker-compose.yml       # PostgreSQL + Redis
└── .env.example             # Environment template
```

## Quick Start

### 1. Infrastructure

```bash
docker compose up -d
```

### 2. Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/development.txt
cp .env.example .env
```

### 3. Database

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Run Backend

```bash
cd backend
python manage.py runserver
```

For WebSocket support (Channels):

```bash
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```

## Cloudflare Quick Tunnel (development)

Use [Cloudflare Quick Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/) to expose your local backend for testing on another device or share a temporary URL.

1. Start infrastructure, backend, and frontend as usual (backend must listen on `0.0.0.0:8000`).
2. In a separate terminal, run:

```bash
cloudflared tunnel --url http://localhost:8000
```

3. Open the printed `https://<random>.trycloudflare.com` URL.

**ALLOWED_HOSTS:** With `DJANGO_SETTINGS_MODULE=config.settings.development` (default local setup), VoteBridge automatically allows Cloudflare Quick Tunnel hostnames (`.trycloudflare.com`) while keeping `localhost` and `127.0.0.1` working. Production settings do **not** add tunnel suffixes — set explicit hosts via `DJANGO_ALLOWED_HOSTS` only.

To allow an additional tunnel domain in development, append a leading-dot suffix to `.env`:

```bash
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,.trycloudflare.com
```

Entries such as `*.trycloudflare.com` are normalized to `.trycloudflare.com`.

**Frontend via tunnel:** The Vite dev server proxies `/api` and `/ws` to port 8000. For full UI over a tunnel, either tunnel port `5173` separately or build the frontend and serve it through Django static files.

## Environment

Copy `.env.example` to `.env` and configure:

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hosts; `.suffix` matches subdomains (dev adds `.trycloudflare.com` automatically) |
| `POSTGRES_*` | PostgreSQL connection |
| `REDIS_URL` | Redis cache connection |
| `CHANNELS_REDIS_URL` | Redis channel layer |
| `VITE_DEV_MODE` | Enable Vite HMR in development |

## Settings Modules

- `config.settings.development` — local development (default)
- `config.settings.production` — production deployment

## API Health Check

```
GET /health/
```

## Apps

| App | Purpose |
|---|---|
| accounts | User management & authentication |
| elections | Election configuration |
| candidates | Candidate management |
| voting | Ballot casting |
| security | Security controls |
| fraud | Fraud detection |
| results | Real-time results |
| strongroom | Secure vote storage |
| notifications | SMS/email notifications |
| ussd | USSD voting channel |
| dashboard | Admin dashboard |
