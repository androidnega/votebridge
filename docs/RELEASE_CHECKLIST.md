# VoteBridge — Release Checklist

**Version:** 1.0 RC1  
Complete before tagging `v1.0.0-rc1`.

---

## Backend verification

- [ ] `python manage.py check` — 0 issues
- [ ] `python manage.py test` — all tests pass (70/70)
- [ ] Migrations applied on clean database
- [ ] `seed_demo_data` runs without error (staging)
- [ ] OpenAPI schema generates: `python manage.py spectacular --file docs/openapi-schema.yaml`
- [ ] `/health/` returns 200
- [ ] JWT login → OTP → token flow works
- [ ] Election lifecycle API: schedule, open, pause, close, archive
- [ ] SVT request → validate → vote → submit integration path
- [ ] USSD callback accepts test payload

---

## Frontend verification

- [ ] `npm ci && npm run build` succeeds
- [ ] No console errors on login page
- [ ] All sidebar routes load for each role (student, admin, super_admin)
- [ ] Election workspace tabs functional
- [ ] Vote wizard → confirmation flow works
- [ ] Strong room investigations tabs load
- [ ] Settings hubs link to configuration pages
- [ ] Reports tabs and explore drill-downs load
- [ ] Mobile responsive check (375px width)
- [ ] Forbidden page shown for unauthorized deep links

---

## Database verification

- [ ] All migrations in repo applied
- [ ] No pending model changes (`makemigrations --check`)
- [ ] Indexes present on high-traffic tables (votes, sessions, audit logs)
- [ ] Demo seed creates elections, candidates, votes, fraud cases

---

## Security verification

- [ ] Student cannot access `/settings`, `/strongroom`, `/operations`
- [ ] Admin cannot access super_admin-only routes (403 or redirect)
- [ ] OPEN election: student API returns no vote totals/rankings
- [ ] WebSocket payloads sanitized for open elections
- [ ] USSD callback rejects missing secret (when configured)
- [ ] Biometric failure audit logs persist
- [ ] Rate limiting active on login and OTP

---

## Documentation verification

- [ ] [Administrator Guide](guides/ADMINISTRATOR_GUIDE.md)
- [ ] [Election Officer Guide](guides/ELECTION_OFFICER_GUIDE.md)
- [ ] [Student Guide](guides/STUDENT_GUIDE.md)
- [ ] [Super Admin Guide](guides/SUPER_ADMIN_GUIDE.md)
- [ ] [USSD Guide](guides/USSD_GUIDE.md)
- [ ] [Deployment Guide](guides/DEPLOYMENT_GUIDE.md)
- [ ] [API.md](API.md) + `/api/docs/` live
- [ ] [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- [ ] [DEMO_SCRIPT.md](DEMO_SCRIPT.md)
- [ ] [VERSION_1.0_SUMMARY.md](VERSION_1.0_SUMMARY.md)
- [ ] UAT scripts in `docs/uat/`

---

## Deployment verification

- [ ] Production settings module tested
- [ ] `collectstatic` output includes Vue dist
- [ ] ASGI WebSocket tested behind Nginx
- [ ] Redis channel layer connected in staging
- [ ] Media serving strategy documented and tested
- [ ] Environment variables documented in `.env.example`
- [ ] Backup restore tested once

---

## Release artifacts

- [ ] Git tag: `v1.0.0-rc1`
- [ ] Changelog or VERSION summary published
- [ ] Demo environment available for stakeholders
- [ ] Known limitations documented in VERSION_1.0_SUMMARY

---

**Release approver:** _______________  **Date:** _______________
