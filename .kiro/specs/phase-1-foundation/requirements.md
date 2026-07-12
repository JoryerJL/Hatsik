# Phase 1 — Foundation: Requirements

> **Phase:** 1
> **Slug:** foundation
> **Goal:** Working project skeleton. Nothing user-facing yet, but everything else depends on this.
> **Module:** Infrastructure (no product module)
> **Depends on:** Nothing — this is the starting point.
> **Stitch screens:** None

---

## User Stories

### US-1: Project Structure
**As a** developer
**I want** a properly structured Django monolith following the architecture spec
**So that** all future modules have a consistent home and the project builds cleanly from day one.

**Acceptance Criteria:**
- [ ] Folder structure matches `ARCHITECTURE_AND_STACK.md` exactly
- [ ] `config/settings/` has `base.py`, `local.py`, `production.py`
- [ ] `apps/` has placeholder modules: `accounts`, `events`, `items`, `moderation`, `internal`
- [ ] `templates/` has `base.html`, `partials/`, `components/`
- [ ] `static/` has `css/`, `js/htmx.min.js`, `img/`
- [ ] `requirements/` has `base.txt`, `local.txt`, `production.txt`
- [ ] `.python-version` is set to `3.12`
- [ ] `manage.py` works with `python manage.py check`

---

### US-2: Containerization & Local Dev
**As a** developer
**I want** Docker and docker-compose configured for local development
**So that** anyone can run the project with `docker compose up` without local Python setup.

**Acceptance Criteria:**
- [ ] `Dockerfile` builds a production-ready image (Python 3.12 slim, deps, Tailwind compile, collectstatic, Gunicorn)
- [ ] `docker-compose.yml` runs Django + PostgreSQL 16 locally
- [ ] `docker compose up` starts the app without errors
- [ ] Hot-reload works in local dev (runserver inside container)
- [ ] `.env.example` has all required variables documented

---

### US-3: Database Schema
**As a** developer
**I want** the full database schema from `DATABASE_SCHEMA.md` implemented as Django models
**So that** all future modules have their tables ready from the start.

**Acceptance Criteria:**
- [ ] Custom User model (`AbstractBaseUser` or `AbstractUser`) in `apps/accounts/models.py` with UUID pk
- [ ] All 8 tables modeled: `users`, `email_verification_tokens`, `password_reset_tokens`, `events`, `event_participations`, `event_items`, `item_assignments`, `item_suggestions`
- [ ] All enums as Django `TextChoices`: `event_status`, `event_role`, `access_status`, `suggestion_status`, `item_unit`
- [ ] All indexes and unique constraints from the schema (including partial unique on `item_assignments`)
- [ ] Migrations run cleanly from scratch against local PostgreSQL
- [ ] Migrations run cleanly against Neon (production DB)
- [ ] Can create a user via Django shell successfully

---

### US-4: Tailwind CSS Integration
**As a** developer
**I want** Tailwind CSS 4.x configured with the Hatsik design tokens
**So that** all future UI components use consistent brand styling.

**Acceptance Criteria:**
- [ ] Tailwind CLI standalone binary (no Node.js dependency)
- [ ] `static/css/input.css` → compiles to `static/css/main.css`
- [ ] Custom theme tokens configured (`@theme` in Tailwind v4):
  - Colors: `--color-primary` (#E8432D), `--color-primary-hover` (#F26B54), `--color-primary-soft` (#FDE8E4), state colors
  - Typography: Nunito (headings), Plus Jakarta Sans (body)
  - Spacing: `--space-1` through `--space-6`
  - Radii: `--radius-card` (16px), `--radius-button` (12px), `--radius-input` (10px), `--radius-pill` (999px)
- [ ] `--watch` mode works for local development
- [ ] `--minify` compiles for production in Docker build
- [ ] Google Fonts loaded in `base.html` (Nunito + Plus Jakarta Sans)

---

### US-5: Base Templates & UI Components
**As a** developer
**I want** the HTML shell and reusable component partials ready
**So that** all future screens have consistent layout and don't reinvent UI primitives.

**Acceptance Criteria:**
- [ ] `templates/base.html` has: `<head>` (fonts, Tailwind CSS, HTMX), `<body>` with nav structure, Django block structure
- [ ] `templates/components/_button.html` — primary, secondary, destructive variants
- [ ] `templates/components/_card.html` — rounded corners, soft border
- [ ] `templates/components/_badge.html` — pill-shaped status badges with semaphore colors
- [ ] `templates/components/_modal.html` — HTMX-powered confirmation dialog shell
- [ ] `templates/components/_input.html` — form input with label, error state, focus ring
- [ ] `templates/components/_toast.html` — ephemeral feedback message
- [ ] HTMX 2.x loaded as static JS file (direct copy, no npm)
- [ ] A test `hx-get` request works correctly

---

### US-6: Email Infrastructure
**As a** developer
**I want** Resend configured for transactional emails
**So that** Phase 2 (Auth) can send verification and password reset emails immediately.

**Acceptance Criteria:**
- [ ] `resend` 2.x SDK installed and configured with `RESEND_API_KEY`
- [ ] Utility module with functions for sending verification and password reset emails
- [ ] Email templates: plain text + simple HTML, branded with Hatsik logo and coral accent
- [ ] A test email sends successfully from local environment
- [ ] A test email sends successfully from Docker environment

---

### US-7: Static Files Serving
**As a** developer
**I want** WhiteNoise configured for production static file serving
**So that** we don't need S3/CDN in the MVP.

**Acceptance Criteria:**
- [ ] WhiteNoise 6.x in production settings
- [ ] `collectstatic` runs as part of Docker build
- [ ] Static files serve correctly when `DEBUG=False`
- [ ] In local dev: Django's built-in static serving works with `DEBUG=True`

---

### US-8: CI/CD Pipeline
**As a** developer
**I want** GitHub Actions configured for automated testing and deployment
**So that** every push to `main` is validated and deployed automatically.

**Acceptance Criteria:**
- [ ] `.github/workflows/deploy.yml` exists
- [ ] Pipeline runs `ruff` (linting) + `ruff format --check` (formatting)
- [ ] Pipeline runs Django tests (`python manage.py test`)
- [ ] Pipeline builds Docker image
- [ ] Pipeline pushes image to AWS ECR
- [ ] Pipeline triggers AWS App Runner deployment
- [ ] Pipeline runs on every push to `main`

---

### US-9: Production Infrastructure (AWS)
**As a** developer
**I want** the AWS infrastructure provisioned and working
**So that** we can deploy and iterate on the app from day one.

**Acceptance Criteria:**
- [ ] AWS ECR repository created and accessible from CI
- [ ] AWS App Runner service created, pulls from ECR
- [ ] Custom domain configured with SSL (ACM) on App Runner
- [ ] App responds with HTTPS on the custom domain
- [ ] AWS EventBridge Scheduler created — calls `/internal/close-expired-events/` every 5 min
- [ ] Internal endpoint returns 200 with valid `X-Internal-Token`

---

### US-10: Environment Variables
**As a** developer
**I want** all environment variables documented and managed properly
**So that** no secrets are committed and setup is clear for any contributor.

**Acceptance Criteria:**
- [ ] `.env.example` documents ALL required variables (no real values)
- [ ] `python-decouple` reads from `.env` locally
- [ ] App Runner console holds production secrets
- [ ] `.env` is in `.gitignore`
- [ ] App starts successfully with only the documented variables

---

## Done Criteria (from ROADMAP.md)

These are the FINAL validation gates. ALL must pass to close Phase 1:

1. [ ] `docker compose up` starts Django + PostgreSQL locally without errors
2. [ ] `Dockerfile` builds successfully — Tailwind compiles, collectstatic runs, Gunicorn starts
3. [ ] Database migrations run cleanly from scratch against local PostgreSQL AND Neon
4. [ ] All tables, enums, indexes, and constraints exist exactly as documented in `DATABASE_SCHEMA.md`
5. [ ] Custom User model with UUID pk works — can create a user via Django shell
6. [ ] HTMX is loaded in `base.html` and a test `hx-get` request works
7. [ ] Tailwind CSS compiles with custom theme tokens — a test page renders coral buttons and rounded cards correctly
8. [ ] Base template components render correctly
9. [ ] Resend API key configured — a test email sends successfully
10. [ ] WhiteNoise serves static files correctly when `DEBUG=False`
11. [ ] GitHub Actions pipeline runs lint + tests on push to `main`
12. [ ] Docker image pushes to ECR successfully from CI
13. [ ] App Runner deploys the image and responds on the custom domain with HTTPS
14. [ ] EventBridge Scheduler calls the internal endpoint every 5 minutes (endpoint returns 200 with valid token)
