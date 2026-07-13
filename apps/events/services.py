"""Business logic for event operations."""

from django.db import transaction
from django.utils import timezone

from apps.events.models import (
    AccessStatus,
    Event,
    EventParticipation,
    EventRole,
    EventStatus,
)


def create_event(
    user,
    *,
    name,
    event_date,
    description=None,
    assignment_deadline_at=None,
) -> Event:
    """Create a new event and assign the user as owner participant."""
    with transaction.atomic():
        event = Event.objects.create(
            owner_user=user,
            name=name,
            event_date=event_date,
            description=description,
            assignment_deadline_at=assignment_deadline_at,
        )
        EventParticipation.objects.create(
            event=event,
            user=user,
            role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
    return event


def close_event(event) -> None:
    """Close an active event. Raises ValueError if cancelled."""
    if event.status == EventStatus.CANCELLED:
        raise ValueError("Cannot close a cancelled event.")
    event.status = EventStatus.CLOSED
    event.closed_at = timezone.now()
    event.save(update_fields=["status", "closed_at", "updated_at"])


def reopen_event(event) -> None:
    """Reopen a closed event. Raises ValueError if cancelled."""
    if event.status == EventStatus.CANCELLED:
        raise ValueError("Cannot reopen a cancelled event.")
    event.status = EventStatus.ACTIVE
    event.closed_at = None
    event.save(update_fields=["status", "closed_at", "updated_at"])


def cancel_event(event) -> None:
    """Cancel an event. Raises ValueError if already cancelled."""
    if event.status == EventStatus.CANCELLED:
        raise ValueError("Event is already cancelled.")
    event.status = EventStatus.CANCELLED
    event.cancelled_at = timezone.now()
    event.save(update_fields=["status", "cancelled_at", "updated_at"])


def promote_to_co_admin(participation) -> None:
    """Promote a participant to co-admin role."""
    participation.role = EventRole.CO_ADMIN
    participation.save(update_fields=["role", "updated_at"])


def demote_co_admin(participation) -> None:
    """Demote a co-admin back to participant role."""
    participation.role = EventRole.PARTICIPANT
    participation.save(update_fields=["role", "updated_at"])


def remove_participant(participation) -> None:
    """Remove a participant from an event.

    Raises ValueError if the participant has purchased item assignments.
    """
    from apps.items.models import ItemAssignment

    has_purchases = ItemAssignment.objects.filter(
        item__event=participation.event,
        user=participation.user,
        purchased_at__isnull=False,
        cancelled_at__isnull=True,
    ).exists()

    if has_purchases:
        raise ValueError("Cannot remove participant with purchased assignments.")

    participation.access_status = AccessStatus.REMOVED
    participation.removed_at = timezone.now()
    participation.save(update_fields=["access_status", "removed_at", "updated_at"])


def close_expired_events() -> int:
    """Bulk close active events past their assignment deadline.

    Returns the count of events closed.
    """
    now = timezone.now()
    count = Event.objects.filter(
        status=EventStatus.ACTIVE,
        assignment_deadline_at__lte=now,
    ).update(
        status=EventStatus.CLOSED,
        closed_at=now,
    )
    return count


# --- Phase 4: Event Access ---


def request_to_join(user, event) -> EventParticipation:
    """Request to join an event.

    Creates a new participation or resets a left/removed one to pending.
    Raises ValueError if the event is not active or user already has
    an active participation (pending, accepted, rejected).
    """
    if event.status != EventStatus.ACTIVE:
        raise ValueError("No es posible unirse a un evento cerrado o cancelado.")

    existing = EventParticipation.objects.filter(event=event, user=user).first()

    if existing:
        if existing.access_status in (AccessStatus.LEFT, AccessStatus.REMOVED):
            # Re-request: reset to pending
            existing.access_status = AccessStatus.PENDING
            existing.role = EventRole.PARTICIPANT
            existing.requested_at = timezone.now()
            existing.responded_at = None
            existing.left_at = None
            existing.removed_at = None
            existing.save(
                update_fields=[
                    "access_status",
                    "role",
                    "requested_at",
                    "responded_at",
                    "left_at",
                    "removed_at",
                    "updated_at",
                ]
            )
            return existing
        # Already pending, accepted, or rejected
        raise ValueError("Ya tenés una solicitud activa para este evento.")

    # New participation
    participation = EventParticipation.objects.create(
        event=event,
        user=user,
        role=EventRole.PARTICIPANT,
        access_status=AccessStatus.PENDING,
        requested_at=timezone.now(),
    )
    return participation


def approve_request(participation) -> None:
    """Approve a pending join request.

    Raises ValueError if participation is not pending.
    """
    if participation.access_status != AccessStatus.PENDING:
        raise ValueError("Solo se pueden aprobar solicitudes pendientes.")

    participation.access_status = AccessStatus.ACCEPTED
    participation.responded_at = timezone.now()
    participation.save(update_fields=["access_status", "responded_at", "updated_at"])


def reject_request(participation) -> None:
    """Reject a pending join request.

    Raises ValueError if participation is not pending.
    """
    if participation.access_status != AccessStatus.PENDING:
        raise ValueError("Solo se pueden rechazar solicitudes pendientes.")

    participation.access_status = AccessStatus.REJECTED
    participation.responded_at = timezone.now()
    participation.save(update_fields=["access_status", "responded_at", "updated_at"])


def correct_rejection(participation) -> None:
    """Correct a rejected request to accepted.

    Raises ValueError if participation is not rejected.
    """
    if participation.access_status != AccessStatus.REJECTED:
        raise ValueError("Solo se pueden corregir solicitudes rechazadas.")

    participation.access_status = AccessStatus.ACCEPTED
    participation.responded_at = timezone.now()
    participation.save(update_fields=["access_status", "responded_at", "updated_at"])


def leave_event(participation) -> None:
    """Leave an event voluntarily.

    Validates participant is accepted and not the owner. Blocks if
    the participant has purchased assignments. If co-admin, demotes
    role before leaving.

    Raises ValueError if owner, not accepted, or has purchased assignments.
    """
    if participation.role == EventRole.OWNER:
        raise ValueError("El organizador no puede abandonar su propio evento.")

    if participation.access_status != AccessStatus.ACCEPTED:
        raise ValueError("Solo participantes aceptados pueden abandonar el evento.")

    from apps.items.models import ItemAssignment

    has_purchases = ItemAssignment.objects.filter(
        item__event=participation.event,
        user=participation.user,
        purchased_at__isnull=False,
        cancelled_at__isnull=True,
    ).exists()

    if has_purchases:
        raise ValueError(
            "No podés abandonar el evento porque tenés compras registradas."
        )

    # Demote co-admin before leaving
    if participation.role == EventRole.CO_ADMIN:
        participation.role = EventRole.PARTICIPANT

    participation.access_status = AccessStatus.LEFT
    participation.left_at = timezone.now()
    participation.save(update_fields=["access_status", "role", "left_at", "updated_at"])
