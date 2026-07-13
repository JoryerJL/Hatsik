# Phase 6 — Assignments: Technical Design

## Architecture Decisions

### AD-1: No New Django App

The `ItemAssignment` model already exists in `apps.items.models`. Assignment logic will be implemented as:
- **Service layer**: `apps/items/services.py` (extend existing file with assignment functions)
- **Views**: `apps/items/views.py` (add assignment views alongside existing item views)
- **URLs**: `apps/items/urls.py` (add assignment URL patterns)
- **Templates**: `apps/items/templates/items/partials/` (assignment UI fragments)

**Rationale**: Assignments are tightly coupled to items (same model module, same queryset, same status computation). Splitting into a separate app would create unnecessary cross-app imports and break cohesion.

### AD-2: HTMX Partial Refresh Pattern

All assignment actions (claim, modify, cancel, mark purchased) will use HTMX to:
1. Submit the form via `hx-post`
2. Return the updated `_item_row.html` partial (with assignments expanded)
3. Swap the specific item row in-place (`hx-target="#item-row-{pk}"`, `hx-swap="outerHTML"`)

This keeps the interaction fast without full page reloads and follows the pattern already established in Phase 5.

**Progress bar update**: After any assignment action, the response includes an `HX-Trigger: progress-updated` header. The progress bar section listens via `hx-trigger="progress-updated from:body"` and refreshes from a dedicated partial endpoint.

### AD-3: Inline Assignment UI (No Modal)

Unlike item add/edit which uses modals, assignments will render **inline within the item row**:
- Claim form appears below the item name when the user clicks "Asignarme"
- Active assignments are listed as compact rows beneath each item
- This provides better context (user sees the item + other assignments while claiming)

**Expanded item row structure**:
```
┌─────────────────────────────────────────────┐
│ Item Name (3 kg)          [Status Badge]     │
│                                              │
│ Assignments:                                 │
│   ├─ Juan (1.5 kg) [✓Comprado]             │
│   └─ María (0.5 kg) [Editar] [Cancelar]    │
│                                              │
│ [Asignarme] (input: 1 kg)  Available: 1 kg  │
│                                              │
│ [Owner: edit/delete buttons]                 │
│━━━━━━━━━━━━━ Status color bar ━━━━━━━━━━━━━│
└─────────────────────────────────────────────┘
```

### AD-4: Service Layer Function Signatures

New functions in `apps/items/services.py`:

```python
def claim_item(item, user, *, quantity_assigned=None) -> ItemAssignment
def modify_assignment(assignment, user, *, quantity_assigned) -> ItemAssignment
def cancel_assignment(assignment, user) -> ItemAssignment
def mark_as_purchased(assignment, user) -> ItemAssignment
def cancel_others_assignment(assignment, owner_user) -> ItemAssignment
def get_available_quantity(item) -> Decimal | None
def compute_event_progress(event) -> dict  # {"percentage": int, "covered": int, "total": int}
```

Each function:
- Validates event status rules (active/closed/cancelled matrix)
- Validates role permissions
- Raises `ItemError` with Spanish user-facing messages on failure
- Returns the modified object on success

### AD-5: Event Status Guards

Centralize the event-status check as a reusable helper:

```python
def _check_event_allows_action(event, action: str) -> None:
    """Raise ItemError if event status blocks the action.
    
    Actions: "claim", "modify", "cancel", "purchase"
    """
```

This maps to the matrix from requirements:

| Event Status | claim | modify | cancel | purchase |
|---|---|---|---|---|
| active | ✅ | ✅ | ✅ | ✅ |
| closed | ❌ | ❌ | ❌ | ✅ |
| cancelled | ❌ | ❌ | ❌ | ❌ |

### AD-6: Progress Bar Computation

The progress bar uses a single efficient query:

```python
def compute_event_progress(event) -> dict:
    """Compute percentage of items fully covered or purchased."""
    items = event.items.all()
    total = items.count()
    if total == 0:
        return {"percentage": 0, "covered": 0, "total": 0}
    
    # Count items where status >= "covered" (cubierto, parcialmente_comprado, comprado)
    covered = ...  # annotated query
    return {"percentage": int(covered / total * 100), "covered": covered, "total": total}
```

Progress is rendered via a dedicated partial `_progress_bar.html` that the event detail view includes. It refreshes via `HX-Trigger` after any assignment change.

### AD-7: Confirmation Dialogs via `hx-confirm`

Following the pattern already established:
- **Cancel assignment**: `hx-confirm="¿Seguro que querés cancelar tu asignación?"`
- **Mark purchased**: `hx-confirm="¿Marcar como comprado? Esta acción no se puede deshacer."`
- **Owner cancel others**: `hx-confirm="¿Cancelar la asignación de {name}?"`
- **Claim & Modify**: No confirmation needed

### AD-8: Permission Model in Views

```python
# Who can do what:
# - claim_item: any accepted participant (event must be active)
# - modify_assignment: assignment.user == request.user
# - cancel_assignment: assignment.user == request.user OR event.owner_user == request.user
# - mark_purchased: assignment.user == request.user OR is_admin (owner/co-admin)
```

We'll create a new decorator `@accepted_participant_required` that:
1. Ensures user is authenticated
2. Ensures user has an accepted participation in the event
3. Passes `event` and `participation` to the view

### AD-9: Highlighted Uncovered Items at Closure

When `event.status == "closed"`, the `_item_row.html` template adds a CSS class:
```html
{% if event.status == "closed" and current_status in "sin_asignar,parcialmente_cubierto" %}
<div class="... ring-2 ring-[#FCA5A5] bg-red-50/30">
{% endif %}
```

No backend logic needed — purely a template conditional using existing status computation.

---

## File Changes Summary

| File | Action | Purpose |
|------|--------|---------|
| `apps/items/services.py` | Extend | Add assignment service functions + progress computation |
| `apps/items/views.py` | Extend | Add claim, modify, cancel, purchase views |
| `apps/items/urls.py` | Extend | Add assignment URL patterns |
| `apps/items/forms.py` | Extend | Add `ClaimItemForm` |
| `apps/items/templatetags/items_tags.py` | Extend | Add `available_quantity` tag |
| `apps/items/templates/items/partials/_item_row.html` | Rewrite | Include assignment list + claim form |
| `apps/items/templates/items/partials/_assignment_row.html` | Create | Single assignment display with actions |
| `apps/items/templates/items/partials/_progress_bar.html` | Create | Progress bar partial for HX-Trigger refresh |
| `apps/items/templates/items/claim-item.html` | Create | Claim form fragment (HTMX target) |
| `apps/items/templates/items/edit-assignment.html` | Create | Modify assignment form fragment |
| `apps/events/templates/events/event-detail.html` | Modify | Wire progress bar partial, pass assignments to item rows |
| `apps/events/views.py` | Modify | Pass assignments data to event detail context |
| `apps/events/decorators.py` | Extend | Add `accepted_participant_required` decorator |
| `apps/items/tests/` | Create | Test files for assignment service + views |

---

## URL Structure

```python
# apps/items/urls.py additions
urlpatterns += [
    # Assignment actions
    path("<uuid:pk>/items/<uuid:item_pk>/claim/", views.claim_item_view, name="claim"),
    path("<uuid:pk>/assignments/<uuid:assignment_pk>/edit/", views.edit_assignment_view, name="edit_assignment"),
    path("<uuid:pk>/assignments/<uuid:assignment_pk>/cancel/", views.cancel_assignment_view, name="cancel_assignment"),
    path("<uuid:pk>/assignments/<uuid:assignment_pk>/purchase/", views.purchase_assignment_view, name="purchase_assignment"),
    # Progress bar partial
    path("<uuid:pk>/progress/", views.progress_bar_view, name="progress"),
]
```

---

## Testing Strategy

- **Unit tests**: Service layer functions with all permutations of event status × role × action
- **Integration tests**: View tests with HTMX headers verifying correct responses
- **Edge cases**: Concurrent claims exceeding quantity (race condition via F() expressions or select_for_update)
- **Template tests**: Verify correct buttons visible per role/status combination

---

## Concurrency Consideration

For the quantity check (sum of assignments ≤ quantity_total), use `select_for_update()` on the item row before creating/modifying assignments to prevent race conditions where two participants claim the last available quantity simultaneously.

```python
with transaction.atomic():
    item = EventItem.objects.select_for_update().get(pk=item.pk)
    available = get_available_quantity(item)
    if quantity_assigned > available:
        raise ItemError(...)
    # Create assignment
```
