# Phase 4 — Event Access: Tasks

## Task Group 1: Service Layer

- [ ] **T-4.1.1** Add `request_to_join(user, event)` to `services.py`
  - Validates event is `active` (not closed/cancelled)
  - Checks existing participation: if `left` or `removed`, updates to `pending`
  - If no existing participation, creates new row with `role=participant, access_status=pending, requested_at=now()`
  - Raises `ValueError` if user already has `pending`, `accepted`, or `rejected` status
- [ ] **T-4.1.2** Add `approve_request(participation)` to `services.py`
  - Sets `access_status=accepted`, `responded_at=now()`
  - Raises `ValueError` if participation is not `pending`
- [ ] **T-4.1.3** Add `reject_request(participation)` to `services.py`
  - Sets `access_status=rejected`, `responded_at=now()`
  - Raises `ValueError` if participation is not `pending`
- [ ] **T-4.1.4** Add `correct_rejection(participation)` to `services.py`
  - Sets `access_status=accepted`, `responded_at=now()`
  - Raises `ValueError` if participation is not `rejected`
- [ ] **T-4.1.5** Add `leave_event(participation)` to `services.py`
  - Validates participant is `accepted` (not owner)
  - Checks no purchased assignments exist
  - If co-admin, demotes to participant first (role = participant)
  - Sets `access_status=left`, `left_at=now()`
  - Raises `ValueError` if user is owner or has purchased assignments

## Task Group 2: Decorator

- [ ] **T-4.2.1** Add `event_admin_required` decorator to `decorators.py`
  - Allows Owner OR any user with `role=co_admin` and `access_status=accepted`
  - Returns 403 if neither condition is met
  - Injects `event` and `participation` (for co-admin) or `event` (for owner)

## Task Group 3: Views

- [ ] **T-4.3.1** Modify `public_card_view` to handle all participation states
  - No participation / left / removed → show join button
  - Pending → redirect to `events:participation_status`
  - Accepted → redirect to `events:detail`
  - Rejected → redirect to `events:participation_status`
  - Closed/cancelled event → show card without join button + message
- [ ] **T-4.3.2** Add `request_to_join_view` (POST only)
  - Calls `request_to_join` service
  - On success: redirect to `events:participation_status`
  - On error: message + redirect back to public card
- [ ] **T-4.3.3** Add `participation_status_view` (GET)
  - Shows pending or rejected state based on current participation
  - If no pending/rejected participation exists, redirect to appropriate place
- [ ] **T-4.3.4** Add `manage_requests_view` (GET)
  - Lists all pending requests for the event
  - Also shows recently rejected requests (for correction)
  - Uses `event_admin_required` decorator
- [ ] **T-4.3.5** Add `approve_request_view` (POST)
  - Calls `approve_request` service
  - Returns HTMX partial (empty response for row removal) or redirect
- [ ] **T-4.3.6** Add `reject_request_view` (POST)
  - Calls `reject_request` service
  - Returns HTMX partial or redirect
- [ ] **T-4.3.7** Add `correct_rejection_view` (POST)
  - Calls `correct_rejection` service
  - Returns HTMX partial or redirect
- [ ] **T-4.3.8** Add `leave_event_view` (POST)
  - Calls `leave_event` service
  - On success: redirect to dashboard with message
  - On error: message + redirect back to event detail

## Task Group 4: URLs

- [ ] **T-4.4.1** Add new URL patterns to `apps/events/urls.py`
  - `/join/<uuid:token>/request/` → `request_to_join_view`
  - `/<uuid:pk>/status/` → `participation_status_view`
  - `/<uuid:pk>/requests/` → `manage_requests_view`
  - `/<uuid:pk>/requests/<uuid:participation_id>/approve/` → `approve_request_view`
  - `/<uuid:pk>/requests/<uuid:participation_id>/reject/` → `reject_request_view`
  - `/<uuid:pk>/requests/<uuid:participation_id>/correct/` → `correct_rejection_view`
  - `/<uuid:pk>/leave/` → `leave_event_view`

## Task Group 5: Templates

- [ ] **T-4.5.1** Download Stitch HTML and save to `docs/stitch-html/` (already done)
- [ ] **T-4.5.2** Modify `events/event-card-public.html`
  - Add "Solicitar unirme" button (POST form to join URL)
  - Show disabled/message state for closed/cancelled events
  - Handle re-request state (left/removed) — same button
- [ ] **T-4.5.3** Create `events/participation-status.html`
  - Match Stitch "Solicitud Pendiente" screen layout
  - Conditional rendering: pending vs rejected state
  - Show event card (name, date, organizer)
  - Lock icon + "list hidden" message
  - "Mis eventos" button back to dashboard
- [ ] **T-4.5.4** Create `events/manage-requests.html` (or embed in event detail)
  - Match Stitch "Gestión de Solicitudes" screen layout
  - List pending requests with display_name and email
  - "Aceptar" and "Rechazar" buttons per row
  - Section for recently rejected (with "Corregir" button)
- [ ] **T-4.5.5** Create `events/partials/_pending_requests.html`
  - HTMX-swappable section for the pending requests list
  - Include badge count
- [ ] **T-4.5.6** Create `events/partials/_request_row.html`
  - Single request row partial for HTMX swap after approve/reject
- [ ] **T-4.5.7** Modify `events/event-detail.html`
  - Add "Solicitudes pendientes" section (visible to Owner/Co-admin only)
  - Add "No puedo asistir" / "Abandonar evento" button for non-owner participants
  - Show pending badge count

## Task Group 6: Dashboard Enhancement

- [ ] **T-4.6.1** Modify `dashboard_view` to include pending request counts
  - For events where user is Owner or Co-admin, count pending participations
  - Pass counts in context
- [ ] **T-4.6.2** Modify dashboard template to show pending badge
  - Show coral badge with count on event cards (only for Owner/Co-admin)

## Task Group 7: Tests

- [ ] **T-4.7.1** Unit tests for service functions
  - `request_to_join`: happy path, closed event, duplicate, re-request after left/removed
  - `approve_request`: happy path, non-pending
  - `reject_request`: happy path, non-pending
  - `correct_rejection`: happy path, non-rejected
  - `leave_event`: happy path, owner blocked, purchased blocked, co-admin demotion
- [ ] **T-4.7.2** Integration tests for views
  - `public_card_view`: all states (no participation, pending, accepted, rejected, left, removed, closed event)
  - `request_to_join_view`: success, error cases
  - `participation_status_view`: pending, rejected, no participation
  - `manage_requests_view`: access control (owner OK, co-admin OK, participant 403)
  - `approve_request_view`: success, forbidden
  - `reject_request_view`: success, forbidden
  - `correct_rejection_view`: success, forbidden
  - `leave_event_view`: success, blocked cases
- [ ] **T-4.7.3** Test access control
  - `event_admin_required` decorator allows owner AND co-admin
  - Non-admin gets 403
  - Unauthenticated user gets redirect to login

## Task Group 8: Verification

- [ ] **T-4.8.1** Run full test suite — all tests pass
- [ ] **T-4.8.2** Run linter (ruff) — no errors
- [ ] **T-4.8.3** Manual verification of all done criteria from ROADMAP
- [ ] **T-4.8.4** Verify both Stitch screens match the design system tokens
