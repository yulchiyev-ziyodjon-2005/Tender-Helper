# TenderHelper VPS Deployment Runbook

**Status:** staging-ready baseline. Production deploy faqat checklist oxiridagi
gate'lar yopilgandan keyin bajariladi.

## 1. Target Topology

Minimum VPS:

- Ubuntu 22.04/24.04 LTS;
- 2 vCPU, 4 GB RAM;
- PostgreSQL 16;
- Redis 7;
- Nginx + Let's Encrypt;
- Python 3.11+;
- Node.js 20.19+ yoki 22.12+.

Services:

- `tenderhelper-web`: Gunicorn + Django API;
- `tenderhelper-worker`: Celery worker;
- `tenderhelper-beat`: Celery Beat;
- Nginx: HTTPS reverse proxy, static/media/frontend serving;
- PostgreSQL and Redis: localhost/private network.

## 2. Required GitHub State

Deploydan oldin:

```powershell
.\scripts\quality-backend.ps1
cd frontend
npm run lint
npm run build
```

CI ham quyidagilarni bajarishi shart:

- backend ruff;
- Django check;
- migration drift check;
- backend tests;
- PostgreSQL migrate/check/test and search benchmark;
- frontend lint/build.

## 3. Server Bootstrap

```bash
sudo apt update
sudo apt install -y \
  git curl build-essential python3.11 python3.11-venv python3-pip \
  postgresql-16 postgresql-contrib redis-server nginx certbot python3-certbot-nginx
```

Create app user:

```bash
sudo adduser --system --group --home /opt/tenderhelper tenderhelper
sudo mkdir -p /opt/tenderhelper/app /opt/tenderhelper/env /opt/tenderhelper/logs
sudo chown -R tenderhelper:tenderhelper /opt/tenderhelper
```

## 4. PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE USER tender_admin WITH PASSWORD '<strong-password>';
CREATE DATABASE tender_helper_prod OWNER tender_admin;
ALTER ROLE tender_admin CREATEDB;
\c tender_helper_prod
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

`CREATEDB` staging/test runner uchun kerak. Production policy qat'iy bo'lsa,
test runner alohida role bilan yuritiladi va app role'dan `CREATEDB` olib
tashlanadi.

## 5. Environment

Create `/opt/tenderhelper/env/backend.env` from `.env.example`.

Minimum production values:

```bash
APP_ENV=production
DEBUG=False
SECRET_KEY=<50+ chars random secret>
ALLOWED_HOSTS=tenderhelperai.com,api.tenderhelperai.com,127.0.0.1
DATABASE_URL=postgresql://tender_admin:<password>@127.0.0.1:5432/tender_helper_prod
DATABASE_CONN_MAX_AGE=60
FRONTEND_BASE_URL=https://tenderhelperai.com
CORS_ALLOWED_ORIGINS=https://tenderhelperai.com,https://www.tenderhelperai.com
CSRF_TRUSTED_ORIGINS=https://tenderhelperai.com,https://www.tenderhelperai.com,https://api.tenderhelperai.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
TRUST_X_FORWARDED_PROTO=True
REDIS_URL=redis://127.0.0.1:6379
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/1
CELERY_TASK_ALWAYS_EAGER=False
DEMO_MODE=False
```

HSTS `includeSubDomains` va `preload` faqat barcha subdomainlar HTTPS-ready
ekanligi audit qilingandan keyin `True` qilinadi.

## 6. Application Release

```bash
sudo -u tenderhelper git clone <repo-url> /opt/tenderhelper/app/current
cd /opt/tenderhelper/app/current/backend
sudo -u tenderhelper python3.11 -m venv .venv
sudo -u tenderhelper .venv/bin/pip install --upgrade pip
sudo -u tenderhelper .venv/bin/pip install -r requirements.txt
```

Preflight:

```bash
set -a
. /opt/tenderhelper/env/backend.env
set +a
cd /opt/tenderhelper/app/current/backend
.venv/bin/python manage.py check
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput
```

Production deploy check:

```bash
APP_ENV=production DEBUG=False .venv/bin/python manage.py check --deploy
```

Expected warning policy:

- HSTS preload/include-subdomains warnings are acceptable only before the
  explicit DNS/subdomain HTTPS audit.
- Any other warning must be reviewed before production.

## 7. Systemd Units

`/etc/systemd/system/tenderhelper-web.service`:

```ini
[Unit]
Description=TenderHelper Django API
After=network.target postgresql.service redis-server.service

[Service]
User=tenderhelper
Group=tenderhelper
WorkingDirectory=/opt/tenderhelper/app/current/backend
EnvironmentFile=/opt/tenderhelper/env/backend.env
ExecStart=/opt/tenderhelper/app/current/backend/.venv/bin/gunicorn core.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/tenderhelper-worker.service`:

```ini
[Unit]
Description=TenderHelper Celery Worker
After=network.target redis-server.service postgresql.service

[Service]
User=tenderhelper
Group=tenderhelper
WorkingDirectory=/opt/tenderhelper/app/current/backend
EnvironmentFile=/opt/tenderhelper/env/backend.env
ExecStart=/opt/tenderhelper/app/current/backend/.venv/bin/celery -A core worker --loglevel=INFO --concurrency=2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/tenderhelper-beat.service`:

```ini
[Unit]
Description=TenderHelper Celery Beat
After=network.target redis-server.service postgresql.service

[Service]
User=tenderhelper
Group=tenderhelper
WorkingDirectory=/opt/tenderhelper/app/current/backend
EnvironmentFile=/opt/tenderhelper/env/backend.env
ExecStart=/opt/tenderhelper/app/current/backend/.venv/bin/celery -A core beat --loglevel=INFO
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tenderhelper-web tenderhelper-worker tenderhelper-beat
```

## 8. Frontend

Build:

```bash
cd /opt/tenderhelper/app/current/frontend
npm ci
VITE_API_BASE_URL=https://api.tenderhelperai.com/api/v1 npm run build
sudo mkdir -p /var/www/tenderhelper
sudo rsync -a --delete dist/ /var/www/tenderhelper/
```

## 9. Nginx

Example server blocks:

```nginx
server {
    server_name api.tenderhelperai.com;

    client_max_body_size 25m;

    location /static/ {
        alias /opt/tenderhelper/app/current/backend/staticfiles/;
    }

    location /media/ {
        alias /opt/tenderhelper/app/current/backend/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    server_name tenderhelperai.com www.tenderhelperai.com;
    root /var/www/tenderhelper;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable HTTPS:

```bash
sudo certbot --nginx -d api.tenderhelperai.com -d tenderhelperai.com -d www.tenderhelperai.com
```

## 10. Smoke Test

After deploy:

```bash
curl -fsS https://api.tenderhelperai.com/api/health/
curl -fsS https://tenderhelperai.com/
sudo systemctl status tenderhelper-web --no-pager
sudo systemctl status tenderhelper-worker --no-pager
sudo systemctl status tenderhelper-beat --no-pager
sudo journalctl -u tenderhelper-web -n 100 --no-pager
```

Manual smoke:

- register/login;
- onboarding STIR skip and/or draft path;
- session endpoint;
- tender list/search;
- dashboard;
- team page;
- superadmin preview with privileged account;
- analysis failure path if provider credentials are absent;
- document template list for Business/STIR account.

## 11. Rollback

Before each deploy:

```bash
pg_dump -Fc "$DATABASE_URL" > /opt/tenderhelper/backups/predeploy-$(date +%Y%m%d-%H%M%S).dump
```

Rollback steps:

1. switch `/opt/tenderhelper/app/current` symlink or checkout to previous commit;
2. reinstall dependencies only if lock/requirements changed;
3. run compatible migrations only after review;
4. restart systemd services;
5. restore database from dump only if migration/data corruption requires it.

## 12. Production Blockers

These are not required for first staging deploy, but block production sign-off:

- successful backup/restore drill on the target VPS;
- Redis/Celery worker/beat observed under real queues;
- SMTP/SMS credentials verified and access policy documented;
- payment provider credentials and reconciliation policy approved;
- object storage abstraction for durable export/media retention;
- Sentry/structured logging and alert route;
- real portal legal/technical audit;
- HSTS preload/subdomain HTTPS audit.
