# Requirements — Phase 3: Events & Dashboard

## Overview

A verified user can create events, see their events on the dashboard, manage the event lifecycle (close, reopen, cancel), share the event link and QR, manage co-admins, and remove participants.

**Modules:** Dashboard, Events
**Depends on:** Phase 2 (verified user session)

## Stitch Screen References

| Screen | ID | Purpose |
|---|---|---|
| Mis Eventos (Dashboard) | `533ded11556f4dc0a43dd05c0a1632e1` | Main screen after login |
| Crear Evento | `f9af4a49a1884a31b077ace0c40a4418` | Event creation form |
| Ficha del Evento | `b30692ae80c94ae6b69be8e1df8595c6` | Public-facing event card |
| Detalle del Evento | `32075f1d510242cdb9b880d66edea76c` | Full event detail for participants |
| Invitar Amigos | `95c384794de3421cb9780b51f3ed2478` | Share link and QR code |

---

## User Stories

### US-3.1: Dashboard — View My Events

**As a** verified user
**I want to** see a list of all events I'm part of
**So that** I can quickly access my events and understand my role in each

**Acceptance Criteria:**
- [ ] AC-3.1.1: Dashboard lists events where user is Owner, Co-admin, or accepted Participant
- [ ] AC-3.1.2: Each event card shows: event name, event date, user's role, event status (active/closed/cancelled)
- [ ] AC-3.1.3: Cancelled events remain visible as history (greyed out or marked)
- [ ] AC-3.1.4: Empty state shown when user has no events ("No tenés eventos aún")
- [ ] AC-3.1.5: Dashboard is the landing page after login (`/events/`)
- [ ] AC-3.1.6: Dashboard requires authentication (redirects to login if not authenticated)

### US-3.2: Create Event

**As a** verified user
**I want to** create a new event
**So that** I can organize a collaborative gift list

**Acceptance Criteria:**
- [ ] AC-3.2.1: Form fields: name (required), event_date (required), description (optional), assignment_deadline_at (optional)
- [ ] AC-3.2.2: On create: insert `events` row + Owner participation row (role=owner, access_status=accepted)
- [ ] AC-3.2.3: Auto-generate `public_share_token` (UUID) for the event
- [ ] AC-3.2.4: No confirmation dialog required on submit
- [ ] AC-3.2.5: After successful creation, redirect to the Event Detail page
- [ ] AC-3.2.6: Form validation errors shown inline (required fields, date format)

### US-3.3: Public Event Card (Ficha del Evento)

**As a** non-participant user
**I want to** see basic event information when I follow a share link
**So that** I can decide if I want to join

**Acceptance Criteria:**
- [ ] AC-3.3.1: Shows event name, description, and date
- [ ] AC-3.3.2: Does NOT show the item list to non-participants
- [ ] AC-3.3.3: Accessible via `/events/join/<public_share_token>/`
- [ ] AC-3.3.4: If user is not logged in, redirect to login (then back to event after login)
- [ ] AC-3.3.5: If user is already an accepted participant, redirect to Event Detail
- [ ] AC-3.3.6: "Join request" button behavior is deferred to Phase 4 — in this phase, show an informational message only

### US-3.4: Event Detail

**As an** accepted participant
**I want to** see the full event details and manage it (if Owner)
**So that** I can track the event and administer it

**Acceptance Criteria:**
- [ ] AC-3.4.1: Full view shows: event header (name, date, status), participant list, and placeholder for items (Phase 5)
- [ ] AC-3.4.2: Owner can edit event: name, description, date, deadline — no confirmation required
- [ ] AC-3.4.3: Owner can close event manually — requires confirmation dialog
- [ ] AC-3.4.4: Owner can reopen event — requires confirmation dialog
- [ ] AC-3.4.5: Owner can cancel event — requires confirmation dialog
- [ ] AC-3.4.6: A cancelled event CANNOT be reopened
- [ ] AC-3.4.7: Owner can assign co-admin — no confirmation required
- [ ] AC-3.4.8: Owner can revoke co-admin — requires confirmation dialog
- [ ] AC-3.4.9: Owner can remove participant — requires confirmation, blocked if participant has purchased assignments
- [ ] AC-3.4.10: Owner cannot remove themselves
- [ ] AC-3.4.11: Revoking a co-admin preserves their existing assignments
- [ ] AC-3.4.12: Only accepted participants can access Event Detail — others get 403 or redirect

### US-3.5: Share Event / Invite Friends

**As an** event Owner or Co-admin
**I want to** share a link and QR code for my event
**So that** people can join my event

**Acceptance Criteria:**
- [ ] AC-3.5.1: Display the full shareable link (built from `public_share_token`)
- [ ] AC-3.5.2: QR code rendered on-demand from `public_share_token` — NOT stored in DB
- [ ] AC-3.5.3: QR downloadable as PNG
- [ ] AC-3.5.4: Only Owner and Co-admin can access the share/invite screen
- [ ] AC-3.5.5: Copy-to-clipboard functionality for the link

### US-3.6: Automatic Event Closure

**As the** system
**I want to** automatically close events when their assignment deadline passes
**So that** events don't stay open indefinitely

**Acceptance Criteria:**
- [ ] AC-3.6.1: When `assignment_deadline_at` is reached, set event `status = closed` and `closed_at = NOW()`
- [ ] AC-3.6.2: Triggered via internal endpoint (`POST /internal/close-expired-events/`)
- [ ] AC-3.6.3: Endpoint protected by `X-Internal-Token` header
- [ ] AC-3.6.4: Only active events with a past `assignment_deadline_at` are affected
- [ ] AC-3.6.5: Events without `assignment_deadline_at` are never auto-closed

---

## Business Rules

| Rule | Enforcement |
|---|---|
| Only Owner can edit event data | View-level permission check |
| Only Owner can close, reopen, cancel | View-level permission check |
| Only Owner can assign/revoke co-admins | View-level permission check |
| Only Owner can remove participants | View-level permission check |
| A cancelled event cannot be reopened | Model/view validation |
| Removing participant with purchased assignments is blocked | Query check before removal |
| Owner cannot remove themselves | View-level check |
| Revoking co-admin preserves assignments | Only changes role, no cascade |
| A removed participant can re-request via share link | Handled in Phase 4 |

---

## Done Criteria (from ROADMAP)

- [ ] User can create an event and see it on the Dashboard
- [ ] Dashboard shows correct role and status for each event
- [ ] Share link and downloadable QR are generated correctly
- [ ] Owner can close, reopen, and cancel the event (each with confirmation)
- [ ] Owner can assign and revoke co-admins (revoke requires confirmation)
- [ ] Owner can remove participants (blocked if they have purchased assignments)
- [ ] Automatic closure fires when `assignment_deadline_at` is reached
- [ ] All 5 Stitch screens for this phase match the design system
