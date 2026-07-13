# Phase 5 — Items & Moderation: Implementation Tasks

## Task Groups

### Group 1: Items Service Layer & Tests

- [ ] **Task 1.1:** Create `apps/items/services.py` with `add_item()`, `edit_item()`, `delete_item()` functions. Include validation: event must be active, user must be owner, quantity_total cannot go below active assignment sum.
- [ ] **Task 1.2:** Implement `compute_item_status(item)` in `apps/items/services.py`. Pure function that computes status from assignments (sin_asignar, parcialmente_cubierto, cubierto, parcialmente_comprado, comprado).
- [ ] **Task 1.3:** Implement `get_items_with_status(event)` in `apps/items/services.py`. Uses Django ORM annotations (Sum, Count with filters) to compute status at query time without N+1.
- [ ] **Task 1.4:** Write unit tests in `apps/items/tests/test_services.py`:
  - add_item happy path
  - add_item blocked on closed/cancelled event
  - add_item blocked for non-owner
  - edit_item with no assignments (all fields editable)
  - edit_item with assignments (only quantity_total, must not go below active sum)
  - delete_item happy path (cascades assignments)
  - delete_item blocked on closed/cancelled event
  - compute_item_status for all 5 states + binary items
  - get_items_with_status annotation correctness

### Group 2: Items Forms

- [ ] **Task 2.1:** Create `apps/items/forms.py` with `AddItemForm` (name, quantity_total, unit). Validate: unit required if quantity_total is set; quantity_total must be > 0 if provided. Unit choices from `ItemUnit`.
- [ ] **Task 2.2:** Create `EditItemForm` in `apps/items/forms.py`. Accepts `has_assignments` flag in `__init__` — if True, name and unit fields are disabled/read-only.
- [ ] **Task 2.3:** Write form tests in `apps/items/tests/test_forms.py`:
  - Valid add form (with quantity + unit)
  - Valid add form (binary, no quantity/unit)
  - Invalid: quantity without unit
  - Invalid: unit without quantity
  - Invalid: quantity_total <= 0
  - EditItemForm respects has_assignments flag

### Group 3: Items Views & URLs

- [ ] **Task 3.1:** Create `apps/items/views.py` with `add_item_view` (GET: render form, POST: call service, redirect to event detail). Use `event_owner_required` decorator.
- [ ] **Task 3.2:** Add `edit_item_view` to `apps/items/views.py`. GET: pre-fill form, detect has_assignments. POST: call service with validation. Redirect on success.
- [ ] **Task 3.3:** Add `delete_item_view` to `apps/items/views.py`. POST-only. Use `hx-post` with HTMX — return empty response with `HX-Trigger` for list refresh, or return `_request_row_empty.html` pattern. Use `event_owner_required`.
- [ ] **Task 3.4:** Create `apps/items/urls.py` with namespace `items` and the 3 URL patterns (add, edit, delete). Register in `config/urls.py`.
- [ ] **Task 3.5:** Write view integration tests in `apps/items/tests/test_views.py`:
  - add_item GET renders form (owner only, 403 for others)
  - add_item POST creates item and redirects
  - add_item POST blocked on inactive event
  - edit_item GET pre-fills, shows warning if has_assignments
  - edit_item POST updates and redirects
  - delete_item POST deletes and returns HTMX response
  - delete_item blocked on inactive event

### Group 4: Items Templates (Stitch Fidelity)

- [ ] **Task 4.1:** Download Stitch HTML for Añadir Ítem (`f4ee82a1da0542898d47b5e0eaabe809`) and Editar Ítem (`4264f659cdcc4d2c931e77a63c27063a`). Save to `docs/stitch-html/`.
- [ ] **Task 4.2:** Create `apps/items/templates/items/add-item.html` matching Stitch design. Extends `base.html`. Form with name, quantity, unit (select). Spanish labels.
- [ ] **Task 4.3:** Create `apps/items/templates/items/edit-item.html` matching Stitch design. Include warning banner when item has assignments. Disabled fields when appropriate. Spanish labels.
- [ ] **Task 4.4:** Create `apps/items/templates/items/partials/_item_row.html` — single item card showing name, quantity, unit, status badge with semaphore color. Include edit/delete actions for owner.
- [ ] **Task 4.5:** Create `apps/items/templates/items/partials/_item_list.html` — full items section. Includes grid of `_item_row.html` partials, "Añadir ítem" button (owner only), empty state.

### Group 5: Moderation Service Layer & Tests

- [ ] **Task 5.1:** Create `apps/moderation/services.py` with `suggest_item()`, `edit_suggestion()`, `delete_suggestion()`. Validate: event active, user is accepted participant, only own pending suggestions editable/deletable.
- [ ] **Task 5.2:** Add `approve_suggestion()` to `apps/moderation/services.py`. Creates an official `EventItem` from the suggestion (with optional overrides). Sets suggestion status to `approved`, links `converted_event_item`.
- [ ] **Task 5.3:** Add `reject_suggestion()` to `apps/moderation/services.py`. Sets status to `rejected`, stores rejection_note, records reviewed_by and reviewed_at.
- [ ] **Task 5.4:** Write unit tests in `apps/moderation/tests/test_services.py`:
  - suggest_item happy path
  - suggest_item blocked on closed/cancelled event
  - suggest_item blocked for non-participant
  - edit_suggestion own pending only
  - delete_suggestion own pending only
  - approve_suggestion creates item, sets status
  - approve_suggestion with overridden name/quantity/unit
  - reject_suggestion sets note and status
  - reject_suggestion already approved/rejected raises error

### Group 6: Moderation Forms

- [ ] **Task 6.1:** Create `apps/moderation/forms.py` with `SuggestItemForm` (name, quantity_total, unit). Same validation logic as AddItemForm.
- [ ] **Task 6.2:** Add `EditSuggestionForm` and `ApproveSuggestionForm` to `apps/moderation/forms.py`. ApproveSuggestionForm pre-fills from suggestion data.
- [ ] **Task 6.3:** Write form tests in `apps/moderation/tests/test_forms.py`:
  - Valid suggestion form
  - Invalid: quantity without unit
  - ApproveSuggestionForm pre-fill works
  - EditSuggestionForm validates same rules

### Group 7: Moderation Views & URLs

- [ ] **Task 7.1:** Create `apps/moderation/views.py` with `suggest_item_view` (GET/POST). Use `participant_required` decorator. Redirect to event detail on success.
- [ ] **Task 7.2:** Add `edit_suggestion_view` and `delete_suggestion_view` to `apps/moderation/views.py`. Edit: GET/POST with `participant_required`. Delete: POST-only with HTMX response.
- [ ] **Task 7.3:** Add `approve_suggestion_view` to `apps/moderation/views.py`. GET: pre-fill form from suggestion. POST: call service. Use `event_admin_required`.
- [ ] **Task 7.4:** Add `reject_suggestion_view` to `apps/moderation/views.py`. POST-only with HTMX response. Use `event_admin_required`. Include rejection_note from form/request.
- [ ] **Task 7.5:** Create `apps/moderation/urls.py` with namespace `moderation` and all 5 URL patterns. Register in `config/urls.py`.
- [ ] **Task 7.6:** Write view integration tests in `apps/moderation/tests/test_views.py`:
  - suggest GET/POST (participant only, 403 for owner acting as participant)
  - edit_suggestion (own pending only)
  - delete_suggestion (own pending only, HTMX response)
  - approve_suggestion (admin only, creates item)
  - reject_suggestion (admin only, sets note)

### Group 8: Moderation Templates (Stitch Fidelity)

- [ ] **Task 8.1:** Download Stitch HTML for Sugerir Ítem (`0c8fa38e491e43c2a5da6a3d984f702e`). Save to `docs/stitch-html/`.
- [ ] **Task 8.2:** Create `apps/moderation/templates/moderation/suggest-item.html` matching Stitch design. Form with name, quantity, unit. Spanish labels.
- [ ] **Task 8.3:** Create `apps/moderation/templates/moderation/edit-suggestion.html`. Same layout as suggest-item, pre-filled.
- [ ] **Task 8.4:** Create `apps/moderation/templates/moderation/approve-suggestion.html`. Form pre-filled from suggestion with all fields editable. Spanish labels.
- [ ] **Task 8.5:** Create `apps/moderation/templates/moderation/partials/_suggestion_row.html` — card for participant's "My Suggestions" view (shows status badge, edit/delete actions for pending).
- [ ] **Task 8.6:** Create `apps/moderation/templates/moderation/partials/_pending_suggestions.html` — admin view: list of pending suggestions with approve/reject actions.

### Group 9: Event Detail Integration

- [ ] **Task 9.1:** Update `apps/events/views.py` `event_detail_view` to pass items (with computed status) and pending suggestions to the template context.
- [ ] **Task 9.2:** Replace the Phase 5 placeholder in `event-detail.html` with `{% include "items/partials/_item_list.html" %}`.
- [ ] **Task 9.3:** Add "Mis sugerencias" section to `event-detail.html` (visible to participants, shows their own suggestions with status).
- [ ] **Task 9.4:** Add "Sugerencias pendientes" section to `event-detail.html` (visible to Owner/Co-admin only). Include with `{% include "moderation/partials/_pending_suggestions.html" %}`.
- [ ] **Task 9.5:** Wire up the "Añadir ítem" button (owner) and "Sugerir ítem" button (participant) links in the event detail.

### Group 10: Final Verification

- [ ] **Task 10.1:** Run full test suite (`python manage.py test`) — all tests pass.
- [ ] **Task 10.2:** Manual smoke test: Owner adds item, edits (with/without assignments), deletes. Status badges correct.
- [ ] **Task 10.3:** Manual smoke test: Participant suggests, edits suggestion, deletes suggestion. Owner approves/rejects.
- [ ] **Task 10.4:** Verify access control: non-owner cannot add/edit/delete items. Non-admin cannot approve/reject.
- [ ] **Task 10.5:** Verify event status blocking: no item/suggestion operations on closed/cancelled events.

---

## Commit Strategy (Work Units)

| Commit | Scope | Tasks |
|---|---|---|
| `feat(items): add item service layer with business rules` | Services + tests | 1.1–1.4 |
| `feat(items): add forms with unit validation` | Forms + tests | 2.1–2.3 |
| `feat(items): add views, URLs, and integration tests` | Views + URLs + tests | 3.1–3.5 |
| `feat(items): add templates matching Stitch design` | Templates | 4.1–4.5 |
| `feat(moderation): add suggestion service layer` | Services + tests | 5.1–5.4 |
| `feat(moderation): add forms with validation` | Forms + tests | 6.1–6.3 |
| `feat(moderation): add views, URLs, and integration tests` | Views + URLs + tests | 7.1–7.6 |
| `feat(moderation): add templates matching Stitch design` | Templates | 8.1–8.6 |
| `feat(events): integrate items and suggestions in event detail` | Integration | 9.1–9.5 |
| `test(phase-5): verify all done criteria pass` | Verification | 10.1–10.5 |

---

## Dependencies Between Groups

```
Group 1 (Items Services) ──→ Group 2 (Items Forms) ──→ Group 3 (Items Views)
                                                              ↓
Group 5 (Moderation Services) → Group 6 (Forms) → Group 7 (Views) → Group 9 (Integration)
                                                              ↑
                                              Group 4 (Items Templates)
                                              Group 8 (Moderation Templates)
```

Groups 1 and 5 can be developed in parallel.
Groups 4 and 8 (templates) depend on views being defined but can be stubbed.
Group 9 (integration) requires all other groups complete.
Group 10 (verification) runs last.
