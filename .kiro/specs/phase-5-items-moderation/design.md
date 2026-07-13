# Phase 5 — Items & Moderation: Technical Design

## Architecture Overview

Phase 5 introduces two Django apps (`items`, `moderation`) with views, services, forms, templates, and URL patterns. Both apps already have their models and migrations from Phase 1. This phase adds the business logic layer and UI.

The item list integrates into the existing `event-detail.html` template (replacing the Phase 5 placeholder section). The add/edit/suggest forms are standalone pages following the same Stitch design patterns used in Phases 2–4.

---

## Module Boundaries

```
apps/items/          → Item CRUD (Owner only) + computed status logic
apps/moderation/     → Suggestion lifecycle (Participant suggests, Owner/Co-admin moderates)
apps/events/         → event-detail.html updated to include item list + suggestions section
```

### Cross-module dependencies

- `items.services` reads `items.models.ItemAssignment` for status computation.
- `moderation.services` creates `items.models.EventItem` when approving a suggestion.
- `events/templates/events/event-detail.html` includes `items` and `moderation` partials.

---

## Service Layer Design

### `apps/items/services.py`

| Function | Description | Access |
|---|---|---|
| `add_item(event, user, *, name, quantity_total, unit)` | Create EventItem. Validates event is active + user is owner. | Owner |
| `edit_item(item, user, *, name, quantity_total, unit)` | Edit item. If has assignments, only quantity_total editable. Validates min threshold. | Owner |
| `delete_item(item, user)` | Delete item + cascade assignments. Validates event active. | Owner |
| `compute_item_status(item)` | Returns computed status string based on assignments. Pure function, no DB write. | Any |
| `get_items_with_status(event)` | Queryset annotated with computed status for display. | Any accepted participant |

### `apps/moderation/services.py`

| Function | Description | Access |
|---|---|---|
| `suggest_item(event, user, *, name, quantity_total, unit)` | Create ItemSuggestion with `pending_approval` status. | Accepted participant |
| `edit_suggestion(suggestion, user, *, name, quantity_total, unit)` | Edit own pending suggestion. | Suggester only |
| `delete_suggestion(suggestion, user)` | Delete own pending suggestion. | Suggester only |
| `approve_suggestion(suggestion, user, *, name, quantity_total, unit)` | Approve + create official item. Optionally override name/quantity/unit. | Owner / Co-admin |
| `reject_suggestion(suggestion, user, *, rejection_note)` | Reject with optional note. | Owner / Co-admin |

---

## Item Status Computation Strategy

Status is NEVER stored. It's computed at query time using Django ORM annotations:

```python
from django.db.models import Sum, Q, Case, When, Value, CharField

def get_items_with_status(event):
    """Return items annotated with computed_status."""
    return event.items.annotate(
        active_assigned=Sum(
            "assignments__quantity_assigned",
            filter=Q(assignments__cancelled_at__isnull=True),
            default=0,
        ),
        total_assignments=Count(
            "assignments",
            filter=Q(assignments__cancelled_at__isnull=True),
        ),
        purchased_count=Count(
            "assignments",
            filter=Q(
                assignments__cancelled_at__isnull=True,
                assignments__purchased_at__isnull=False,
            ),
        ),
    )
```

The template renders the status badge based on these annotations using template logic or a template tag.

---

## Forms

### `apps/items/forms.py`

| Form | Fields | Notes |
|---|---|---|
| `AddItemForm` | name, quantity_total, unit | Unit choices from `ItemUnit`. Unit required only if quantity is set. |
| `EditItemForm` | name, quantity_total, unit | Dynamically restricts fields if item has assignments (JS + server validation). |

### `apps/moderation/forms.py`

| Form | Fields | Notes |
|---|---|---|
| `SuggestItemForm` | name, quantity_total, unit | Same validation as AddItemForm. |
| `EditSuggestionForm` | name, quantity_total, unit | Only for pending suggestions. |
| `ApproveSuggestionForm` | name, quantity_total, unit | Pre-filled from suggestion. All fields editable. |

---

## URL Design

### Items (`apps/items/urls.py`)

```python
# Namespace: items
urlpatterns = [
    path("<uuid:event_pk>/items/add/", add_item_view, name="add"),
    path("<uuid:event_pk>/items/<uuid:item_pk>/edit/", edit_item_view, name="edit"),
    path("<uuid:event_pk>/items/<uuid:item_pk>/delete/", delete_item_view, name="delete"),
]
```

### Moderation (`apps/moderation/urls.py`)

```python
# Namespace: moderation
urlpatterns = [
    path("<uuid:event_pk>/suggestions/add/", suggest_item_view, name="suggest"),
    path("<uuid:event_pk>/suggestions/<uuid:suggestion_pk>/edit/", edit_suggestion_view, name="edit"),
    path("<uuid:event_pk>/suggestions/<uuid:suggestion_pk>/delete/", delete_suggestion_view, name="delete"),
    path("<uuid:event_pk>/suggestions/<uuid:suggestion_pk>/approve/", approve_suggestion_view, name="approve"),
    path("<uuid:event_pk>/suggestions/<uuid:suggestion_pk>/reject/", reject_suggestion_view, name="reject"),
]
```

---

## Template Structure

### New templates

| File | Purpose |
|---|---|
| `apps/items/templates/items/add-item.html` | Full-page form for adding an item |
| `apps/items/templates/items/edit-item.html` | Full-page form for editing an item |
| `apps/items/templates/items/partials/_item_row.html` | Single item card (used in list) |
| `apps/items/templates/items/partials/_item_list.html` | Complete items section (HTMX target) |
| `apps/moderation/templates/moderation/suggest-item.html` | Full-page form for suggesting |
| `apps/moderation/templates/moderation/edit-suggestion.html` | Full-page form for editing suggestion |
| `apps/moderation/templates/moderation/partials/_suggestion_row.html` | Suggestion card for participant view |
| `apps/moderation/templates/moderation/partials/_pending_suggestions.html` | Admin view of pending suggestions |
| `apps/moderation/templates/moderation/approve-suggestion.html` | Full-page form for approve (with editable fields) |

### Modified templates

| File | Change |
|---|---|
| `apps/events/templates/events/event-detail.html` | Replace placeholder with `{% include "items/partials/_item_list.html" %}` and `{% include "moderation/partials/_pending_suggestions.html" %}` |

---

## HTMX Integration

| Action | Method | Target | Swap |
|---|---|---|---|
| Delete item | `hx-post` + `hx-confirm` | `#item-{pk}` | `outerHTML` (replace with empty) |
| Delete suggestion | `hx-post` + `hx-confirm` | `#suggestion-{pk}` | `outerHTML` (replace with empty) |
| Approve suggestion | Full page (form with editable fields) | — | Redirect back to event detail |
| Reject suggestion | `hx-post` + `hx-confirm` | `#suggestion-{pk}` | `outerHTML` |

Add/Edit/Suggest use full-page forms (not inline HTMX) to match Stitch screen designs.

---

## Access Control Matrix

| Action | Owner | Co-admin | Participant |
|---|---|---|---|
| Add item | ✅ | ❌ | ❌ |
| Edit item | ✅ | ❌ | ❌ |
| Delete item | ✅ | ❌ | ❌ |
| View item list | ✅ | ✅ | ✅ |
| Suggest item | ❌ | ❌ | ✅ |
| Edit own suggestion | — | — | ✅ (pending only) |
| Delete own suggestion | — | — | ✅ (pending only) |
| Approve suggestion | ✅ | ✅ | ❌ |
| Reject suggestion | ✅ | ✅ | ❌ |

Access control enforced via decorators from `apps/events/decorators.py`:
- `event_owner_required` → add/edit/delete item
- `event_admin_required` → approve/reject suggestion
- `participant_required` → suggest item, edit/delete own suggestion, view list

---

## Stitch Screen Mapping

| Screen | Template | Notes |
|---|---|---|
| Añadir Ítem (`f4ee82a1da0542898d47b5e0eaabe809`) | `items/add-item.html` | Download Stitch HTML and match exactly |
| Editar Ítem (`4264f659cdcc4d2c931e77a63c27063a`) | `items/edit-item.html` | Warning state for items with assignments |
| Sugerir Ítem (`0c8fa38e491e43c2a5da6a3d984f702e`) | `moderation/suggest-item.html` | Same form layout as add-item |
| Detalle del Evento (`32075f1d510242cdb9b880d66edea76c`) | `events/event-detail.html` | Items section replaces placeholder |

---

## Testing Strategy

### Unit tests (services layer)

- `apps/items/tests/test_services.py` — add/edit/delete business rules, status computation, access control violations.
- `apps/moderation/tests/test_services.py` — suggest/edit/delete/approve/reject, rejection notes, cross-module item creation.

### Integration tests (views)

- `apps/items/tests/test_views.py` — HTTP status codes, form validation errors, redirects, HTMX responses.
- `apps/moderation/tests/test_views.py` — Same pattern for moderation views.

### Form tests

- `apps/items/tests/test_forms.py` — Unit validation (quantity required if unit set, etc.)
- `apps/moderation/tests/test_forms.py` — Same for suggestion forms.

---

## Decisions & Rationale

| Decision | Rationale |
|---|---|
| Services layer (not fat views) | Consistent with Phase 3/4 pattern. Testable. |
| Status computed via DB annotations | No redundant state. Single source of truth. N+1 safe. |
| Full-page forms for add/edit/suggest | Stitch designs show standalone form pages, not inline modals. |
| HTMX for delete/reject | Inline actions don't need full page reload. |
| Participant suggests, not Co-admin | ROADMAP explicitly says "Only Owner manages official list". Co-admin can moderate but not add directly. |
| No views.py in items/moderation from Phase 1 | Phase 1 only created models + migrations. Views, forms, services are Phase 5 work. |
