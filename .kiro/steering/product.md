# Product Overview — Hatsik

Hatsik ("dividir, compartir" in Maya) is a collaborative web app for organizing potlucks and group gatherings (asados, posadas, birthdays, picnics). It solves the "¿qué llevo?" (what should I bring?) coordination problem that normally happens over chaotic WhatsApp threads.

## Core concept

An **Owner** creates an **Event**, defines a list of **Items** (with optional quantity/unit), and shares it via a private link + QR code. **Participants** join by requesting entry (must be approved), then claim items they'll bring — fully or partially. The list updates in real time so nobody double-buys or misses something.

## Roles (per-event, not global)

- **Owner**: creator of the event. Full control — edit event/list, approve/reject entry requests and suggestions, assign/revoke co-admins, remove participants, cancel others' unpurchased assignments, close/reopen/cancel the event.
- **Co-admin**: participant delegated by the Owner. Can approve/reject entry requests and suggestions, mark any assignment as purchased. Cannot edit the event/list, name other co-admins, or remove participants.
- **Participant**: any approved user. Can view the list, claim items (partial/full), suggest new items (pending approval), mark their own claims as purchased, leave the event (if no unpurchased assignments).

The Owner is also a participant and can claim items on their own list.

## Key domain rules

- All users must register (email + password); no anonymous participation.
- Events are private — access only via shareable link or QR code, never publicly searchable.
- Items are either quantified (need a unit from a controlled catalog: kg, g, litros, ml, piezas, paquetes, bolsas, cajas, latas, botellas, garrafones, charolas, docenas) or binary (someone brings it or not).
- Item state is always computed automatically, never set manually: `sin_asignar` → `parcialmente_cubierto` → `cubierto` → `parcialmente_comprado` → `comprado`.
- A purchased assignment is immutable in the MVP — it cannot be unmarked, modified, or cancelled.
- Events have a lifecycle: `activo` → `cerrado` (manual or auto via deadline) / `cancelado`. Closed events are read-only for new assignments but existing assignees can still mark items purchased. Cancelled events block everything and are kept as history (no hard deletes anywhere — soft state via enums and timestamps).

## Explicitly out of scope for MVP

OAuth login, event notifications (in-app/email/push beyond transactional account emails), chat/comments, shared payments, multiple lists per event, history/stats, list templates, in-app invitations by email/phone, public searchable events, offline/PWA, native mobile app, item photos.

See `docs/PRODUCT_OVERVIEW.md` for the full spec (use cases, entities, state diagrams, decisions log).
