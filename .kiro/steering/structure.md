# Project Structure — Hatsik

## Folder layout

```
hatsik/
├── config/                      # Django project config
│   ├── settings/
│   │   ├── base.py              # shared settings
│   │   ├── local.py              # dev overrides
│   │   └── production.py         # prod overrides (App Runner)
│   ├── urls.py                   # root urlconf
│   └── wsgi.py
│
├── apps/                        # one Django app per product module
│   ├── accounts/                 # auth: register, login, logout, verify, reset
│   ├── events/                   # Event, EventParticipation
│   ├── items/                    # EventItem, ItemAssignment
│   ├── moderation/                # ItemSuggestion (suggest/approve/reject)
│   └── internal/                  # cron/internal endpoints (e.g. close_expired_events)
│
├── templates/                    # base + shared templates
│   ├── base.html                  # layout, nav, head, scripts
│   ├── partials/                  # HTMX fragments, prefixed with `_`
│   ├── components/                # server-logic-free UI components
│   └── dev/                       # internal component/style preview pages
│
├── static/
│   ├── css/main.css               # Tailwind output — generated, don't hand-edit
│   ├── js/                        # HTMX bundle (no npm)
│   └── img/
│
├── docs/                         # product/architecture source-of-truth docs
├── requirements/                  # base.txt / local.txt / production.txt
├── .kiro/specs/                   # phase-based spec docs (requirements/design/tasks)
├── manage.py
├── pyproject.toml                 # ruff config + pytest config
├── Makefile                       # tailwind build/watch/install targets
├── Dockerfile
└── docker-compose.yml              # local Django + Postgres
```

## App internal layout (each app under `apps/`)

```
apps/<app_name>/
├── migrations/
├── templates/<app_name>/          # e.g. apps/accounts/templates/accounts/
├── tests/                          # test_forms.py, test_views.py, test_validators.py
├── admin.py
├── apps.py
├── forms.py
├── models.py
├── urls.py
└── views.py
```

Not every app has every file yet (e.g. `events`, `items`, `moderation` don't have `views.py`/`urls.py`/`forms.py` yet — being built incrementally per `.kiro/specs/` phases).

## Naming conventions

| Element | Convention | Example |
|---|---|---|
| Variables, functions | `snake_case` | `close_expired_events` |
| Classes, Models, Forms | `PascalCase` | `EventItem`, `RegisterUserForm` |
| Constants | `UPPER_SNAKE_CASE` | `INTERNAL_CRON_TOKEN` |
| Django apps | plural lowercase noun | `events`, `items`, `accounts` |
| Models | singular `PascalCase` | `Event`, `ItemAssignment` |
| Function-based views | `snake_case` + `_view` | `event_detail_view` |
| Class-based views | `PascalCase` + `View` | `EventDetailView` |
| URL paths | `kebab-case` | `/events/<uuid:pk>/close/` |
| URL names | `snake_case` with app prefix | `events:detail` |
| Templates | `kebab-case` | `event-detail.html` |
| HTMX partials | `_`-prefixed | `_event_card.html` |
| Django template blocks | `snake_case` | `{% block page_content %}` |
| HTML ids | `kebab-case` | `id="close-modal"` |

## Database conventions

- Tables: `snake_case` plural (`event_items`, `item_assignments`).
- Columns: `snake_case` (`owner_user_id`, `created_at`).
- Primary keys: always `uuid`, never autoincrement.
- Foreign keys: `{referenced_entity}_id`.
- Every table has `created_at` + `updated_at` (`timestamptz`).
- No hard deletes — use terminal states + timestamps (`cancelled_at`, `removed_at`).
- Enums: lowercase `snake_case` (`event_status`, `access_status`).

## Frontend conventions

- Tailwind utility classes directly in HTML; avoid `@apply` unless justified.
- Mobile-first: base classes for mobile, `md:`/`lg:` prefixes for larger breakpoints (primary use case is on phones).
- No dark mode (out of MVP scope).
- No component CSS files — use template partials instead.
- HTMX: partial views return only the needed fragment, not the full page. Use `hx-target` with an explicit ID. Use `hx-confirm` or custom modals, never `window.confirm()`. Use `HX-Redirect` header for post-action redirects.

## Import order (Python)

stdlib → third-party → Django → local apps, each group separated by a blank line (enforced by `ruff` isort rules, first-party = `apps`, `config`).

## Specs

Feature/phase work is tracked under `.kiro/specs/<phase-name>/` with `requirements.md`, `design.md`, and `tasks.md`. Check there before starting new work — it's the authoritative plan for what's being built and in what order.
