# Design — Phase 3: Events & Dashboard

## Technical Approach

### Architecture Pattern

Same monolith pattern as Phase 2: Django function-based views + Django templates + HTMX for partial updates. No REST API, no SPA.

### URL Structure

```
/events/                              → Dashboard (list events)
/events/create/                       → Create event form
/events/<uuid:pk>/                    → Event detail (accepted participants only)
/events/<uuid:pk>/edit/               → Edit event (Owner only, HTMX partial)
/events/<uuid:pk>/close/              → Close event (Owner only, POST)
/events/<uuid:pk>/reopen/             → Reopen event (Owner only, POST)
/events/<uuid:pk>/cancel/             → Cancel event (Owner only, POST)
/events/<uuid:pk>/share/              → Share/invite screen (Owner + Co-admin)
/events/<uuid:pk>/share/qr/           → QR download endpoint (PNG)
/events/<uuid:pk>/participants/<uuid:participation_id>/remove/   → Remove participant (POST)
/events/<uuid:pk>/participants/<uuid:participation_id>/promote/  → Assign co-admin (POST)
/events/<uuid:pk>/participants/<uuid:participation_id>/demote/   → Revoke co-admin (POST)
/events/join/<uuid:token>/            → Public event card (via share link)
/internal/close-expired-events/       → Cron endpoint (already in internal app)
```

### URL Names (namespaced: `events:`)

```python
app_name = "events"

# Dashboard
"events:dashboard"            → /events/
"events:create"               → /events/create/
"events:detail"               → /events/<pk>/
"events:edit"                 → /events/<pk>/edit/

# Lifecycle
"events:close"                → /events/<pk>/close/
"events:reopen"               → /events/<pk>/reopen/
"events:cancel"               → /events/<pk>/cancel/

# Share
"events:share"                → /events/<pk>/share/
"events:share_qr"             → /events/<pk>/share/qr/

# Participants
"events:remove_participant"   → /events/<pk>/participants/<participation_id>/remove/
"events:promote_participant"  → /events/<pk>/participants/<participation_id>/promote/
"events:demote_participant"   → /events/<pk>/participants/<participation_id>/demote/

# Public
"events:public_card"          → /events/join/<token>/
```

---

## File Structure

```
apps/events/
├── forms.py              ← CreateEventForm, EditEventForm
├── views.py              ← All function-based views
├── urls.py               ← URL patterns with namespace
├── decorators.py         ← Permission decorators (event_owner_required, participant_required)
├── services.py           ← Business logic (create_event, close_event, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_views.py     ← View tests (happy path + permissions)
│   ├── test_forms.py     ← Form validation tests
│   └── test_services.py  ← Business logic tests
└── templates/
    └── events/
        ├── dashboard.html         ← Mis Eventos main page
        ├── create-event.html      ← Event creation form
        ├── event-detail.html      ← Full event detail
        ├── event-card-public.html ← Public-facing event info
        ├── share-event.html       ← Share link + QR
        ├── _event_card.html       ← Dashboard card partial (HTMX)
        ├── _participant_row.html  ← Single participant row (HTMX)
        ├── _edit_form.html        ← Edit form partial (HTMX)
        └── _confirm_modal.html    ← Confirmation dialog partial
```

---

## Views Design

### Pattern: Function-Based Views with Decorators

```python
@login_required
@require_http_methods(["GET", "POST"])
def create_event_view(request):
    ...

@login_required
@participant_required(min_role="accepted")
def event_detail_view(request, pk):
    ...

@login_required
@event_owner_required
@require_POST
def close_event_view(request, pk):
    ...
```

### Custom Decorators

- `@event_owner_required`: Verifies user is the Owner of the event referenced by `pk`
- `@participant_required(min_role=...)`: Verifies user has an accepted participation
- Both decorators inject the `event` object into kwargs to avoid re-querying

### HTMX Interactions

| Action | Trigger | Response |
|--------|---------|----------|
| Edit event | Click "Editar" button | Swap form into detail header (hx-target) |
| Save edit | Submit edit form | HX-Redirect to detail or swap updated header |
| Close/Reopen/Cancel | Click button after confirm | HX-Redirect to detail (status badge updates) |
| Remove participant | Click "Eliminar" after confirm | Remove row from DOM (hx-swap="outerHTML") |
| Promote/Demote | Click button | Swap participant row with updated role badge |
| Copy link | Click "Copiar" button | Client-side clipboard API + toast |

---

## Services Layer

Business logic lives in `apps/events/services.py`, not in views. Views handle HTTP concerns; services handle domain logic.

```python
def create_event(user, *, name, event_date, description=None, assignment_deadline_at=None) -> Event:
    """Create event + Owner participation in a transaction."""

def close_event(event) -> None:
    """Close an active event. Raises if already cancelled."""

def reopen_event(event) -> None:
    """Reopen a closed event. Raises if cancelled."""

def cancel_event(event) -> None:
    """Cancel an event. Raises if already cancelled."""

def promote_to_co_admin(participation) -> None:
    """Promote participant to co-admin."""

def demote_co_admin(participation) -> None:
    """Demote co-admin to participant."""

def remove_participant(participation) -> None:
    """Remove participant. Raises if has purchased assignments."""

def close_expired_events() -> int:
    """Close all active events past their deadline. Returns count."""
```

---

## QR Generation

Using `qrcode` library (already in requirements):

```python
import io
import qrcode
from django.http import HttpResponse

def share_qr_view(request, pk):
    event = get_object_or_404(Event, pk=pk)
    url = request.build_absolute_uri(
        reverse("events:public_card", kwargs={"token": event.public_share_token})
    )
    img = qrcode.make(url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer, content_type="image/png",
                        headers={"Content-Disposition": f"attachment; filename=hatsik-event-{event.pk}.png"})
```

---

## Template Inheritance

```
base.html                    ← Has nav header, main layout
├── events/dashboard.html    ← {% block content %}
├── events/create-event.html
├── events/event-detail.html
├── events/share-event.html
└── events/event-card-public.html
```

The Event Detail page uses the app nav header (base.html). The public card (Ficha del Evento) also uses base.html but shows different nav actions depending on auth state.

---

## Permission Model

| Action | Who can do it | Check location |
|--------|---------------|----------------|
| View dashboard | Any verified user | `@login_required` |
| Create event | Any verified user | `@login_required` |
| View event detail | Accepted participants | `@participant_required` |
| Edit event | Owner only | `@event_owner_required` |
| Close/Reopen/Cancel | Owner only | `@event_owner_required` |
| Share/Invite | Owner + Co-admin | Custom check in view |
| Promote/Demote/Remove | Owner only | `@event_owner_required` |
| View public card | Any authenticated user | `@login_required` |
| Automatic closure | Internal endpoint | Token check in `internal` app |

---

## Internal Endpoint (Auto-close)

The `/internal/close-expired-events/` endpoint already exists in `apps/internal/`. The service function `close_expired_events()` will be defined in `apps/events/services.py` and called from the existing internal view.

---

## Dependencies & Packages

No new dependencies required. All needed packages are already installed:
- `django` (views, forms, ORM)
- `qrcode` (QR generation)
- `django-htmx` (HTMX detection)

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Services layer separate from views | Testable business logic; views stay thin |
| Custom decorators for permissions | DRY; consistent pattern across all event views |
| HTMX for edit/lifecycle actions | No full page reloads for management actions |
| QR generated on-demand, not stored | Simpler; URL changes automatically reflected |
| Public card accessible to authenticated users only | Aligns with "no anonymous access" rule from Phase 2 |
| Confirmation modals via `_confirm_modal.html` | Reusable; consistent UX for destructive actions |
| Participant removal blocked at service level | Central enforcement, not just UI |
