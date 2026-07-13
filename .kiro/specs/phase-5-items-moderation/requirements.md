# Phase 5 — Items & Moderation: Requirements

> **Goal:** Owner can manage the item list. Participants can suggest new items. Owner/Co-admin can approve or reject suggestions.
> **Modules:** `Items`, `Moderation`
> **Depends on:** Phase 4 (accepted participants must exist; event roles must be enforced)

## Stitch Screens

| Screen | ID | Module |
|---|---|---|
| Añadir Ítem | `f4ee82a1da0542898d47b5e0eaabe809` | Items |
| Editar Ítem | `4264f659cdcc4d2c931e77a63c27063a` | Items |
| Sugerir Ítem | `0c8fa38e491e43c2a5da6a3d984f702e` | Moderation |

> Items are displayed inside Detalle del Evento (screen `32075f1d510242cdb9b880d66edea76c`). This phase completes that screen's item list section.

---

## User Stories

### US-5.1: Add Item (Owner)

**As** an event owner,
**I want** to add items to my event's shopping list,
**So that** participants know what needs to be brought.

**Acceptance Criteria:**
- [ ] Form fields: name (required), quantity_total (optional), unit (required if quantity is set).
- [ ] Unit is selected from a controlled catalog (dropdown), not free text.
- [ ] No confirmation dialog required on add.
- [ ] New item appears immediately in the item list.
- [ ] Adding items is blocked in `closed` or `cancelled` events.
- [ ] Only the Owner can add items (not co-admins, not participants).
- [ ] UI matches Stitch screen `f4ee82a1da0542898d47b5e0eaabe809` (Añadir Ítem).

### US-5.2: Edit Item (Owner)

**As** an event owner,
**I want** to edit items on my event's list,
**So that** I can correct mistakes or adjust quantities.

**Acceptance Criteria:**
- [ ] Item with NO assignments: Owner can edit name, quantity, and unit. No confirmation required.
- [ ] Item WITH assignments: Owner can edit quantity_total ONLY. Must show a warning message. Requires confirmation dialog.
- [ ] Cannot reduce quantity below the sum of active (non-cancelled) assignments.
- [ ] Editing items is blocked in `closed` or `cancelled` events.
- [ ] Only the Owner can edit items.
- [ ] UI matches Stitch screen `4264f659cdcc4d2c931e77a63c27063a` (Editar Ítem).

### US-5.3: Delete Item (Owner)

**As** an event owner,
**I want** to delete items from the list,
**So that** I can remove items that are no longer needed.

**Acceptance Criteria:**
- [ ] Deletion requires confirmation dialog.
- [ ] Deleting an item also deletes all associated assignments.
- [ ] Deleting items is blocked in `closed` or `cancelled` events.
- [ ] Only the Owner can delete items.

### US-5.4: Item Status Display (Computed Semaphore)

**As** an event participant,
**I want** to see the status of each item via a color-coded indicator,
**So that** I know which items still need to be claimed or purchased.

**Acceptance Criteria:**
- [ ] Status is NEVER stored in the database — always computed from `item_assignments` at query time.
- [ ] Status values and colors:
  - `sin_asignar` → `#FCA5A5` (red) — No active assignments.
  - `parcialmente_cubierto` → `#FDBA74` (orange) — Sum of assignments < quantity_total.
  - `cubierto` → `#86EFAC` (green) — Sum of assignments = quantity_total.
  - `parcialmente_comprado` → `#93C5FD` (blue) — Some but not all assignees marked purchased.
  - `comprado` → `#4ADE80` (bright green) — All assignees marked purchased.
- [ ] Binary items (no quantity): `sin_asignar` → `cubierto` → `comprado`.
- [ ] Status updates correctly after every assignment/purchase/cancellation action.

### US-5.5: Suggest Item (Participant)

**As** an accepted participant,
**I want** to suggest items for the event's list,
**So that** I can propose things the group might need.

**Acceptance Criteria:**
- [ ] Form fields: name (required), quantity_total (optional), unit (optional but required if quantity is set).
- [ ] No confirmation required on suggest.
- [ ] Suggested items are NOT visible in the official item list until approved by Owner/Co-admin.
- [ ] Participant can see the status of their own suggestions (pending / approved / rejected + rejection note).
- [ ] Suggesting items is blocked in `closed` or `cancelled` events.
- [ ] UI matches Stitch screen `0c8fa38e491e43c2a5da6a3d984f702e` (Sugerir Ítem).

### US-5.6: Edit Own Suggestion (Participant)

**As** a participant who suggested an item,
**I want** to edit my pending suggestion,
**So that** I can fix typos or adjust the quantity before it's reviewed.

**Acceptance Criteria:**
- [ ] Participant can edit only their own suggestions.
- [ ] Only pending suggestions can be edited.
- [ ] No confirmation required on edit.

### US-5.7: Delete Own Suggestion (Participant)

**As** a participant who suggested an item,
**I want** to delete my pending suggestion,
**So that** I can withdraw it if I change my mind.

**Acceptance Criteria:**
- [ ] Participant can delete only their own suggestions.
- [ ] Only pending suggestions can be deleted.
- [ ] Deletion requires confirmation dialog.

### US-5.8: Approve Suggestion (Owner / Co-admin)

**As** an event owner or co-admin,
**I want** to approve participant suggestions,
**So that** useful suggestions become official items on the list.

**Acceptance Criteria:**
- [ ] Owner and Co-admin can approve pending suggestions.
- [ ] Before approving, they can optionally modify name, quantity, or unit.
- [ ] No confirmation required on approve.
- [ ] Approved suggestion creates an official item with computed status `sin_asignar`.
- [ ] The official item does NOT show "suggested by" (anonymous once approved).
- [ ] "Pending Suggestions" section visible in event detail for Owner/Co-admin.

### US-5.9: Reject Suggestion (Owner / Co-admin)

**As** an event owner or co-admin,
**I want** to reject participant suggestions,
**So that** inappropriate or duplicate suggestions don't clutter the list.

**Acceptance Criteria:**
- [ ] Owner and Co-admin can reject pending suggestions.
- [ ] Rejection includes an optional rejection note (free text).
- [ ] Rejection requires confirmation dialog.
- [ ] Rejection note is visible to the suggester.
- [ ] Rejection note is visible to Owner/Co-admins in the suggestion history.

---

## Business Rules

1. Only the Owner manages the official item list (add/edit/delete). Co-admins CANNOT add/edit/delete items.
2. Item status is NEVER stored — always computed from `item_assignments` at query time.
3. Unit is controlled via enum — enforced at both DB level and UI level (select dropdown).
4. Modifying quantity with existing assignments ALWAYS shows a warning before confirmation.
5. Cannot reduce quantity below sum of active assignments.
6. Items cannot be added/edited/deleted in `closed` or `cancelled` events.
7. Suggestions are invisible to the official list until approved.
8. Only the suggester can edit/delete their own pending suggestion.
9. Approved suggestions don't attribute the original author in the official list.

---

## Done Criteria (from ROADMAP)

- [ ] Owner can add, edit, and delete items.
- [ ] Edit of quantity-constrained item with assignments shows warning and requires confirmation.
- [ ] Reduction below assigned quantity is blocked.
- [ ] Item status is computed correctly and displays with the correct semaphore color.
- [ ] Participants can suggest items; suggestions are hidden from the official list until approved.
- [ ] Participants can edit and delete their own pending suggestions.
- [ ] Owner/Co-admin can approve (with optional pre-approval edits) and reject suggestions.
- [ ] Rejection note is visible to the suggester.
- [ ] Approved suggestion becomes an official item without attributing the suggestion author.
- [ ] All 3 Stitch screens for this phase match the design system.
