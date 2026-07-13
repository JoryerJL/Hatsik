# Phase 4 — Event Access: Design

## Architecture Decisions

### 1. No New Django App — Extend `events` App

The EventAccess module does NOT require a new Django app. All logic lives within `apps/events/` because:
- `EventParticipation` model already exists in `apps/events/models.py`
- Join, approve, reject, leave are operations on the same `EventParticipation` model
- URLs logically belong under the events namespace (`/events/join/...`, `/events/<pk>/requests/...`)

### 2. Service Layer Pattern (Same as Phase 3)

All business logic lives in `apps/events/services.py`. Views remain thin — they handle HTTP concerns (request/response, messages, redirects) and delegate to services.

New service functions:
- `request_to_join(user, event)` → creates/resets participation
- `approve_request(participation)` → sets accepted
- `reject_request(participation)` → sets rejected
- `correct_rejection(participation)` → changes rejected → accepted
- `leave_event(participation)` → validates and sets left

### 3. View Access Control Strategy

| Route | Who can access | Decorator |
|---|---|---|
| Public card (`/events/join/<token>/`) | Any authenticated user | `@login_required` |
| Join request POST | Any authenticated user without active participation | `@login_required` |
| Pending/rejected state | User with pending/rejected participation | `@login_required` |
| Request management | Owner / Co-admin | `@event_admin_required` (NEW) |
| Approve/reject/correct | Owner / Co-admin | `@event_admin_required` |
| Leave event | Accepted participant (not Owner) | `@participant_required` |

**New decorator: `event_admin_required`** — allows Owner OR Co-admin (not just Owner like `event_owner_required`).

### 4. URL Design

```
# Join flow (public share link entry point — already exists)
/events/join/<uuid:token>/                  GET  → public_card_view (MODIFIED)
/events/join/<uuid:token>/request/          POST → request_to_join_view (NEW)

# Pending/rejected state view
/events/<uuid:pk>/status/                   GET  → participation_status_view (NEW)

# Request management (Owner/Co-admin)
/events/<uuid:pk>/requests/                 GET  → manage_requests_view (NEW)
/events/<uuid:pk>/requests/<uuid:participation_id>/approve/  POST → approve_request_view (NEW)
/events/<uuid:pk>/requests/<uuid:participation_id>/reject/   POST → reject_request_view (NEW)
/events/<uuid:pk>/requests/<uuid:participation_id>/correct/  POST → correct_rejection_view (NEW)

# Leave event
/events/<uuid:pk>/leave/                    POST → leave_event_view (NEW)
```

### 5. Modifying `public_card_view` (Phase 3 Enhancement)

The existing `public_card_view` needs to handle multiple states:

1. **User NOT a participant** → Show event card + "Solicitar unirme" button
2. **User with `pending` status** → Redirect to `/events/<pk>/status/`
3. **User with `accepted` status** → Redirect to `/events/<pk>/` (event detail)
4. **User with `rejected` status** → Redirect to `/events/<pk>/status/`
5. **User with `left` or `removed` status** → Show event card + "Solicitar unirme" button (re-request)
6. **Event is `closed` or `cancelled`** → Show event card + message (no join button)

### 6. Template Strategy

| Template | Purpose |
|---|---|
| `events/event-card-public.html` | MODIFIED: add join button, closed/cancelled state |
| `events/participation-status.html` | NEW: pending + rejected state (same template, conditional) |
| `events/manage-requests.html` | NEW: list of pending requests with approve/reject actions |
| `events/event-detail.html` | MODIFIED: add "Solicitudes pendientes" section for admins |
| `events/partials/_pending_requests.html` | NEW: HTMX partial for requests section |
| `events/partials/_request_row.html` | NEW: single request row for approve/reject |

### 7. HTMX Strategy

Use HTMX for approve/reject actions to avoid full page reloads:
- Approve/reject buttons use `hx-post` with `hx-target` replacing the request row
- After approve: row disappears, badge count updates
- After reject: row disappears (or shows "rejected" state), badge count updates
- Confirmation for reject: use the existing `_modal.html` component with `hx-confirm` or custom modal

### 8. Dashboard Badge (Pending Count)

Add pending request count to the dashboard event card:
- Query `EventParticipation.objects.filter(event=event, access_status='pending').count()`
- Show coral badge with count if > 0
- Only visible to Owner and Co-admins

### 9. Re-request Flow (Left/Removed Users)

When a user who previously left or was removed follows the share link:
- Their existing participation is updated: `access_status=pending`, `requested_at=now()`, `left_at=NULL`, `removed_at=NULL`
- This avoids duplicate rows and respects the UNIQUE constraint on `(event, user)`

### 10. Confirmation Dialog

Reuse the existing `_modal.html` component for:
- Reject request confirmation
- Leave event confirmation

No new component needed.

---

## Data Flow

```
User follows share link
    ↓
login_required (redirect to login if not auth, with ?next=)
    ↓
public_card_view reads EventParticipation
    ↓
┌─ No participation or left/removed → Show "Solicitar unirme" button
│   ↓ POST
│   request_to_join_view → create/update participation (pending)
│   ↓ redirect
│   participation_status_view (pending screen)
│
├─ Pending → redirect to participation_status_view (pending screen)
├─ Rejected → redirect to participation_status_view (rejected screen)
└─ Accepted → redirect to event_detail_view
```

```
Owner/Co-admin views event detail
    ↓
event_detail_view includes pending requests section
    ↓
┌─ Approve (hx-post) → approve_request service → row removed via HTMX
└─ Reject (confirm modal → hx-post) → reject_request service → row removed via HTMX
```

---

## Testing Strategy

- **Unit tests** (services): test all service functions with valid/invalid inputs, edge cases
- **Integration tests** (views): test request/response cycle, redirects, access control
- **Edge cases**: double-submit, concurrent approve/reject, re-request after left, leave with purchases

---

## Dependencies

- No new Python packages required
- No new models or migrations (EventParticipation already has all needed fields)
- Uses existing design tokens from Warm Kitchen Board
- Uses existing `_modal.html` component
