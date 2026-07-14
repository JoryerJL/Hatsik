# Tech Stack — Hatsik

## Architecture

Django monolith with template-driven views, not an SPA and no public REST API. The server renders full HTML on initial load; **HTMX** handles partial updates without hand-written JavaScript.

## Stack

| Layer | Technology | Version | Notes |
|---|---|---|---|
| Backend framework | Django | 5.2.x | Templates + business logic |
| Frontend interactivity | HTMX | 2.x | `django-htmx`, use `request.htmx` to detect |
| Styling | Tailwind CSS | 4.x | Utility-first, standalone CLI (no Node/npm) |
| Database | PostgreSQL | 16.x | Hosted on Neon (serverless), driver `psycopg[binary]` |
| ORM | Django ORM | — | Migrations via `manage.py migrate` |
| Email | Resend | latest SDK | Transactional only: verification + password reset |
| Auth | Django auth + sessions | — | HTTP-only cookie, no JWT |
| QR generation | `qrcode` | 7.x | Generated on-demand, not persisted |
| Static files | whitenoise | 6.x | Served from container, no S3/CDN in MVP |
| Env config | python-decouple | 3.x | Reads `.env` locally, Lightsail deployment config in prod |
| Deploy | AWS Lightsail Containers | — | Docker image, $7/mo Nano plan, HTTPS included |
| CI/CD | GitHub Actions | — | lint → test → build → push Lightsail → deploy |
| Cron | AWS EventBridge Scheduler | — | Hits internal endpoint every 5 min for event auto-close |
| Python | 3.12.x | — | Pinned in `.python-version` and `Dockerfile` |

## Commands

```bash
# Local dev server
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Django system check
python manage.py check

# Create superuser
python manage.py createsuperuser

# Tests
pytest

# Lint / format (ruff replaces flake8 + black + isort)
ruff check .
ruff format --check .
ruff format .

# Tailwind CSS
make tailwind-watch    # dev, watch mode
make tailwind-build    # production, minified
make tailwind-install  # download standalone CLI binary (macOS arm64)

# Docker (local)
docker compose up
docker compose exec web python manage.py migrate

# Docker (production image)
docker build .
```

## Testing

- `pytest` + `pytest-django` for unit tests (validators, forms, token logic).
- Django `TestCase` + `Client` for view/integration tests (responses, redirects, sessions, middleware).
- Mock `resend.Emails.send` for email-sending tests — never hit the real API in tests.
- Settings module for tests: `config.settings.local` (set via `pyproject.toml` `DJANGO_SETTINGS_MODULE`).
- Test file conventions: `tests.py`, `test_*.py`, or `*_tests.py`; test classes `Test*`; test functions `test_*`.

## Dependency management

Split requirements files, pinned to minor version with `.*`:
- `requirements/base.txt` — shared runtime deps
- `requirements/local.txt` — adds `django-debug-toolbar`, `ruff`, `pytest`, `pytest-django`
- `requirements/production.txt` — just includes `base.txt`

## Key architecture decisions

- **No SPA/REST API**: avoids CORS/cross-origin auth complexity; one container, one deploy.
- **Session cookies, no JWT**: simpler, safer by default (not exposed to XSS), no refresh-token logic needed.
- **Lightsail Containers over ECS/EC2**: $7/mo fixed price, zero server administration, HTTPS included, no ALB needed.
- **Neon over RDS**: real free tier, swap is just changing `DATABASE_URL`.
- **Resend over SES**: fast setup, generous free tier, no sandbox approval needed.
- **EventBridge Scheduler over Celery+Redis**: no extra workers/containers, near-zero cost for a simple 5-minute cron.
- **whitenoise over S3+CloudFront**: sufficient for MVP static file serving, no bucket/CDN setup.

Full rationale and what's explicitly out of scope: `docs/ARCHITECTURE_AND_STACK.md`.

## Stitch Design Fidelity (MANDATORY)

Every template/UI that has a corresponding Stitch screen MUST be built from the actual Stitch HTML source code. This is a hard rule, not a guideline.

### Process

1. **Download the HTML source** from Stitch via the MCP `get_screen` tool to get the `htmlCode.downloadUrl`, then `curl` it to `docs/stitch-html/{screen-name}.html`.
2. **Read the downloaded HTML** to understand the exact structure, classes, tokens, spacing, and layout that Stitch generated.
3. **Replicate the design** in Django templates using the same CSS classes, structure, and tokens. Adapt only what's necessary for Django template logic ({% for %}, {% if %}, {% url %}, form fields).
4. **Never invent layout or styling** — if Stitch uses a sidebar, use a sidebar. If Stitch uses a top bar, use a top bar. If Stitch uses rounded-full inputs, use rounded-full inputs.

### What to preserve from Stitch

- Layout structure (grid columns, flex directions, positioning)
- Font sizes and weights (headline-md = 20px/28px/700, body-md = 14px/20px/400, etc.)
- Color token usage (primary, secondary, surface-container-*, on-surface-variant, etc.)
- Border radii (rounded-xl, rounded-full, rounded-2xl)
- Spacing values (xs=4, sm=8, md=12, lg=16, xl=24)
- Icon font (Material Symbols Outlined with variation settings)
- Component patterns (card-status-indicator, hatsik-input focus rings, etc.)

### What to adapt for Django

- Replace hardcoded content with {{ template_vars }}
- Replace `<a href="#">` with `{% url 'app:name' %}`
- Replace static `<form>` with `method="post"` + `{% csrf_token %}`
- Replace static images with `{% static 'img/...' %}`
- Add conditional blocks (`{% if is_owner %}`, `{% for item in items %}`)

### Reference files

All Stitch HTML sources live in `docs/stitch-html/` for permanent reference. They are NOT committed to git (add to .gitignore) but must be downloaded fresh when needed.
