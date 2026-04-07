# MfalmeBits — Architecture Audit & Pre-Flight Deployment Checklist
================================================================

## Files Provided in This Audit

| File | Purpose |
|------|---------|
| `utils/payments.py` | Full M-Pesa Daraja 3.0 STK Push implementation |
| `utils/search.py` | Multi-field Q-object search with tokenisation |
| `utils/seo_monitor.py` | 404 logging middleware + metadata validation |
| `utils/storage.py` | WhiteNoise / S3 toggle with `configure_storage()` |
| `core/settings/base.py` | Cleaned base settings (robots removed, no hardcoded secrets) |
| `core/settings/render.py` | Full production settings for Render / VPS |
| `core/wsgi.py` | Environment-aware WSGI with Gunicorn guidance |
| `core/asgi.py` | ASGI entry point for Uvicorn |
| `core/urls.py` | robots.txt via template view (replaces broken package) |
| `templates/robots.txt` | robots.txt template |
| `nginx/mfalmebits.conf` | Nginx with gzip, browser caching, security headers |
| `gunicorn.conf.py` | Gunicorn config tuned for 2 GB RAM / 2 vCPU |
| `build.sh` | Updated Render build script |

---

## ✅ Pre-Flight Deployment Checklist

### 1 — Secrets & Environment Variables
- [ ] `DJANGO_SECRET_KEY` is a 50+ character random string
      (`python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] `DATABASE_URL` is set (format: `postgresql://user:pass@host:5432/dbname`)
- [ ] `DJANGO_ALLOWED_HOSTS` includes your domain AND Render subdomain
- [ ] `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com`
- [ ] `STRIPE_PUBLIC_KEY` and `STRIPE_SECRET_KEY` are set (live keys, not test)
- [ ] `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_PASSKEY`, `MPESA_SHORTCODE` set
- [ ] `MPESA_CALLBACK_URL` is a public HTTPS URL (not localhost)
- [ ] `MPESA_ENVIRONMENT=production` (not sandbox) for live payments
- [ ] `DEFAULT_FROM_EMAIL` is set to your verified sender address

### 2 — Email / SMTP
- [ ] `EMAIL_BACKEND=smtp` in Render env (or leave as `console` for first deploy)
- [ ] `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` set
- [ ] Test with: `python manage.py sendtestemail you@example.com`
- [ ] `ACCOUNT_EMAIL_VERIFICATION=mandatory` once SMTP is confirmed working

### 3 — AllAuth Configuration
- [ ] `ACCOUNT_SIGNUP_ENABLED=false` if you only want admin-created users
- [ ] `ACCOUNT_EMAIL_VERIFICATION` matches your SMTP readiness
- [ ] Custom `ACCOUNT_FORMS` pointing to MfalmeBits forms (set in render.py)
- [ ] `LOGIN_REDIRECT_URL` points to `/accounts/dashboard/`

### 4 — Static Files (Jazzmin Admin Styling)
- [ ] `STATIC_ROOT` = absolute path: `BASE_DIR / "staticfiles"`
- [ ] `STATICFILES_DIRS` contains `BASE_DIR / "static"` (source files)
- [ ] `build.sh` runs `collectstatic --clear` on every deploy
- [ ] `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"`
      (this adds content hashes → Admin CSS never goes stale)
- [ ] Jazzmin logo at: `static/images/logo.png` ✓
- [ ] After deploy, visit `/admin/` and confirm styling is intact
- [ ] If Admin loses styles, check Nginx `location /static/` alias path

### 5 — Media Files
- [ ] If keeping files on disk: `MEDIA_ROOT` is on a persistent disk (not ephemeral)
      Render free tier has ephemeral disk — upgrade to Render Disk or use S3
- [ ] If using S3: set `USE_S3=true`, `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`,
      `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME`
- [ ] S3 bucket has public-read ACL enabled for the `media/` prefix
- [ ] Test file upload via Django Admin after deploy

### 6 — Database
- [ ] Using PostgreSQL (not SQLite) in production
- [ ] `conn_max_age=60` set (connection pooling reduces DB overhead)
- [ ] `ssl_require=True` (Render Postgres enforces TLS)
- [ ] `python manage.py migrate` runs in build.sh ✓
- [ ] Run `python manage.py dbshell` to verify connection works

### 7 — Cache & Sessions
- [ ] If `REDIS_URL` is set, sessions are stored in Redis (fast & shared across workers)
- [ ] If no Redis: sessions are in the DB (`SESSION_ENGINE` default) — acceptable for start
- [ ] `SESSION_COOKIE_SECURE=True` ✓
- [ ] `CSRF_COOKIE_SECURE=True` ✓

### 8 — Security Headers
- [ ] `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")` ✓
- [ ] `SECURE_SSL_REDIRECT = False` (Render handles HTTPS → HTTP is never seen by Django) ✓
- [ ] `X_FRAME_OPTIONS = "DENY"` ✓
- [ ] `SECURE_HSTS_SECONDS = 31536000` ✓
- [ ] Run `python manage.py check --deploy` — all warnings should be resolved

### 9 — Python 2 robots Package (FIXED)
- [ ] Remove `robots` from `THIRD_PARTY_APPS` in ALL settings files ✓
- [ ] Confirm `core/urls.py` has the `robots_txt` view function ✓
- [ ] Confirm `templates/robots.txt` exists ✓
- [ ] Visit `/robots.txt` on live site to verify response

### 10 — Gunicorn / Server Config
- [ ] Start Command on Render: `gunicorn core.wsgi:application -c gunicorn.conf.py`
- [ ] `PORT` env var is set by Render automatically
- [ ] 3 workers + 2 threads on 2 GB RAM (adjust via `GUNICORN_WORKERS` env var)
- [ ] `preload_app = True` in gunicorn.conf.py (saves ~50 MB RAM via fork COW) ✓
- [ ] `max_requests = 1000` to prevent memory leaks ✓

### 11 — Nginx (VPS only — skip for Render)
- [ ] Update `alias` paths in nginx/mfalmebits.conf to match your server paths
- [ ] SSL certificate via Certbot: `sudo certbot --nginx -d yourdomain.com`
- [ ] `gzip on` with correct MIME types ✓
- [ ] `expires 1y` for `/static/` (matched with CompressedManifest hashing) ✓
- [ ] `proxy_set_header X-Forwarded-Proto https` to satisfy SECURE_PROXY_SSL_HEADER ✓
- [ ] Test: `nginx -t` before reloading

### 12 — Celery (if using background tasks)
- [ ] `REDIS_URL` is set (Celery requires Redis or another broker)
- [ ] Start a separate Render Worker: `celery -A core.celery worker -c 2 --loglevel=info`
- [ ] Beat scheduler: `celery -A core.celery beat --loglevel=info`
- [ ] `CELERY_WORKER_CONCURRENCY=2` on 2 GB RAM ✓

### 13 — M-Pesa Specific
- [ ] Callback URL (`MPESA_CALLBACK_URL`) is publicly reachable HTTPS
- [ ] Callback URL is whitelisted in Safaricom Daraja app settings
- [ ] Create a Django view at the callback URL path (csrf_exempt + POST)
- [ ] Test with sandbox credentials before switching to production
- [ ] Store `receipt_number` and `checkout_request_id` in your Purchase model

### 14 — Frontend Performance
- [ ] All `<img>` tags in templates have `loading="lazy"` attribute
- [ ] Tailwind CSS is purged (no dev-only utility classes in production bundle)
- [ ] `COMPRESS_ENABLED=False` in production (WhiteNoise handles compression) ✓
- [ ] Consider Cloudflare free tier for global CDN caching
- [ ] Use `.select_related()` and `.prefetch_related()` in all list views

---

## 🚨 Security Risks Found in Original Code

1. **Hardcoded SECRET_KEY default** in base.py — any app started without .env
   would use the insecure fallback. Fixed: render.py raises ValueError if not set.

2. **`DEBUG=True` in base settings** with no guard — if env var is missing,
   Django exposes tracebacks publicly. Fixed: render.py forces `DEBUG=False`.

3. **`robots` package** causes ImportError on Python 3.10+ (`print` statement
   syntax). Fixed: removed from INSTALLED_APPS, replaced with template view.

4. **`debug_toolbar` in production MIDDLEWARE** — the original render.py kept
   DebugToolbarMiddleware. It adds overhead and exposes profiling data.
   Fixed: removed from render.py MIDDLEWARE.

5. **`EMAIL_BACKEND = console`** was the only backend — silently drops all
   password reset and verification emails in production.
   Fixed: render.py switches to SMTP when `EMAIL_BACKEND=smtp` env var is set.

6. **`ACCOUNT_EMAIL_VERIFICATION = "none"`** in the original render.py —
   allows account takeover via email spoofing (anyone can register with your email).
   Fixed: defaults to `"optional"` with env-var override to `"mandatory"`.

7. **`ACCOUNT_SIGNUP_ENABLED = False` hardcoded** in original render.py —
   prevents any new user registration. Fixed: controlled via env var.

8. **No `SECURE_REFERRER_POLICY`** set — browsers send full referrer URLs
   to third-party assets. Fixed: added `"strict-origin-when-cross-origin"`.

9. **`compress_offline = False`** in production — each page load runs the
   compressor pipeline. Fixed: disabled compression entirely (WhiteNoise handles it).

10. **`COLLABORATION_EMAIL` and `INSTITUTIONAL_EMAIL`** referenced in views
    but never declared in settings — raises `AttributeError` at runtime.
    Fixed: added to base.py and render.py with env-var defaults.

---

## 📦 Additional pip packages required

Add these to requirements.txt if not already present:

```
# Payments
requests>=2.31.0           # M-Pesa HTTP calls

# Production server
gunicorn>=21.2.0
uvicorn[standard]>=0.27.0  # Only if using ASGI

# Database
dj-database-url>=2.1.0
psycopg2-binary>=2.9.9     # PostgreSQL adapter

# Caching (optional but recommended)
django-redis>=5.4.0
hiredis>=2.3.2             # C-speed Redis parser

# Error tracking (optional)
sentry-sdk[django]>=1.40.0

# S3 storage (optional)
django-storages[boto3]>=1.14.0
boto3>=1.34.0
```

Remove from requirements.txt:
```
# robots            ← Python 2 only; remove entirely
```