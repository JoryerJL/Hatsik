# Phase 1 — Foundation: Technical Design

> **Phase:** 1
> **Slug:** foundation
> **Date:** 2026-07-12

---

## Architecture Overview

Phase 1 creates the foundational skeleton. No business logic, no user-facing features. The output is a Django monolith that builds, deploys, and runs — ready for Phase 2 to start writing product code.

```
┌──────────────────────────────────────────────┐
│  GitHub Actions (CI/CD)                      │
│  ruff lint → tests → Docker build → ECR push │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  AWS ECR (container registry)                │
└─────────────────────┬────────────────────────┘
                      │ auto-detect new image
                      ▼
┌──────────────────────────────────────────────┐
│  AWS App Runner                              │
│  Gunicorn → Django → PostgreSQL (Neon)       │
│  WhiteNoise serves static files              │
│  Custom domain + SSL (ACM)                   │
└──────────────────────────────────────────────┘
                      ▲
                      │ every 5 min
┌──────────────────────────────────────────────┐
│  AWS EventBridge Scheduler                   │
│  POST /internal/close-expired-events/        │
└──────────────────────────────────────────────┘
```

---

## Key Technical Decisions

### D1: Django Settings Split

| Decision | Use split settings: `base.py`, `local.py`, `production.py` |
|----------|-------------------------------------------------------------|
| Why | Isolate dev conveniences (DEBUG toolbar, runserver) from production hardening (WhiteNoise, Gunicorn, forced HTTPS) |
| How | `DJANGO_SETTINGS_MODULE` defaults to `config.settings.local` in docker-compose, `config.settings.production` in Dockerfile |
| Trade-off | Slightly more files vs. cleaner separation; accepted per ARCHITECTURE_AND_STACK.md |

### D2: Custom User Model (day one)

| Decision | Define `accounts.User` extending `AbstractBaseUser` with UUID pk from the start |
|----------|-----------------------------------------------------------------------------|
| Why | Django docs warn: changing the User model after the first migration is extremely painful |
| How | `AUTH_USER_MODEL = 'accounts.User'` in `base.py`. All FK references use `settings.AUTH_USER_MODEL` |
| Fields | `id` (UUID), `display_name`, `email` (unique, normalized), `password` (hashed), `email_verified_at`, `created_at`, `updated_at` |
| Manager | Custom `UserManager` — `create_user()` normalizes email, `create_superuser()` for admin access |

### D3: All Models in Phase 1 (empty tables)

| Decision | Create ALL models and migrations in Phase 1, even though only `users` is used |
|----------|---------------------------------------------------------------------------|
| Why | Avoids migration conflicts later, ensures schema matches DATABASE_SCHEMA.md from day one |
| How | Each app (`events`, `items`, `moderation`) defines its models now; views/urls remain empty until their phase |
| Risk | Models may need adjustments — but the schema doc is finalized, so changes should be minimal |

### D4: Tailwind CSS Standalone (no Node.js)

| Decision | Use Tailwind CLI standalone binary, not npm |
|----------|---------------------------------------------|
| Why | Django project; no frontend build step with Node. Keeps the Docker image slim |
| How | Download binary in Dockerfile (`tailwindcss-linux-x64`), use Makefile for local dev |
| Watch mode | `make tailwind-watch` or `./tailwindcss --watch` during development |
| Production | `./tailwindcss --minify` in Dockerfile before `collectstatic` |

### D5: Tailwind v4 @theme Configuration

| Decision | Use Tailwind v4's `@theme` directive in `input.css` |
|----------|-------------------------------------------------------|
| Why | Tailwind v4 drops `tailwind.config.js` in favor of CSS-first config |
| How | Define tokens directly in `static/css/input.css` using `@theme { }` block |
| Tokens | Colors, spacing, radii from `hatsik-brand-identity.md`; fonts from Google Fonts link |

### D6: HTMX as Static File (no CDN)

| Decision | Copy `htmx.min.js` into `static/js/` |
|----------|----------------------------------------|
| Why | No external runtime dependency, works offline, version-pinned |
| Version | HTMX 2.x (latest stable at implementation time) |
| Config | `django-htmx` middleware for `request.htmx` detection in views |

### D7: Database Driver — psycopg 3

| Decision | Use `psycopg[binary]` 3.2.x, NOT `psycopg2` |
|----------|-----------------------------------------------|
| Why | Modern async-ready driver, better performance, maintained actively |
| Config | `DATABASE_URL` parsed by `dj-database-url` or manual parsing in settings |
| Neon compatibility | psycopg3 works with Neon's serverless PostgreSQL without issues |

### D8: python-decouple for ENV Management

| Decision | Use `python-decouple` to read environment variables |
|----------|------------------------------------------------------|
| Why | Simple, no framework lock-in, reads from `.env` file locally and from OS env in production |
| Pattern | `config('SECRET_KEY')`, `config('DEBUG', default=False, cast=bool)` |
| Production | App Runner injects env vars directly — no `.env` file in the container |

### D9: WhiteNoise for Static Files

| Decision | Use WhiteNoise 6.x in production — no S3 in MVP |
|----------|--------------------------------------------------|
| Why | Simpler deploy (no S3 buckets, no CDN config), static files served from the container |
| How | `WhiteNoiseMiddleware` in `MIDDLEWARE`, `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'` |
| Migration path | If scale demands it, move to S3+CloudFront post-MVP |

### D10: Resend for Transactional Email

| Decision | Use Resend SDK (Python) for verification and password reset emails |
|----------|---------------------------------------------------------------------|
| Why | Simple API, good DX, no SMTP config needed |
| How | `resend.Emails.send()` with API key from env |
| Templates | Plain text + minimal HTML (inline styles, no complex layouts) |
| Abstraction | Wrap in `apps/accounts/emails.py` functions so the email provider is swappable |

### D11: EventBridge + Internal Endpoint Security

| Decision | Protect `/internal/close-expired-events/` with a shared secret token |
|----------|-----------------------------------------------------------------------|
| Why | No public auth system yet in Phase 1; simple token validation is sufficient |
| How | `X-Internal-Token` header checked against `INTERNAL_CRON_TOKEN` env var |
| View | In `apps/internal/views.py`, returns 200 on success (events closure logic comes in Phase 3) |

### D12: Ruff for Linting & Formatting

| Decision | Use `ruff` for both linting AND formatting (replaces flake8 + black + isort) |
|----------|-------------------------------------------------------------------------------|
| Why | Single tool, extremely fast, covers all Python style checks |
| Config | `pyproject.toml` with `[tool.ruff]` section |
| CI | `ruff check .` + `ruff format --check .` in GitHub Actions |

---

## Dependencies (Pinned Versions)

### base.txt
```
Django==5.2.*
psycopg[binary]==3.2.*
django-htmx==1.21.*
resend==2.*
qrcode==7.*
gunicorn==23.*
whitenoise==6.*
python-decouple==3.*
```

### local.txt
```
-r base.txt
django-debug-toolbar==4.*
ruff==0.11.*
```

### production.txt
```
-r base.txt
```

---

## File Ownership per App (Phase 1)

| App | Models created | Views/URLs | Templates |
|-----|---------------|------------|-----------|
| `accounts` | `User`, `EmailVerificationToken`, `PasswordResetToken` | None (Phase 2) | None (Phase 2) |
| `events` | `Event`, `EventParticipation` | None (Phase 3) | None (Phase 3) |
| `items` | `EventItem`, `ItemAssignment` | None (Phase 5) | None (Phase 5) |
| `moderation` | `ItemSuggestion` | None (Phase 5) | None (Phase 5) |
| `internal` | None | `close_expired_events` (stub: returns 200) | None |

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Neon cold start delays | Slow first request | Acceptable for MVP; monitor in production |
| Tailwind v4 breaking changes | Build failures | Pin standalone binary version in Dockerfile |
| App Runner cold starts | Latency spikes | Min instances = 1 if budget allows |
| ECR/App Runner IAM complexity | Deploy failures | Use minimal IAM roles, document in README |
| Partial unique index (Django limitation) | Migration workaround needed | Use `Meta.constraints` with `UniqueConstraint(condition=Q(...))` |
