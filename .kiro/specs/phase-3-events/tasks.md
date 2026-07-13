# Tasks — Phase 3: Events & Dashboard

## Task Groups

### Group 1: Infrastructure & Routing

- [ ] 1.1: Create `apps/events/urls.py` with namespace `events` and all URL patterns
- [ ] 1.2: Register events URLs in `config/urls.py` (`path("events/", include("apps.events.urls"))`)
- [ ] 1.3: Create `apps/events/decorators.py` with `@event_owner_required` and `@participant_required`
- [ ] 1.4: Create `apps/events/services.py` with all business logic functions (stubs first)
- [ ] 1.5: Create `apps/events/templates/events/` directory and empty template files
- [ ] 1.6: Create `apps/events/tests/__init__.py`

### Group 2: Forms

- [ ] 2.1: Create `CreateEventForm` — fields: name, event_date, description, assignment_deadline_at
- [ ] 2.2: Create `EditEventForm` — same fields as CreateEventForm, all optional except name and event_date
- [ ] 2.3: Write tests for form validation (`apps/events/tests/test_forms.py`)

### Group 3: Services Layer

- [ ] 3.1: Implement `create_event()` — creates Event + Owner EventParticipation in a transaction
- [ ] 3.2: Implement `close_event()` — sets status=closed, closed_at=now; raises on cancelled
- [ ] 3.3: Implement `reopen_event()` — sets status=active, clears closed_at; raises on cancelled
- [ ] 3.4: Implement `cancel_event()` — sets status=cancelled, cancelled_at=now; raises if already cancelled
- [ ] 3.5: Implement `promote_to_co_admin()` — changes participation role to co_admin
- [ ] 3.6: Implement `demote_co_admin()` — changes participation role back to participant
- [ ] 3.7: Implement `remove_participant()` — sets access_status=removed, removed_at=now; raises if has purchased assignments
- [ ] 3.8: Implement `close_expired_events()` — bulk update active events past deadline
- [ ] 3.9: Write tests for all service functions (`apps/events/tests/test_services.py`)

### Group 4: Dashboard View & Template

- [ ] 4.1: Implement `dashboard_view` — query events for current user (Owner/Co-admin/Accepted Participant)
- [ ] 4.2: Fetch Stitch screen `533ded11556f4dc0a43dd05c0a1632e1` and match design
- [ ] 4.3: Create `events/dashboard.html` template with event cards and empty state
- [ ] 4.4: Create `events/_event_card.html` partial for individual event cards
- [ ] 4.5: Update `accounts` login redirect to point to `/events/` (dashboard as home)
- [ ] 4.6: Write view tests for dashboard (`apps/events/tests/test_views.py` — dashboard section)

### Group 5: Create Event View & Template

- [ ] 5.1: Implement `create_event_view` — GET shows form, POST validates and creates
- [ ] 5.2: Fetch Stitch screen `f9af4a49a1884a31b077ace0c40a4418` and match design
- [ ] 5.3: Create `events/create-event.html` template with the creation form
- [ ] 5.4: Write view tests for create event (happy path, validation errors)

### Group 6: Event Detail View & Template

- [ ] 6.1: Implement `event_detail_view` — shows full event info for accepted participants
- [ ] 6.2: Fetch Stitch screen `32075f1d510242cdb9b880d66edea76c` and match design
- [ ] 6.3: Create `events/event-detail.html` template with event header, participant list, lifecycle buttons (Owner only)
- [ ] 6.4: Create `events/_participant_row.html` partial
- [ ] 6.5: Create `events/_confirm_modal.html` reusable confirmation dialog
- [ ] 6.6: Implement `edit_event_view` — HTMX form swap for inline editing (Owner only)
- [ ] 6.7: Create `events/_edit_form.html` partial for inline edit
- [ ] 6.8: Write view tests for event detail and edit (permissions, happy path)

### Group 7: Event Lifecycle Views

- [ ] 7.1: Implement `close_event_view` — POST, Owner only, calls service, returns HX-Redirect
- [ ] 7.2: Implement `reopen_event_view` — POST, Owner only, calls service, returns HX-Redirect
- [ ] 7.3: Implement `cancel_event_view` — POST, Owner only, calls service, returns HX-Redirect
- [ ] 7.4: Write view tests for lifecycle actions (permissions, state transitions, cancelled cannot reopen)

### Group 8: Participant Management Views

- [ ] 8.1: Implement `remove_participant_view` — POST, Owner only, calls service, HTMX response
- [ ] 8.2: Implement `promote_participant_view` — POST, Owner only, calls service, HTMX response
- [ ] 8.3: Implement `demote_participant_view` — POST, Owner only, calls service, HTMX response
- [ ] 8.4: Write view tests for participant management (permissions, edge cases)

### Group 9: Share/Invite & QR

- [ ] 9.1: Implement `share_event_view` — shows share link and QR for Owner/Co-admin
- [ ] 9.2: Implement `share_qr_view` — returns PNG image response
- [ ] 9.3: Fetch Stitch screen `95c384794de3421cb9780b51f3ed2478` and match design
- [ ] 9.4: Create `events/share-event.html` template with link, copy button, QR preview, download button
- [ ] 9.5: Write view tests for share (permissions, QR content)

### Group 10: Public Event Card

- [ ] 10.1: Implement `public_card_view` — lookup by share token, show event info
- [ ] 10.2: Fetch Stitch screen `b30692ae80c94ae6b69be8e1df8595c6` and match design
- [ ] 10.3: Create `events/event-card-public.html` — shows name, description, date; no items; "join" placeholder for Phase 4
- [ ] 10.4: Handle redirect logic: not logged in → login → back; already participant → detail
- [ ] 10.5: Write view tests for public card (auth redirect, participant redirect, normal display)

### Group 11: Auto-Close Integration

- [ ] 11.1: Wire `close_expired_events()` service into the existing `apps/internal/views.py` endpoint
- [ ] 11.2: Write integration test for the internal close endpoint (token auth, correct events closed)

### Group 12: Final Verification

- [ ] 12.1: Run full test suite — all tests pass
- [ ] 12.2: Run linter (`ruff check`) — no errors
- [ ] 12.3: Run type check if configured
- [ ] 12.4: Manual verification: create event, view on dashboard, edit, close, reopen, cancel, share, view QR
- [ ] 12.5: Verify all 5 Stitch screen designs are matched
- [ ] 12.6: Generate `docs/html/phase-3-testing.html` manual QA guide

---

## Execution Order

Groups 1-3 first (infrastructure, forms, services) → then Groups 4-10 (views + templates) → Group 11 (integration) → Group 12 (verification).

Within Groups 4-10, implementation can proceed sequentially since each builds on the routing and services already established.

## Test Strategy

- **Unit tests**: Forms (validation), Services (business logic, state transitions, error cases)
- **Integration tests**: Views (HTTP methods, permissions, redirects, HTMX responses)
- **Coverage targets**: All service functions, all permission boundaries, all state transition edge cases
- **Test runner**: `pytest` with `pytest-django`
