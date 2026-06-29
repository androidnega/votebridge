# VoteBridge — Production Checklist

**Version:** 1.0 RC1  
Use this checklist before go-live.

---

## Server preparation

- [ ] Production server provisioned (CPU, RAM, disk sized for expected voters)
- [ ] OS packages updated; firewall configured
- [ ] Non-root service user created for VoteBridge
- [ ] Timezone set to institution local time (UTC storage in DB)
- [ ] `DJANGO_SETTINGS_MODULE=config.settings.production` set for all processes

---

## SSL / HTTPS

- [ ] TLS certificate installed (Let's Encrypt or institutional CA)
- [ ] `SECURE_SSL_REDIRECT=True` in production
- [ ] HTTP → HTTPS redirect at load balancer or Nginx
- [ ] HSTS enabled and tested
- [ ] Cloudflare SSL mode: Full (strict) if proxied

---

## PostgreSQL

- [ ] PostgreSQL 14+ running with dedicated database
- [ ] Strong `POSTGRES_PASSWORD` set
- [ ] `python manage.py migrate` completed
- [ ] Connection pooling configured (`POSTGRES_CONN_MAX_AGE`)
- [ ] Daily `pg_dump` backup scheduled
- [ ] Restore procedure tested

---

## Redis

- [ ] Redis running and reachable at `REDIS_URL`
- [ ] Separate DB index for Channels (`CHANNELS_REDIS_URL`)
- [ ] Persistence policy defined (AOF/RDB for production)
- [ ] Memory limit configured

---

## Static files

- [ ] `cd frontend && npm ci && npm run build`
- [ ] `python manage.py collectstatic --noinput`
- [ ] WhiteNoise serving static files verified
- [ ] No 404 on `/static/` assets

---

## Media uploads

- [ ] `MEDIA_ROOT` directory created with correct permissions
- [ ] Nginx `location /media/` configured OR S3 storage enabled
- [ ] Candidate photo upload tested end-to-end

---

## ASGI / Channels

- [ ] Uvicorn (or Daphne) running with production settings
- [ ] WebSocket upgrade works through Nginx/Cloudflare
- [ ] Redis channel layer connected
- [ ] Real-time dashboard feed verified

---

## Celery / notification queue

- [ ] Decision documented: cron vs Celery worker
- [ ] If cron: schedule `POST /api/v1/notifications/queue/process/`
- [ ] SMS provider credentials configured and test send successful
- [ ] Email SMTP or provider configured

---

## Cloudflare (if used)

- [ ] DNS proxied correctly
- [ ] WebSockets enabled
- [ ] `DJANGO_ALLOWED_HOSTS` includes production domain
- [ ] Rate limiting / WAF on auth endpoints (optional)
- [ ] Tunnel disabled for production (use only for staging)

---

## Arkesel — SMS

- [ ] `ARKESEL_API_KEY` and `ARKESEL_SENDER_ID` set
- [ ] Test OTP delivery to real handset
- [ ] Sender ID approved by carrier

---

## Arkesel — USSD

- [ ] Callback URL registered: `https://domain/api/v1/ussd/callback/`
- [ ] `ARKESEL_USSD_CALLBACK_SECRET` set (mandatory)
- [ ] `X-Arkesel-Secret` header verified in test callback
- [ ] USSD short code active
- [ ] End-to-end vote test on physical device

---

## Security

- [ ] `DJANGO_SECRET_KEY` unique and secret
- [ ] `DJANGO_DEBUG=False`
- [ ] Default/demo accounts disabled or passwords rotated
- [ ] Super admin biometrics enrolled (if policy requires)
- [ ] Legacy `/dashboard/*` Django pages blocked at Nginx (optional)
- [ ] API docs (`/api/docs/`) access restricted if required

---

## Monitoring & logging

- [ ] `LOG_LEVEL=INFO` (or WARNING) in production
- [ ] Log rotation configured
- [ ] External uptime monitor on `/health/`
- [ ] Alerting on disk, CPU, DB connections
- [ ] Operations health dashboard accessible to super admin

---

## Backups & disaster recovery

- [ ] Database backup schedule + off-site copy
- [ ] Media backup schedule
- [ ] Documented RTO/RPO
- [ ] Restore drill completed once

---

## Final smoke test

- [ ] Officer: create → open → close election
- [ ] Student: web vote with confirmation
- [ ] USSD: vote with confirmation SMS
- [ ] Super admin: certify and publish results
- [ ] All 70 backend tests pass in CI/staging

---

**Sign-off**

| Role | Name | Date |
|------|------|------|
| Technical lead | | |
| Election commission | | |
| Institution IT | | |
