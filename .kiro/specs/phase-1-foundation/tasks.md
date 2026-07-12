# Phase 1 — Foundation: Implementation Tasks

> **Phase:** 1
> **Slug:** foundation
> **Branch:** `phase-1/foundation`
> **Estimated tasks:** 47

---

## Task Groups

Tasks are ordered by dependency. Complete each group before moving to the next.

---

## Group A: Project Skeleton & Django Setup

> **Commit scope:** `feat: scaffold Django project structure`

- [ ] **A1.** Create `config/` directory with `__init__.py`
- [ ] **A2.** Create `config/settings/__init__.py` (empty)
- [ ] **A3.** Create `config/settings/base.py` — INSTALLED_APPS, MIDDLEWARE, TEMPLATES, DATABASES (reads DATABASE_URL), AUTH_USER_MODEL, STATIC/MEDIA config, django-htmx middleware
- [ ] **A4.** Create `config/settings/local.py` — DEBUG=True, debug toolbar, Django static serving
- [ ] **A5.** Create `config/settings/production.py` — DEBUG=False, ALLOWED_HOSTS from env, WhiteNoise, security settings (SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, etc.)
- [ ] **A6.** Create `config/urls.py` — root urlconf with admin and internal app include
- [ ] **A7.** Create `config/wsgi.py` — WSGI application for Gunicorn
- [ ] **A8.** Create `manage.py` pointing to `config.settings.local` by default
- [ ] **A9.** Create `.python-version` with `3.12`
- [ ] **A10.** Create `pyproject.toml` with project metadata and `[tool.ruff]` config
- [ ] **A11.** Create `requirements/base.txt` with pinned dependencies
- [ ] **A12.** Create `requirements/local.txt` with dev dependencies
- [ ] **A13.** Create `requirements/production.txt` (includes base.txt)
- [ ] **A14.** Create `.env.example` with all required env vars documented
- [ ] **A15.** Create `.gitignore` (Python, Django, .env, __pycache__, .DS_Store, static/css/main.css)

---

## Group B: Django Apps (Models Only)

> **Commit scope:** `feat: define all Django models and migrations`

- [ ] **B1.** Create `apps/accounts/` app structure: `__init__.py`, `apps.py`, `admin.py`, `models.py`, `managers.py`
- [ ] **B2.** Implement `apps/accounts/managers.py` — custom `UserManager` with `create_user()` and `create_superuser()`
- [ ] **B3.** Implement `apps/accounts/models.py` — `User` (AbstractBaseUser, UUID pk, display_name, email, password, email_verified_at, timestamps)
- [ ] **B4.** Implement `apps/accounts/models.py` — `EmailVerificationToken` model (UUID pk, FK user, token_hash, expires_at, consumed_at, created_at)
- [ ] **B5.** Implement `apps/accounts/models.py` — `PasswordResetToken` model (UUID pk, FK user, token_hash, expires_at, consumed_at, created_at)
- [ ] **B6.** Create `apps/events/` app structure: `__init__.py`, `apps.py`, `admin.py`, `models.py`
- [ ] **B7.** Implement `apps/events/models.py` — TextChoices: `EventStatus`, `EventRole`, `AccessStatus`
- [ ] **B8.** Implement `apps/events/models.py` — `Event` model (all fields from schema, UUID pk, FK owner_user)
- [ ] **B9.** Implement `apps/events/models.py` — `EventParticipation` model (all fields, unique constraint on event+user, indexes)
- [ ] **B10.** Create `apps/items/` app structure: `__init__.py`, `apps.py`, `admin.py`, `models.py`
- [ ] **B11.** Implement `apps/items/models.py` — TextChoices: `SuggestionStatus`, `ItemUnit`
- [ ] **B12.** Implement `apps/items/models.py` — `EventItem` model (all fields, FK event, FK source_suggestion nullable)
- [ ] **B13.** Implement `apps/items/models.py` — `ItemAssignment` model (all fields, partial unique constraint WHERE cancelled_at IS NULL)
- [ ] **B14.** Create `apps/moderation/` app structure: `__init__.py`, `apps.py`, `admin.py`, `models.py`
- [ ] **B15.** Implement `apps/moderation/models.py` — `ItemSuggestion` model (all fields, FK event, FK suggested_by, FK converted_event_item nullable)
- [ ] **B16.** Create `apps/internal/` app structure: `__init__.py`, `apps.py`, `views.py`, `urls.py`
- [ ] **B17.** Implement `apps/internal/views.py` — `close_expired_events` view stub (verify X-Internal-Token, return 200)
- [ ] **B18.** Implement `apps/internal/urls.py` — wire the internal endpoint
- [ ] **B19.** Run `python manage.py makemigrations` — verify all migrations generate cleanly
- [ ] **B20.** Run `python manage.py migrate` — verify all migrations apply cleanly
- [ ] **B21.** Verify: create a user via Django shell (`User.objects.create_user(...)`)

---

## Group C: Tailwind CSS Setup

> **Commit scope:** `feat: configure Tailwind CSS v4 with Hatsik design tokens`

- [ ] **C1.** Download Tailwind CLI standalone binary (macOS arm64 for local, linux-x64 for Docker)
- [ ] **C2.** Create `static/css/input.css` with `@theme` block defining all Hatsik tokens (colors, spacing, radii, fonts)
- [ ] **C3.** Add `@import "tailwindcss"` directives in `input.css`
- [ ] **C4.** Create `Makefile` with targets: `tailwind-watch`, `tailwind-build` (minify)
- [ ] **C5.** Run `make tailwind-build` — verify `static/css/main.css` is generated
- [ ] **C6.** Add `static/css/main.css` to `.gitignore` (generated artifact)

---

## Group D: Base Templates & Components

> **Commit scope:** `feat: create base templates and UI component partials`

- [ ] **D1.** Download HTMX 2.x min.js and place in `static/js/htmx.min.js`
- [ ] **D2.** Create `templates/base.html` — HTML5 shell, Google Fonts (Nunito + Plus Jakarta Sans), Tailwind CSS link, HTMX script, Django blocks (title, content, extra_js)
- [ ] **D3.** Create `templates/components/_button.html` — accepts `variant` (primary/secondary/destructive), `text`, optional `href` or `type`
- [ ] **D4.** Create `templates/components/_card.html` — wrapper with rounded-[--radius-card], border, shadow
- [ ] **D5.** Create `templates/components/_badge.html` — accepts `status` → maps to color variant
- [ ] **D6.** Create `templates/components/_modal.html` — HTMX-triggered dialog with confirm/cancel actions
- [ ] **D7.** Create `templates/components/_input.html` — accepts `name`, `label`, `type`, `error`, `placeholder`
- [ ] **D8.** Create `templates/components/_toast.html` — auto-dismiss feedback message
- [ ] **D9.** Create a test view + URL (`/dev/components/`) that renders all components for visual verification
- [ ] **D10.** Verify: `hx-get` request to a test endpoint returns partial HTML correctly

---

## Group E: Email Infrastructure

> **Commit scope:** `feat: configure Resend SDK for transactional emails`

- [ ] **E1.** Create `apps/accounts/emails.py` — `send_verification_email(user, token)` and `send_password_reset_email(user, token)` functions
- [ ] **E2.** Create email HTML template (inline CSS, Hatsik branding, coral accent, logo)
- [ ] **E3.** Create email plain text fallback
- [ ] **E4.** Add `RESEND_API_KEY` to settings via python-decouple
- [ ] **E5.** Verify: send a test email successfully (manual test via Django shell)

---

## Group F: Containerization

> **Commit scope:** `feat: Docker and docker-compose for local and production`

- [ ] **F1.** Create `Dockerfile` — multi-concern: install deps, download Tailwind binary, compile CSS, collectstatic, Gunicorn entrypoint
- [ ] **F2.** Create `docker-compose.yml` — Django service (volume mount, runserver, port 8000) + PostgreSQL 16 service
- [ ] **F3.** Create `.dockerignore` — exclude .git, .env, node_modules, __pycache__, docs
- [ ] **F4.** Verify: `docker compose up` starts both services without errors
- [ ] **F5.** Verify: `docker compose exec web python manage.py migrate` runs cleanly
- [ ] **F6.** Verify: `docker build .` completes without errors (production image)

---

## Group G: CI/CD Pipeline

> **Commit scope:** `feat: GitHub Actions workflow for lint, test, build, deploy`

- [ ] **G1.** Create `.github/workflows/deploy.yml` — trigger on push to main
- [ ] **G2.** Add step: checkout code
- [ ] **G3.** Add step: setup Python 3.12
- [ ] **G4.** Add step: install dependencies (`requirements/local.txt`)
- [ ] **G5.** Add step: run `ruff check .` and `ruff format --check .`
- [ ] **G6.** Add step: run `python manage.py test`
- [ ] **G7.** Add step: build Docker image and tag with commit SHA
- [ ] **G8.** Add step: authenticate to AWS ECR
- [ ] **G9.** Add step: push image to ECR
- [ ] **G10.** Add step: trigger App Runner deployment (update service)
- [ ] **G11.** Add required GitHub secrets documentation in README or `.env.example`

---

## Group H: AWS Infrastructure

> **Commit scope:** `infra: provision ECR, App Runner, EventBridge`
> **Note:** This group may be done manually via AWS Console or IaC — document what was done.

- [ ] **H1.** Create AWS ECR repository for Hatsik images
- [ ] **H2.** Create AWS App Runner service connected to ECR (auto-deploy on push)
- [ ] **H3.** Configure App Runner environment variables (SECRET_KEY, DATABASE_URL, RESEND_API_KEY, INTERNAL_CRON_TOKEN, ALLOWED_HOSTS)
- [ ] **H4.** Configure custom domain + SSL certificate (ACM) on App Runner
- [ ] **H5.** Create EventBridge Scheduler rule — every 5 min, POST to `/internal/close-expired-events/` with X-Internal-Token header
- [ ] **H6.** Verify: deploy via CI → App Runner picks up the new image
- [ ] **H7.** Verify: custom domain responds with HTTPS
- [ ] **H8.** Verify: EventBridge calls the internal endpoint (check CloudWatch logs or endpoint response)

---

## Verification Checklist (Final)

Run these checks after ALL groups are complete:

- [ ] `docker compose up` → app accessible at localhost:8000
- [ ] `Dockerfile` builds → Gunicorn starts on port 8000
- [ ] `python manage.py migrate` → zero errors on local PG AND Neon
- [ ] `python manage.py shell` → `User.objects.create_user(email='test@test.com', display_name='Test', password='test1234')` succeeds
- [ ] `base.html` loads → HTMX and Tailwind CSS present in page source
- [ ] `/dev/components/` → all components render with correct styling
- [ ] `make tailwind-build` → `main.css` contains custom color tokens
- [ ] Test email sends via Resend (manual shell test)
- [ ] `DEBUG=False` + `collectstatic` → WhiteNoise serves CSS/JS correctly
- [ ] Push to `main` → GitHub Actions runs green (lint + test + build)
- [ ] CI pushes image to ECR → App Runner deploys
- [ ] Custom domain responds on HTTPS
- [ ] EventBridge fires → `/internal/close-expired-events/` returns 200
