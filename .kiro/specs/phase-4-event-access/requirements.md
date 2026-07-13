# Phase 4 — Event Access: Requirements

## Overview

A user can join an event via share link or QR, go through the approval flow, and be accepted or rejected by the Owner/Co-admin. Users can also leave events voluntarily.

**Module:** `EventAccess`
**Depends on:** Phase 3 (events must exist; share link and roles must be working)

## Stitch Screen References

| Screen | ID |
|---|---|
| Solicitud Pendiente | `e9b1b3a8511c4ef882584dffe0b086ba` |
| Gestión de Solicitudes | `701373d8c8384b49891b4e60050ab12f` |

> Note: `Ficha del Evento` (`b30692ae80c94ae6b69be8e1df8595c6`) built in Phase 3 also serves as the join entry point. Its "Request to join" button behavior is completed in this phase.

---

## User Stories

### US-4.1: Request to Join an Event

**As a** registered and verified user who follows a share link,
**I want to** request access to the event,
**So that** the organizer can approve me and I can participate.

**Acceptance Criteria:**

- [ ] AC-4.1.1: Following the share link while unauthenticated redirects to login with `next` pointing back to the event public card.
- [ ] AC-4.1.2: Authenticated user sees the Ficha del Evento with a "Solicitar unirme" button.
- [ ] AC-4.1.3: Clicking the button creates an `event_participations` row with `role=participant`, `access_status=pending`, `requested_at=now()`.
- [ ] AC-4.1.4: No confirmation dialog is required before submitting the request.
- [ ] AC-4.1.5: Attempting to join a `closed` or `cancelled` event shows an error message and the button is disabled/hidden.
- [ ] AC-4.1.6: If the user already has a participation (pending, accepted, or rejected), the button is not shown — show the appropriate state instead.
- [ ] AC-4.1.7: If the user was previously removed (`access_status=removed`) or left (`access_status=left`), they CAN re-request. A new participation row is created (or existing one is updated to `pending`).

### US-4.2: Pending Request State

**As a** user who has submitted a join request,
**I want to** see a clear indication that my request is pending,
**So that** I know the organizer needs to approve me.

**Acceptance Criteria:**

- [ ] AC-4.2.1: After submitting, the user is redirected to the "Solicitud Pendiente" screen.
- [ ] AC-4.2.2: The screen shows the event card (name, date, organizer name) and a "pending approval" message.
- [ ] AC-4.2.3: The item list is NOT visible while status is `pending`.
- [ ] AC-4.2.4: If the user navigates directly to the event detail while pending, they are redirected to the pending screen.
- [ ] AC-4.2.5: A lock icon with text explains that the item list becomes visible after acceptance.

### US-4.3: Rejected State

**As a** user whose request was rejected,
**I want to** see that my request was rejected,
**So that** I understand I cannot access the event.

**Acceptance Criteria:**

- [ ] AC-4.3.1: Rejected user sees a "rejected" status on the event card (similar layout to pending screen but with rejected state).
- [ ] AC-4.3.2: The item list is NOT visible for rejected users.
- [ ] AC-4.3.3: Rejected user CANNOT re-request access (no button shown).
- [ ] AC-4.3.4: If a rejected request is later corrected to `accepted` by Owner/Co-admin, the user gains full access.

### US-4.4: Manage Pending Requests (Owner/Co-admin)

**As an** event Owner or Co-admin,
**I want to** see and act on pending join requests,
**So that** I can control who participates in my event.

**Acceptance Criteria:**

- [ ] AC-4.4.1: "Solicitudes pendientes" section is visible in the event detail page for Owner and Co-admins.
- [ ] AC-4.4.2: Each request shows the applicant's `display_name` and `email`.
- [ ] AC-4.4.3: "Aceptar" button sets `access_status=accepted`, `responded_at=now()`. No confirmation required.
- [ ] AC-4.4.4: "Rechazar" button requires a confirmation dialog. On confirm, sets `access_status=rejected`, `responded_at=now()`.
- [ ] AC-4.4.5: A badge with the pending request count is shown on the event card in the Dashboard.
- [ ] AC-4.4.6: Owner/Co-admin can change a previously rejected request to accepted (correction flow).
- [ ] AC-4.4.7: The section is hidden when there are no pending requests (empty state with message).

### US-4.5: Leave Event Voluntarily

**As an** accepted participant,
**I want to** leave an event voluntarily,
**So that** I can opt out if I can no longer attend.

**Acceptance Criteria:**

- [ ] AC-4.5.1: "No puedo asistir" / "Abandonar evento" button is visible for accepted participants (not Owner).
- [ ] AC-4.5.2: Confirmation dialog is required before leaving.
- [ ] AC-4.5.3: Leaving is blocked if the participant has purchased assignments. Error message explains why.
- [ ] AC-4.5.4: On leave: `access_status=left`, `left_at=now()`.
- [ ] AC-4.5.5: If a Co-admin leaves, their role is automatically revoked to `participant` before setting `left`.
- [ ] AC-4.5.6: Owner CANNOT leave their own event (button not shown for Owner).
- [ ] AC-4.5.7: A user who left CAN re-request entry via the share link (enters as regular Participant, no role restoration).

---

## Business Rules

1. Having the link does NOT grant automatic access to the item list.
2. A rejected user cannot re-request access — unless Owner/Co-admin manually corrects the rejection.
3. A rejected → accepted → voluntarily left user CAN re-request entry.
4. Re-joining always enters as a regular Participant (no automatic role restoration).
5. Access control is enforced server-side, not just in the UI.

---

## Done Criteria (from ROADMAP)

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
