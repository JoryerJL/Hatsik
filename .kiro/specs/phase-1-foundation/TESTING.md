# Phase 1 — Foundation: Testing Guide

> How to verify everything works after cloning and setting up the project.

---

## Prerequisites

- Python 3.12+ installed
- PostgreSQL running locally (pgAdmin or similar)
- Database `hatsik` created (owner: `postgres`)

---

## 1. Setup

```bash
# Clone and enter the project
cd Hatsik

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements/local.txt

# Create .env from example
cp .env.example .env
```

Edit `.env` with your local values:
```bash
SECRET_KEY=any-random-string-for-local-dev
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres@localhost:5432/hatsik
RESEND_API_KEY=
INTERNAL_CRON_TOKEN=dev-internal-token
```

---

## 2. Database — Migrations

```bash
# Apply all migrations
python manage.py migrate
```

**Expected output:** 23 migrations applied without errors.

**Verify tables exist:**
```bash
psql -U postgres -d hatsik -c "\dt"
```

Should show: `users`, `email_verification_tokens`, `password_reset_tokens`, `events`, `event_participations`, `event_items`, `item_assignments`, `item_suggestions` + Django internal tables.

---

## 3. User Model — Create a test user

```bash
python manage.py shell -c "
from apps.accounts.models import User
user = User.objects.create_user(
    email='test@hatsik.com',
    display_name='Test User',
    password='test1234'
)
print(f'User: {user.id} | {user.email}')
"
```

**Expected:** UUID printed, no errors.

---

## 4. Django Dev Server

```bash
python manage.py runserver
```

**Visit:** http://localhost:8000/admin/ — Django admin login should render.

**Create superuser for admin access:**
```bash
python manage.py createsuperuser
# Enter: email, display_name, password
```

---

## 5. Component Gallery (UI Verification)

**Visit:** http://localhost:8000/dev/components/

**Should render:**
- ✅ 3 button variants (Primary coral, Secondary gray, Destructive red)
- ✅ 5 badge variants (Success, Warning, Error, Info, Neutral)
- ✅ Card with rounded corners and border
- ✅ 3 input states (normal, placeholder, error)
- ✅ HTMX test button → clicking it shows "✓ HTMX is working!"

> **Note:** Styling requires Tailwind CSS compiled. If buttons appear unstyled, run:
> ```bash
> make tailwind-install  # downloads the binary (first time only)
> make tailwind-build    # compiles static/css/main.css
> ```
> Then refresh the page.

---

## 6. HTMX Test

On the component gallery page (`/dev/components/`), click the blue "Test hx-get →" button.

**Expected:** The dashed box below it should show: `✓ HTMX is working!`

---

## 7. Internal Endpoint (EventBridge Stub)

```bash
# Should return 401 without token
curl -X POST http://localhost:8000/internal/close-expired-events/
# {"error": "Unauthorized"}

# Should return 200 with valid token
curl -X POST http://localhost:8000/internal/close-expired-events/ \
  -H "X-Internal-Token: dev-internal-token"
# {"status": "ok", "closed_count": 0}
```

---

## 8. Tailwind CSS Compilation

```bash
# Install Tailwind CLI (first time only)
make tailwind-install

# Build for production (minified)
make tailwind-build

# Watch mode for development (auto-recompiles on save)
make tailwind-watch
```

**Verify tokens compiled:**
```bash
grep "E8432D" static/css/main.css && echo "✓ Color tokens present"
```

---

## 9. Linting

```bash
# Check for errors
ruff check .

# Check formatting
ruff format --check .

# Auto-fix formatting
ruff format .
```

**Expected:** All checks passed.

---

## 10. Django System Check

```bash
python manage.py check
```

**Expected:** `System check identified no issues (0 silenced).`

---

## Quick Verification Checklist

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 1 | Django starts | `python manage.py runserver` | No errors, serves on :8000 |
| 2 | DB migrated | `python manage.py migrate` | 23 migrations applied |
| 3 | User created | Django shell (see above) | UUID user created |
| 4 | Admin works | Visit `/admin/` | Login page renders |
| 5 | Components render | Visit `/dev/components/` | Buttons, badges, cards visible |
| 6 | HTMX works | Click test button | "HTMX is working!" appears |
| 7 | Internal endpoint | curl with token | Returns 200 + JSON |
| 8 | Tailwind compiles | `make tailwind-build` | main.css generated |
| 9 | Lint passes | `ruff check . && ruff format --check .` | All passed |
| 10 | Check passes | `python manage.py check` | No issues |

---

## Pending (Require External Setup)

| Item | What's needed | When |
|------|---------------|------|
| Docker compose up | Open Docker Desktop, then `docker compose up` | Before deploy |
| Resend email test | Add real `RESEND_API_KEY` to `.env` | Before Phase 2 |
| AWS ECR + App Runner | Provision via AWS Console | Before first deploy |
| EventBridge Scheduler | Create in AWS Console | Before Phase 3 |
| Neon DB | Configure `DATABASE_URL` in App Runner | Before first deploy |
