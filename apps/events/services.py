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
