# Phase 6 — Assignments: Implementation Tasks

## Task Ordering

Tasks are ordered by dependency: service layer first (testable in isolation), then views, then templates, then integration.

---

## Tasks

### Task 1: Service Layer — Event Status Guard Helper

**File**: `apps/items/services.py`

Add `_check_event_allows_action(event, action)` helper function that raises `ItemError` when the event status blocks the action. Actions: `"claim"`, `"modify"`, `"cancel"`, `"purchase"`.

**Acceptance**: Unit test covers all 12 combinations (3 statuses × 4 actions).

---

### Task 2: Service Layer — `claim_item`

**File**: `apps/items/services.py`

Implement `claim_item(item, user, *, quantity_assigned=None)`:
- Validates event is `active`
- Validates user has accepted participation
- For quantified items: validates quantity > 0 and sum + new ≤ quantity_total (with `select_for_update`)
- For binary items: `quantity_assigned` must be None
- Creates `ItemAssignment` row
- Returns the created assignment

**Acceptance**: Tests for quantified claim, binary claim, over-limit blocked, inactive event blocked, non-participant blocked, duplicate active assignment blocked (DB constraint).

---

### Task 3: Service Layer — `modify_assignment`

**File**: `apps/items/services.py`

Implement `modify_assignment(assignment, user, *, quantity_assigned)`:
- Validates event is `active`
- Validates `assignment.user == user` (only own)
- Validates assignment is not purchased
- Validates new quantity + others ≤ quantity_total
- Updates `quantity_assigned`
- Returns updated assignment

**Acceptance**: Tests for valid modify, exceed-limit blocked, purchased blocked, other user blocked, closed/cancelled blocked.

---

### Task 4: Service Layer — `cancel_assignment`

**File**: `apps/items/services.py`

Implement `cancel_assignment(assignment, user)`:
- Validates event is `active`
- Validates `assignment.user == user` (own) OR `user == event.owner_user` (owner cancel others)
- Validates assignment is not purchased
- Sets `cancelled_at = now()`, `cancelled_by_user = user`
- Returns updated assignment

**Acceptance**: Tests for self-cancel, owner-cancel-others, co-admin-cannot-cancel-others, purchased blocked, closed/cancelled blocked.

---

### Task 5: Service Layer — `mark_as_purchased`

**File**: `apps/items/services.py`

Implement `mark_as_purchased(assignment, user)`:
- Validates event is NOT `cancelled` (allowed in active AND closed)
- Validates user is assignment owner OR event admin (owner/co-admin)
- Validates assignment is not already purchased
- Sets `purchased_at = now()`, `purchased_by_user = user`
- Returns updated assignment

**Acceptance**: Tests for self-purchase, admin-purchase-others, cancelled event blocked, already purchased blocked, regular participant cannot purchase others.

---

### Task 6: Service Layer — `get_available_quantity` and `compute_event_progress`

**File**: `apps/items/services.py`

Implement:
1. `get_available_quantity(item) -> Decimal | None`: Returns remaining quantity (or None for binary items)
2. `compute_event_progress(event) -> dict`: Returns `{"percentage": int, "covered": int, "total": int}` where "covered" = items with status ≥ cubierto

**Acceptance**: Tests for various item states, empty events (0%), fully covered (100%), mixed states.

---

### Task 7: Decorator — `accepted_participant_required`

**File**: `apps/events/decorators.py`

Add decorator that:
1. Requires authentication
2. Looks up `EventParticipation` with `access_status=accepted` for the user + event
3. Returns 403 if not found
4. Passes `event` and `participation` to view kwargs

**Acceptance**: Test with accepted participant (passes), pending participant (403), non-participant (403).

---

### Task 8: Forms — `ClaimItemForm`

**File**: `apps/items/forms.py`

Add form with:
- `quantity_assigned` (DecimalField, optional — hidden for binary items)
- Clean method validates > 0 when provided

**Acceptance**: Form validation tests.

---

### Task 9: Views — Assignment CRUD

**File**: `apps/items/views.py`

Add views:
1. `claim_item_view(request, pk, item_pk)` — GET returns claim form fragment, POST creates claim
2. `edit_assignment_view(request, pk, assignment_pk)` — GET returns edit form, POST modifies
3. `cancel_assignment_view(request, pk, assignment_pk)` — POST only, cancels
4. `purchase_assignment_view(request, pk, assignment_pk)` — POST only, marks purchased

All return HTMX partials (updated item row) with `HX-Trigger: progress-updated` header on success.

**Acceptance**: Integration tests with HTMX headers verifying correct response behavior.

---

### Task 10: Views — Progress Bar Endpoint

**File**: `apps/items/views.py`

Add `progress_bar_view(request, pk)` — returns the `_progress_bar.html` partial. Used by `hx-trigger="progress-updated from:body"` on the progress section.

**Acceptance**: Returns correct percentage HTML fragment.

---

### Task 11: URLs — Wire Assignment Patterns

**File**: `apps/items/urls.py`

Add URL patterns for claim, edit_assignment, cancel_assignment, purchase_assignment, and progress.

**Acceptance**: URL resolution tests.

---

### Task 12: Template — Rewrite `_item_row.html` with Assignments

**File**: `apps/items/templates/items/partials/_item_row.html`

Extend the existing item row to:
1. Show assignment list below item name (assignee name, quantity, status)
2. Show "Asignarme" button for uncovered items (accepted participants only)
3. Show claim form inline when clicked (HTMX GET)
4. Show edit/cancel/purchase actions per assignment based on permissions
5. Show available quantity hint for quantified items
6. Add red highlight ring when event is closed and item is uncovered

**Acceptance**: Visual match with design spec. Correct buttons shown per role.

---

### Task 13: Template — `_assignment_row.html`

**File**: `apps/items/templates/items/partials/_assignment_row.html`

Create partial for a single assignment:
- Assignee avatar (initial) + name
- Quantity (for quantified items)
- Status badge (purchased ✓ or active)
- Action buttons: Edit, Cancel (own), Mark purchased, Owner cancel

**Acceptance**: Renders correctly for all permission combinations.

---

### Task 14: Template — `_progress_bar.html`

**File**: `apps/items/templates/items/partials/_progress_bar.html`

Extract progress bar section from event-detail into a standalone partial:
- Percentage display
- Animated bar with correct width
- `hx-get` endpoint for refresh
- `hx-trigger="progress-updated from:body"` for reactive updates

**Acceptance**: Updates correctly after assignment changes.

---

### Task 15: Template — Claim Form Fragment

**File**: `apps/items/templates/items/claim-item.html`

Inline form fragment for claiming:
- Quantity input (shown only for quantified items)
- Available quantity hint text
- Submit button "Confirmar"
- Cancel link to collapse form

**Acceptance**: Form submits via HTMX, returns updated item row.

---

### Task 16: Template — Edit Assignment Fragment

**File**: `apps/items/templates/items/edit-assignment.html`

Inline form for modifying quantity:
- Pre-filled quantity input
- Available quantity hint
- Submit + Cancel buttons

**Acceptance**: Form submits via HTMX, returns updated item row.

---

### Task 17: Event Detail View — Wire Context

**File**: `apps/events/views.py`

Modify `event_detail_view` to pass additional context:
- Prefetch assignments for each item (with user info)
- Pass `request.user` to template for permission checks
- Pass event progress data for initial render

**Acceptance**: No N+1 queries. Progress renders correctly on page load.

---

### Task 18: Template Tags — `available_quantity`

**File**: `apps/items/templatetags/items_tags.py`

Add `@register.simple_tag` for `available_quantity(item)` that returns remaining claimable quantity.

**Acceptance**: Returns correct value based on annotations.

---

### Task 19: Integration Test Suite

**File**: `apps/items/tests/test_assignments.py`

Comprehensive test file covering:
- All service layer functions (already covered per-task, consolidate here)
- View integration with HTMX
- Permission matrix: participant/co-admin/owner × each action × each event status
- Edge case: race condition (concurrent claims — verify constraint)
- Progress bar computation accuracy

**Acceptance**: All tests pass. Coverage of critical paths.

---

### Task 20: Tailwind Build + Visual Verification

Rebuild `static/css/main.css` with new `@source` directives if needed. Verify:
- Status colors render correctly
- Red highlight on uncovered items in closed events
- Progress bar animation works
- Responsive layout (mobile: items stack, desktop: 2-col grid)

**Acceptance**: `./tailwindcss -i static/css/input.css -o static/css/main.css` succeeds. Visual spot-check.

---

## Done Criteria Mapping

| ROADMAP Done Criterion | Task(s) |
|---|---|
| Participant can claim quantified item | 2, 8, 9, 12, 15 |
| Claim blocked when exceeding total | 2, 9 |
| Binary item claim works | 2, 9, 12 |
| Modify own non-purchased assignment | 3, 9, 12, 16 |
| Cancel own non-purchased (with confirmation) | 4, 9, 12, 13 |
| Mark purchased requires confirmation, irreversible | 5, 9, 13 |
| Mark purchased allowed in closed events | 5, 9 |
| Mark purchased blocked in cancelled events | 5, 9 |
| Owner can cancel others (with confirmation) | 4, 9, 13 |
| Co-admin cannot cancel others | 4, 9, 19 |
| Item status semaphore updates correctly | Already working from Phase 5 + HTMX refresh |
| Progress bar reflects completion | 6, 10, 14, 17 |
| Uncovered items highlighted when closed | 12, 20 |
