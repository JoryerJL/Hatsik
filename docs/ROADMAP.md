# ROADMAP.md — Hatsik Implementation Roadmap

> **Version:** 1.1
> **Date:** 2026-07-12
> **Status:** Active
> **Project:** Hatsik Unified Web System
> **Stitch Project:** [View in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339)

---

## Overview

This roadmap organizes the MVP implementation into **6 sequential phases**, each one testable and shippable on its own. Every phase builds on top of the previous one, strictly following module dependency order.

**Core principle:** independent modules ship first; dependent modules ship only after their foundation is stable.

```
Phase 1: Foundation        → Infrastructure, DB, design system
Phase 2: Auth              → Registration, login, email verification
Phase 3: Events            → Create, manage, share events
Phase 4: Event Access      → Join flow, request management
Phase 5: Items + Moderation → List management + item suggestions
Phase 6: Assignments        → Claim, track, and mark items as purchased
```

---

## Module Dependency Graph

```
Auth ──────────────────────────────────┐
  └─→ Dashboard                        │
  └─→ Events ─────────────────────────→┤
        └─→ EventAccess ───────────────→┤
              └─→ Items ───────────────→┤
                    └─→ Assignments    │
                    └─→ Moderation ────┘

Notifications → POST-MVP (not in scope)
```

**Rule:** A module CANNOT be implemented before all modules it depends on are complete and tested.

---

## Stitch Design Reference

All UI screens referenced in this roadmap belong to:

- **Project ID:** `17560302013947311339`
- **Design System Asset:** `assets/4b0bfd162b1d461cbdd85c1d0ab945ef` (Warm Kitchen Board)
- **Base URL pattern:** `https://stitch.withgoogle.com/projects/17560302013947311339`

### Screen Inventory

| Screen ID | Title | Module | Phase |
|---|---|---|---|
| `31616452da9645128f2c492244260487` | Iniciar Sesión | Auth | 2 |
| `4e62e0c5470344a8acba2468d6b8cecd` | Registro de Usuario | Auth | 2 |
| `8612ccf1e1304ff9bd3a5090ddf8f9c7` | Verificación Pendiente | Auth | 2 |
| `b533a824d16a4fd39fcc7135a1404392` | Recuperar Contraseña | Auth | 2 |
| `d3b60fbd13ef45dd8b0fa6149ec4e5ef` | Restablecer Contraseña | Auth | 2 |
| `533ded11556f4dc0a43dd05c0a1632e1` | Mis Eventos (Dashboard) | Dashboard | 3 |
| `f9af4a49a1884a31b077ace0c40a4418` | Crear Evento | Events | 3 |
| `b30692ae80c94ae6b69be8e1df8595c6` | Ficha del Evento | Events | 3 |
| `32075f1d510242cdb9b880d66edea76c` | Detalle del Evento | Events + Items | 3–5 |
| `95c384794de3421cb9780b51f3ed2478` | Invitar Amigos | Events | 3 |
| `e9b1b3a8511c4ef882584dffe0b086ba` | Solicitud Pendiente | EventAccess | 4 |
| `701373d8c8384b49891b4e60050ab12f` | Gestión de Solicitudes | EventAccess | 4 |
| `f4ee82a1da0542898d47b5e0eaabe809` | Añadir Ítem | Items | 5 |
| `4264f659cdcc4d2c931e77a63c27063a` | Editar Ítem | Items | 5 |
| `0c8fa38e491e43c2a5da6a3d984f702e` | Sugerir Ítem | Moderation | 5 |

---

## Phase 1 — Foundation

> **Goal:** Working project skeleton. Nothing user-facing yet, but everything else depends on this.
> **Module:** Infrastructure (no product module)
> **Depends on:** Nothing — this is the starting point.
> **Stitch screens in this phase:** None

### What gets built

#### 1. Project structure (Django monolith)

Create the folder structure defined in `ARCHITECTURE_AND_STACK.md`:

```
hatsik/
├── .github/workflows/deploy.yml
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/
│   ├── events/
│   ├── items/
│   ├── moderation/
│   └── internal/
├── templates/
│   ├── base.html
│   ├── partials/
│   └── components/
├── static/
│   ├── css/main.css
│   ├── js/htmx.min.js
│   └── img/
├── docs/
├── .env.example
├── .python-version          ← "3.12"
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── pyproject.toml
└── requirements/
    ├── base.txt
    ├── local.txt
    └── production.txt
```

- **Python 3.12** runtime, pinned in `.python-version` and `Dockerfile`.
- **Django 5.2.x** as the web framework. Function-based views.
- **django-htmx** installed and configured as middleware.
- **Gunicorn** as production WSGI server.
- **python-decouple** for environment variable management.

#### 2. Containerization & local dev

- **`Dockerfile`** — production image: Python 3.12 slim, installs dependencies, builds Tailwind CSS, runs collectstatic, serves via Gunicorn.
- **`docker-compose.yml`** — local development: Django app + PostgreSQL 16 container. Hot-reload with `runserver`.
- Both must build and run with `docker compose up` without errors.

#### 3. Database (PostgreSQL 16 on Neon)

Full schema from `DATABASE_SCHEMA.md` implemented as Django models and migrations:

- **Tables:** `users`, `email_verification_tokens`, `password_reset_tokens`, `events`, `event_participations`, `event_items`, `item_assignments`, `item_suggestions`.
- **Enums:** `event_status`, `event_role`, `access_status`, `suggestion_status`, `item_unit` — implemented as Django `TextChoices`.
- **All indexes and unique constraints** defined in the schema.
- **Custom User model** (`AbstractBaseUser` or `AbstractUser`) in `apps/accounts/models.py` with UUID pk.
- **Driver:** `psycopg[binary]` 3.2.x.
- **Connection:** `DATABASE_URL` via `python-decouple`, pointing to Neon in production.

#### 4. Tailwind CSS 4.x integration

- **Tailwind CLI standalone binary** (no Node.js dependency). Downloaded as part of Docker build.
- `static/css/input.css` → compiled to `static/css/main.css`.
- Custom `manage.py tailwind` command or Makefile target for local dev (`--watch`) and production (`--minify`).
- Design tokens from `hatsik-brand-identity.md` and `UI_UX_SPEC.md` configured as Tailwind theme (`@theme` in Tailwind v4):
  - Colors: `--color-primary` (#E8432D), `--color-primary-hover` (#F26B54), `--color-primary-soft` (#FDE8E4), state colors.
  - Typography: Nunito (headings), Plus Jakarta Sans (body) — loaded from Google Fonts in `base.html`.
  - Spacing: `--space-1` through `--space-6`.
  - Radii: `--radius-card` (16px), `--radius-button` (12px), `--radius-input` (10px), `--radius-pill` (999px).

#### 5. Base templates and UI components

- **`templates/base.html`** — HTML shell with: `<head>` (fonts, Tailwind CSS, HTMX), `<body>` with nav structure (responsive header per `UI_UX_SPEC.md`), Django block structure (`{% block content %}`).
- **Reusable template partials** (`templates/components/`):
  - `_button.html` — primary, secondary, destructive variants.
  - `_card.html` — event card shell with rounded corners and soft border.
  - `_badge.html` — pill-shaped status badges with semaphore colors.
  - `_modal.html` — confirmation dialog shell (HTMX-powered).
  - `_input.html` — form input with label, error state, focus ring.
  - `_toast.html` — ephemeral feedback message.
- All components use Tailwind utility classes matching the Warm Kitchen Board design tokens.
- **HTMX 2.x** included as a static JS file (direct copy, no npm).

#### 6. Email infrastructure (Resend)

- **Resend SDK** (`resend` 2.x) configured with `RESEND_API_KEY`.
- Utility module (`apps/accounts/emails.py` or similar) with functions for:
  - Sending verification email.
  - Sending password reset email.
- Email templates: plain text + simple HTML. Branded with Hatsik logo and coral accent.
- Verified: a test email sends successfully from local and Docker environments.

#### 7. Static files serving

- **WhiteNoise 6.x** configured in production settings — serves static files from the container without S3.
- `collectstatic` runs as part of Docker build.
- In local dev: Django's built-in static serving (`DEBUG=True`).

#### 8. CI/CD pipeline (GitHub Actions)

- **`.github/workflows/deploy.yml`:**
  1. Run `ruff` (linting) + `ruff format --check` (formatting).
  2. Run Django tests (`python manage.py test`).
  3. Build Docker image.
  4. Push to AWS ECR.
  5. Trigger AWS App Runner deployment.
- Pipeline runs on every push to `main`.

#### 9. Production infrastructure (AWS)

- **AWS ECR** repository created — stores Docker images.
- **AWS App Runner** service created — pulls from ECR, auto-deploys on new image push.
- **Custom domain** + SSL certificate via AWS ACM configured on App Runner.
- **AWS EventBridge Scheduler** — calls `POST /internal/close-expired-events/` every 5 minutes with `X-Internal-Token` header.

#### 10. Environment variables

`.env.example` documenting all required variables:

```bash
# Django
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Neon)
DATABASE_URL=postgres://user:password@host/dbname

# Email (Resend)
RESEND_API_KEY=

# Internal endpoints (EventBridge cron)
INTERNAL_CRON_TOKEN=

# AWS (CI/CD only — not in App Runner env)
AWS_REGION=
ECR_REPOSITORY=
APPRUNNER_SERVICE_ARN=
```

### Done criteria

- [ ] `docker compose up` starts Django + PostgreSQL locally without errors.
- [ ] `Dockerfile` builds successfully — Tailwind compiles, collectstatic runs, Gunicorn starts.
- [ ] Database migrations run cleanly from scratch against local PostgreSQL AND Neon.
- [ ] All tables, enums, indexes, and constraints exist exactly as documented in `DATABASE_SCHEMA.md`.
- [ ] Custom User model with UUID pk works — can create a user via Django shell.
- [ ] HTMX is loaded in `base.html` and a test `hx-get` request works.
- [ ] Tailwind CSS compiles with custom theme tokens — a test page renders coral buttons and rounded cards correctly.
- [ ] Base template components (`_button.html`, `_card.html`, `_badge.html`, `_modal.html`, `_input.html`) render correctly.
- [ ] Resend API key configured — a test email sends successfully.
- [ ] WhiteNoise serves static files correctly when `DEBUG=False`.
- [ ] GitHub Actions pipeline runs lint + tests on push to `main`.
- [ ] Docker image pushes to ECR successfully from CI.
- [ ] App Runner deploys the image and responds on the custom domain with HTTPS.
- [ ] EventBridge Scheduler calls the internal endpoint every 5 minutes (endpoint returns 200 with valid token).

---

## Phase 2 — Auth

> **Goal:** A user can register, verify their email, log in, log out, and recover their password. No anonymous access.
> **Module:** `Auth`
> **Depends on:** Phase 1 (database, email infrastructure, design tokens)
> **Stitch screens in this phase:**

| Screen | ID | Preview |
|---|---|---|
| Registro de Usuario | `4e62e0c5470344a8acba2468d6b8cecd` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Verificación Pendiente | `8612ccf1e1304ff9bd3a5090ddf8f9c7` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Iniciar Sesión | `31616452da9645128f2c492244260487` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Recuperar Contraseña | `b533a824d16a4fd39fcc7135a1404392` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Restablecer Contraseña | `d3b60fbd13ef45dd8b0fa6149ec4e5ef` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |

### What gets built

**Registration**
- Form: `display_name`, `email`, `password` (min 8 chars, at least 1 letter + 1 number).
- On submit: create user with `email_verified_at = NULL`, generate verification token (24h TTL), send verification email.
- Redirect unverified users to the Verificación Pendiente screen on any protected route.

**Email verification**
- Token link flow: on click, mark `email_verified_at`, consume token.
- Resend button: rate-limited to 1 request per 60 seconds per user.
- Expired token: show error with resend option.

**Login**
- Form: `email`, `password`.
- Unverified account: accept login, redirect to Verificación Pendiente screen — no access to the app.
- Invalid credentials: generic error (do not reveal whether email exists).
- Session management: Django session with secure HTTP-only cookie (no JWT — per `ARCHITECTURE_AND_STACK.md`).

**Logout**
- Destroy session / invalidate token.

**Password recovery**
- Request form: email input → always show generic success message (do not reveal if email exists).
- Rate limit: 1 request per 60 seconds per email.
- Recovery email: link with token (1h TTL).
- Reset form: new password with same validation rules.
- Token consumed after first use.

**Route protection**
- All app routes redirect to `/login` if unauthenticated.
- Unverified accounts are redirected to `/verify-email` on any protected route.

### Business rules to enforce

- No anonymous access — every user must have an account.
- Unverified account: can log in, sees only the verification screen, cannot create events, join events, or interact with any event.
- Error messages must never reveal whether an email exists in the system.
- OAuth is out of scope for this phase (post-MVP roadmap item).

### Done criteria

- [ ] User can register, receive verification email, click the link, and access the app.
- [ ] Unverified user is blocked from all app features and sees the Verificación Pendiente screen.
- [ ] Resend verification email enforces 60-second rate limit.
- [ ] User can log in with verified account.
- [ ] Unverified account login redirects to verification screen.
- [ ] Invalid credentials show generic error.
- [ ] Password recovery sends email and allows password reset.
- [ ] Expired tokens show appropriate error.
- [ ] All 5 Stitch screens (Registro, Verificación, Login, Recuperar Contraseña, Restablecer Contraseña) are implemented matching the design system.

---

## Phase 3 — Events & Dashboard

> **Goal:** A verified user can create events, see their events on the dashboard, manage the event lifecycle (close, reopen, cancel), share the event link and QR, manage co-admins, and remove participants.
> **Modules:** `Dashboard`, `Events`
> **Depends on:** Phase 2 (verified user session)
> **Stitch screens in this phase:**

| Screen | ID | Preview |
|---|---|---|
| Mis Eventos (Dashboard) | `533ded11556f4dc0a43dd05c0a1632e1` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Crear Evento | `f9af4a49a1884a31b077ace0c40a4418` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Ficha del Evento | `b30692ae80c94ae6b69be8e1df8595c6` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Detalle del Evento | `32075f1d510242cdb9b880d66edea76c` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Invitar Amigos | `95c384794de3421cb9780b51f3ed2478` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |

### What gets built

**Dashboard (`Mis Eventos`)**
- List of events where the user is Owner, Co-admin, or accepted Participant.
- Each card shows: event name, date, user's role, event status (`active`, `closed`, `cancelled`).
- Cancelled events remain visible as history.
- Empty state when no events exist.

**Create Event (`Crear Evento`)**
- Form: `name` (required), `event_date` (required), `description` (optional), `assignment_deadline_at` (optional).
- On create: insert `events` row + insert Owner participation row (`role = owner`, `access_status = accepted`).
- Auto-generate `public_share_token` (UUID).
- No mandatory confirmation dialog on submit.

**Event Card / Ficha del Evento (`Ficha del Evento`)**
- Public-facing view of the event (visible even before a user joins).
- Shows: name, description, date. Does NOT show the item list to non-participants.
- Used as the landing page when a non-member follows the share link.

**Event Detail (`Detalle del Evento`)**
- Full view for accepted participants.
- Sections: event header (name, date, status), item list (built in Phase 5), request badges (built in Phase 4), participant list.
- Edit event: name, description, date, deadline — no confirmation required.
- Close event manually: requires confirmation dialog.
- Reopen event: requires confirmation dialog.
- Cancel event: requires confirmation dialog.
- Co-admin management: assign co-admin (no confirmation), revoke co-admin (requires confirmation).
- Remove participant: requires confirmation; blocked if participant has purchased assignments.

**Share / Invitar Amigos (`Invitar Amigos`)**
- Display the shareable link.
- QR code rendered on-demand from `public_share_token` — not stored in DB.
- QR downloadable as PNG.

**Automatic closure**
- Background job or cron: when `assignment_deadline_at` is reached, set `status = closed`.

### Business rules to enforce

- Only the Owner can edit event data, close, reopen, cancel, assign/revoke co-admins, remove participants.
- A cancelled event cannot be reopened.
- Removing a participant with purchased assignments is blocked.
- Owner cannot remove themselves.
- Revoking a co-admin preserves their existing assignments.
- A removed participant can re-request entry via the share link (re-enters as a regular Participant).

### Done criteria

- [ ] User can create an event and see it on the Dashboard.
- [ ] Dashboard shows correct role and status for each event.
- [ ] Share link and downloadable QR are generated correctly.
- [ ] Owner can close, reopen, and cancel the event (each with confirmation).
- [ ] Owner can assign and revoke co-admins (revoke requires confirmation).
- [ ] Owner can remove participants (blocked if they have purchased assignments).
- [ ] Automatic closure fires when `assignment_deadline_at` is reached.
- [ ] All 5 Stitch screens for this phase match the design system.

---

## Phase 4 — Event Access

> **Goal:** A user can join an event via link or QR, go through the approval flow, and be accepted or rejected by Owner/Co-admin. Users can also leave events voluntarily.
> **Module:** `EventAccess`
> **Depends on:** Phase 3 (events must exist; share link and roles must be working)
> **Stitch screens in this phase:**

| Screen | ID | Preview |
|---|---|---|
| Solicitud Pendiente | `e9b1b3a8511c4ef882584dffe0b086ba` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Gestión de Solicitudes | `701373d8c8384b49891b4e60050ab12f` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |

> Note: `Ficha del Evento` (screen `b30692ae80c94ae6b69be8e1df8595c6`) built in Phase 3 also serves as the entry point for this flow. Its "join request" behavior is completed here.

### What gets built

**Join flow**
- User follows the share link → if not logged in, redirected to login (then back to the event).
- Registered and verified user sees Ficha del Evento with a "Request to join" button.
- On submit: create `event_participations` row with `access_status = pending`. No confirmation required.
- Attempting to join a `closed` or `cancelled` event is blocked.

**Solicitud Pendiente state (`Solicitud Pendiente` screen)**
- After submitting, the user sees the event card + a "Your request is pending approval" message.
- The item list is NOT visible while pending.
- If rejected: user sees the rejected status. Cannot request again.
- Rejected → accepted correction: Owner/Co-admin can change a rejected request to accepted.

**Request management (`Gestión de Solicitudes`)**
- Owner and Co-admins see a "Pending Requests" section inside the event detail.
- Each request shows the applicant's `display_name` and `email`.
- Accept: no confirmation required. Sets `access_status = accepted`.
- Reject: requires confirmation. No rejection reason required in MVP. Sets `access_status = rejected`.
- Badge with pending request count shown on the event card in Dashboard.

**Leave event**
- Participant can leave voluntarily if they have no active (non-purchased) assignments.
- Confirmation required.
- Blocked if participant has purchased assignments.
- If a Co-admin leaves, their co-admin role is automatically revoked.
- Owner cannot leave their own event.
- A user who left can re-request entry via the share link.

### Business rules to enforce

- Tener el link does NOT grant automatic access to the item list.
- A rejected user cannot re-request access — unless Owner/Co-admin corrects the rejection manually.
- A rejected → accepted → voluntarily left user CAN re-request entry.
- Re-joining always enters as a regular Participant (no automatic role restoration).

### Done criteria

- [ ] User following share link reaches Ficha del Evento.
- [ ] Unauthenticated user is redirected to login and returned to the event after.
- [ ] Join request is created and user sees the pending state screen.
- [ ] Item list is hidden for pending and rejected users.
- [ ] Owner and Co-admin can approve and reject requests.
- [ ] Rejection requires confirmation. Approved rejection can be corrected to accepted.
- [ ] Rejected user cannot re-request entry (unless corrected).
- [ ] Participant can leave voluntarily (with confirmation), blocked if purchased assignments exist.
- [ ] Co-admin role auto-revoked on voluntary leave.
- [ ] Both Stitch screens for this phase match the design system.

---

## Phase 5 — Items & Moderation

> **Goal:** Owner can manage the item list. Participants can suggest new items. Owner/Co-admin can approve or reject suggestions.
> **Modules:** `Items`, `Moderation`
> **Depends on:** Phase 4 (accepted participants must exist; event roles must be enforced)
> **Stitch screens in this phase:**

| Screen | ID | Preview |
|---|---|---|
| Añadir Ítem | `f4ee82a1da0542898d47b5e0eaabe809` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Editar Ítem | `4264f659cdcc4d2c931e77a63c27063a` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |
| Sugerir Ítem | `0c8fa38e491e43c2a5da6a3d984f702e` | [Open in Stitch](https://stitch.withgoogle.com/projects/17560302013947311339) |

> Note: Items are displayed inside Detalle del Evento (screen `32075f1d510242cdb9b880d66edea76c`), built in Phase 3. This phase completes that screen's item list section.

### What gets built

**Item management (Owner only)**

- Add item (`Añadir Ítem`): name (required), `quantity_total` (optional), `unit` (required if quantity is set, from controlled catalog).
- No confirmation required on add.
- Item states are computed, not stored — derived from assignments at query time.
- Edit item (`Editar Ítem`):
  - No assignments: edit name, quantity, unit. No confirmation required.
  - Has assignments: edit quantity total only. Must show warning. Requires confirmation.
  - Cannot reduce quantity below sum of active assignments.
- Delete item: requires confirmation. Deletes item and all associated assignments.
- Cannot add/edit/delete items in `closed` or `cancelled` events.

**Unit catalog (controlled list — no free text)**

`kg`, `g`, `liters`, `ml`, `pieces`, `packages`, `bags`, `boxes`, `cans`, `bottles`, `jugs`, `trays`, `dozens`

**Item status display (computed)**

| State | Color token | Condition |
|---|---|---|
| `sin_asignar` | `state-unassigned` (#FCA5A5) | No active assignments |
| `parcialmente_cubierto` | `state-partial` (#FDBA74) | Sum of assignments < total quantity |
| `cubierto` | `state-covered` (#86EFAC) | Sum of assignments = total quantity |
| `parcialmente_comprado` | `state-partial-bought` (#93C5FD) | Some but not all assignees marked purchased |
| `comprado` | `state-bought` (#4ADE80) | All assignees marked purchased |

> Binary items (no quantity): `sin_asignar` → `cubierto` → `comprado`

**Item suggestions — Participant flow (`Sugerir Ítem`)**

- Suggest item: name (required), quantity + unit (optional). No confirmation required.
- Suggested items are NOT visible in the official list until approved.
- Participant can edit their own pending suggestion (no confirmation required).
- Participant can delete their own pending suggestion (requires confirmation).
- Participant sees the status of their suggestion (pending / approved / rejected + rejection note).

**Item suggestions — Moderation flow (Owner / Co-admin)**

- "Pending Suggestions" section in event detail.
- Approve: optionally modify name, quantity, or unit first. No confirmation required.
  - Approved suggestion creates an official item with `status = sin_asignar`. The item does NOT show "suggested by".
- Reject: with optional rejection note. Requires confirmation.
  - Rejection note is visible to the suggester and to Owner/Co-admins in the suggestion history.

### Business rules to enforce

- Only the Owner manages the official item list.
- Item status is never stored — always computed from `item_assignments`.
- Controlling unit prevents free-text abuse (enforced both at DB level with enum and at UI level with a select).
- Modifying quantity with existing assignments always shows a warning before the confirmation dialog.

### Done criteria

- [ ] Owner can add, edit, and delete items.
- [ ] Edit of quantity-constrained item with assignments shows warning and requires confirmation.
- [ ] Reduction below assigned quantity is blocked.
- [ ] Item status is computed correctly and displays with the correct semaphore color.
- [ ] Participants can suggest items; suggestions are hidden from the official list until approved.
- [ ] Participants can edit and delete their own pending suggestions.
- [ ] Owner/Co-admin can approve (with optional pre-approval edits) and reject suggestions.
- [ ] Rejection note is visible to the suggester.
- [ ] Approved suggestion becomes an official item without attributing the suggestion author.
- [ ] All 3 Stitch screens for this phase match the design system.

---

## Phase 6 — Assignments

> **Goal:** Participants can claim items (partially or fully), modify their claims, mark them as purchased. Owner can cancel others' claims.
> **Module:** `Assignments`
> **Depends on:** Phase 5 (items must exist and have computed status; participant roles must be enforced)
> **Stitch screens in this phase:** None (assignments UI lives inside Detalle del Evento, screen `32075f1d510242cdb9b880d66edea76c`, already built in Phase 3)

### What gets built

**Claim an item**

- Accepted participant selects an item from the list.
- Quantified item: input for `quantity_assigned`. Validation: sum of all active assignments cannot exceed `quantity_total`.
- Binary item: "I'll bring this" toggle — binary, no quantity input.
- Covered item: assign button is disabled but assignees are still visible.
- No confirmation required on create.

**Modify own assignment**

- Can modify own non-purchased assignment.
- No confirmation required.
- Cannot modify quantity to exceed available quantity.

**Cancel own assignment**

- Requires confirmation.
- Blocked if assignment is already purchased.
- On cancel: quantity returns to available pool. Item status recomputed.

**Mark as purchased**

- Any assignee can mark their own part as purchased.
- Owner and Co-admin can mark ANY assignment as purchased.
- Requires confirmation (cannot be undone in MVP).
- Purchased assignments cannot be modified or cancelled.
- Item status recalculated after marking:
  - Some assignees purchased → `parcialmente_comprado`.
  - All assignees purchased → `comprado`.
- Marking as purchased is allowed even when event is `closed`.
- Marking as purchased is blocked when event is `cancelled`.

**Cancel others' assignments (Owner only)**

- Owner can cancel any non-purchased assignment of any participant.
- Requires confirmation.
- Co-admin CANNOT cancel others' assignments.

**Progress bar**

- Shown in event detail: percentage of items fully covered or purchased.

**Highlighted uncovered items at closure**

- When event status is `closed`, items in `sin_asignar` or `parcialmente_cubierto` are highlighted in red.
- No automatic reassignment in MVP.

### Business rules to enforce

- Sum of active assignments for a quantified item can never exceed `quantity_total`.
- Purchased assignments are immutable — no modifications, no cancellation.
- In `cancelled` events: no new assignments, no modifications, no cancellations, no "mark as purchased".
- In `closed` events: no new assignments, no modifications, no cancellations — but marking as purchased IS allowed.
- Co-admin cannot cancel others' assignments (only Owner can).

### Done criteria

- [ ] Participant can claim a quantified item with a valid quantity.
- [ ] Claim is blocked when the quantity would exceed the item total.
- [ ] Binary item claim works without quantity input.
- [ ] Participant can modify their own non-purchased assignment.
- [ ] Participant can cancel their own non-purchased assignment (with confirmation).
- [ ] Marking as purchased requires confirmation and is irreversible in MVP.
- [ ] Marking as purchased is allowed in closed events.
- [ ] Marking as purchased is blocked in cancelled events.
- [ ] Owner can cancel any non-purchased assignment (with confirmation).
- [ ] Co-admin cannot cancel others' assignments.
- [ ] Item status semaphore updates correctly after every assignment/purchase/cancellation action.
- [ ] Progress bar reflects overall event completion.
- [ ] Uncovered items are highlighted when event is closed.

---

## MVP Completion Checklist

When all 6 phases are done and their done criteria are met, the MVP is complete.

**Cross-cutting concerns** that must be verified across all phases:

- [ ] All routes enforce authentication (no anonymous access).
- [ ] Unverified accounts are blocked from all product features.
- [ ] Role-based access control is enforced server-side, not just in the UI.
- [ ] All confirmation dialogs match the Warm Kitchen Board design system.
- [ ] Coral semaphore system (`state-*` color tokens) is used consistently.
- [ ] Event status transitions (`active` → `closed` → `active` → `cancelled`) are correctly enforced.
- [ ] Transactional emails (verification, password reset) are the ONLY emails sent in MVP.
- [ ] No notification system, no email events (post-MVP scope).
- [ ] All UI screens are implemented matching the Stitch Warm Kitchen Board design tokens.

---

## Post-MVP Roadmap (not scoped)

| Feature | Description |
|---|---|
| OAuth (Google) | Social login for faster onboarding |
| Event notifications by email | Notify Owner of new requests, participants of status changes |
| In-app notification center | Real-time updates within the app |
| Item photo upload | Visual reference per item |
| List templates | "Kit asado básico" and similar presets |
| Multiple lists per event | More than one shopping list per convivio |
| Event history and analytics | Past events summary and stats |
| Invite by email/phone | Send invitations directly from the app |
| Public event directory | Optional public events with search |
| Progressive Web App (PWA) | Offline support and installable app |
| Native mobile app | iOS and Android |
| Shared payments (vaquita) | Cost splitting between participants |

---

## Architecture Decisions (resolved)

Decisions made during documentation review. These are binding for implementation.

| # | Decision | Rationale |
|---|---|---|
| AD-1 | **Mobile-first, responsive design** | Primary use case is mobile (sharing lists at events, checking items on the go). All layouts start from small screens and scale up with `md:` / `lg:` breakpoints. Stitch screens are desktop reference but implementation prioritizes mobile viewport first. |
| AD-2 | **Typography: Nunito (headings) + Plus Jakarta Sans (body)** | Confirmed per `hatsik-brand-identity.md`. The Stitch design system uses the same fonts. |
| AD-3 | **Event routing: single URL with conditional template** | `/events/<uuid:pk>/` renders `Ficha del Evento` (public card) for non-participants or pending/rejected users, and `Detalle del Evento` (full operational view) for accepted participants. One Django view, two template paths based on `access_status`. |
| AD-4 | **Enum values in English, UI labels in Spanish** | DB enums (`item_unit`, `event_status`, etc.) use English identifiers. The display layer maps them to Spanish labels for the user. No localization framework needed — a simple dict/choices display is sufficient for MVP. |
| AD-5 | **Django sessions, no JWT** | Per `ARCHITECTURE_AND_STACK.md`. HTTP-only session cookie. No refresh token logic. |
| AD-6 | **Rate limiting via DB timestamp** | No Redis needed. Check `created_at` of last token (verification/recovery) in the DB. If < 60 seconds, reject. |

---

## Reference Documents

| Document | Path |
|---|---|
| Product Overview | `docs/PRODUCT_OVERVIEW.md` |
| Modules Specification | `docs/MODULES_SPEC.md` |
| Database Schema | `docs/DATABASE_SCHEMA.md` |
| UI/UX Specification | `docs/UI_UX_SPEC.md` |
| Brand Identity | `docs/hatsik-brand-identity.md` |
| Stitch Design System | `assets/4b0bfd162b1d461cbdd85c1d0ab945ef` |
