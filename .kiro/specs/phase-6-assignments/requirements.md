# Phase 6 — Assignments: Requirements

## Overview

Participants can claim items (partially or fully), modify their claims, mark them as purchased. Owner can cancel others' claims. This is the final phase of the MVP — it completes the core loop of the application.

## Module

`Assignments` (extends `apps/items` — no new Django app needed since `ItemAssignment` model already exists in `apps.items.models`)

## Dependencies

- Phase 5 (Items & Moderation) — items must exist with computed status
- Phase 4 (Event Access) — accepted participants must have event roles enforced
- Phase 3 (Events) — event status transitions must be working

## Stitch Screens

**None** — Assignment UI lives inside Detalle del Evento (screen `32075f1d510242cdb9b880d66edea76c`), already built in Phase 3 and extended in Phase 5.

---

## User Stories

### US-1: Claim a Quantified Item

**As** an accepted participant,
**I want to** claim a portion of a quantified item,
**So that** other participants know I'm bringing part of it.

**Acceptance Criteria:**

1. Participant sees a "Claim" action on items in the event detail
2. For quantified items, a quantity input appears (max = available quantity)
3. Validation blocks claims where sum of active assignments would exceed `quantity_total`
4. On success, assignment is created and item status recomputes immediately
5. No confirmation dialog required on create
6. Claim button is disabled for fully covered items (`cubierto` or above)
7. Participant can only have ONE active assignment per item (partial unique constraint)

### US-2: Claim a Binary Item

**As** an accepted participant,
**I want to** claim a binary item ("I'll bring this"),
**So that** the item shows as covered.

**Acceptance Criteria:**

1. Binary items show a simple "I'll bring this" toggle/button (no quantity input)
2. On success, assignment is created with `quantity_assigned = NULL`
3. Item status moves from `sin_asignar` → `cubierto`
4. Covered binary items show the assignee name instead of a claim button

### US-3: Modify Own Assignment

**As** a participant with an active non-purchased assignment,
**I want to** modify my claimed quantity,
**So that** I can adjust what I'm bringing.

**Acceptance Criteria:**

1. Participant sees an "Edit" action on their own active assignment
2. Can change `quantity_assigned` (quantified items only)
3. Validation: new quantity + other assignments cannot exceed `quantity_total`
4. Cannot modify a purchased assignment (edit button hidden)
5. No confirmation required
6. Item status recomputes after modification

### US-4: Cancel Own Assignment

**As** a participant with an active non-purchased assignment,
**I want to** cancel my claim,
**So that** the quantity returns to the available pool.

**Acceptance Criteria:**

1. Participant sees a "Cancel claim" action on their own active assignment
2. Requires confirmation dialog before cancellation
3. On cancel: sets `cancelled_at` and `cancelled_by_user`, does NOT delete the row
4. Quantity returns to available pool, item status recomputes
5. Cannot cancel a purchased assignment (action hidden)
6. After cancellation, participant can claim the same item again (new assignment row)

### US-5: Mark as Purchased

**As** an assignee (or Owner/Co-admin),
**I want to** mark an assignment as purchased,
**So that** the event tracks real progress.

**Acceptance Criteria:**

1. Any assignee can mark their own assignment as purchased
2. Owner and Co-admin can mark ANY assignment as purchased
3. Requires confirmation dialog ("This action cannot be undone")
4. Sets `purchased_at` timestamp and `purchased_by_user`
5. Purchased assignments become immutable — no edit, no cancel
6. Item status recalculates: some purchased → `parcialmente_comprado`, all purchased → `comprado`
7. Marking as purchased IS allowed when event status is `closed`
8. Marking as purchased IS BLOCKED when event status is `cancelled`

### US-6: Owner Cancels Others' Assignments

**As** an event owner,
**I want to** cancel any participant's non-purchased assignment,
**So that** I can manage the event's item coverage.

**Acceptance Criteria:**

1. Owner sees a "Cancel" action on any non-purchased assignment (not just their own)
2. Co-admin does NOT see this action on others' assignments
3. Requires confirmation dialog
4. On cancel: quantity returns to pool, item status recomputes
5. Cannot cancel purchased assignments

### US-7: Event Progress Bar

**As** a participant viewing event detail,
**I want to** see overall event progress,
**So that** I understand how much of the shopping is covered.

**Acceptance Criteria:**

1. Progress bar visible in event detail view
2. Shows percentage of items that are fully covered OR purchased
3. Updates reactively after any assignment action (via HTMX partial refresh)

### US-8: Highlighted Uncovered Items at Closure

**As** a participant viewing a closed event,
**I want to** see uncovered items highlighted,
**So that** I know what's still missing.

**Acceptance Criteria:**

1. When event status is `closed`, items with status `sin_asignar` or `parcialmente_cubierto` are highlighted in red (using `state-unassigned` color token)
2. No automatic reassignment — just visual indicator

---

## Business Rules

| Rule | Enforcement |
|------|-------------|
| Sum of active assignments ≤ `quantity_total` | Service layer validation + DB check |
| Purchased assignments are immutable | Service layer blocks modify/cancel |
| `cancelled` events: no new assignments, no modifications, no cancellations, no mark as purchased | Service layer blocks all write operations |
| `closed` events: no new assignments, no modifications, no cancellations — but marking as purchased IS allowed | Service layer conditional check |
| Co-admin cannot cancel others' assignments | Permission check in service + view |
| One active assignment per user per item | DB UniqueConstraint (already exists) |

---

## Event Status vs. Allowed Assignment Actions

| Event Status | Claim | Modify | Cancel | Mark Purchased |
|--------------|-------|--------|--------|----------------|
| `active` | ✅ | ✅ | ✅ | ✅ |
| `closed` | ❌ | ❌ | ❌ | ✅ |
| `cancelled` | ❌ | ❌ | ❌ | ❌ |
