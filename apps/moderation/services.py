"""Business logic for item suggestion moderation."""

from django.db import transaction
from django.utils import timezone

from apps.events.models import AccessStatus, EventParticipation, EventRole, EventStatus
from apps.items.models import EventItem
from apps.moderation.models import ItemSuggestion, SuggestionStatus


class ModerationError(Exception):
    """Domain error for moderation operations."""

    pass


def suggest_item(event, user, *, name, quantity_total=None, unit=None) -> ItemSuggestion:
    """Create a new item suggestion for an event.

    Args:
        event: The event to suggest the item for.
        user: The user making the suggestion (must be accepted participant).
        name: Suggested item name (required).
        quantity_total: Suggested quantity (optional).
        unit: Suggested unit (required if quantity_total is set).

    Returns:
        The created ItemSuggestion.

    Raises:
        ModerationError: If validation fails.
    """
    if event.status != EventStatus.ACTIVE:
        raise ModerationError(
            "No se pueden sugerir ítems en un evento cerrado o cancelado."
        )

    _validate_accepted_participant(event, user)

    if quantity_total is not None and quantity_total <= 0:
        raise ModerationError("La cantidad debe ser mayor a cero.")

    if quantity_total is not None and not unit:
        raise ModerationError("La unidad es obligatoria cuando se especifica cantidad.")

    return ItemSuggestion.objects.create(
        event=event,
        suggested_by_user=user,
        name=name,
        quantity_total=quantity_total,
        unit=unit,
        status=SuggestionStatus.PENDING_APPROVAL,
    )


def edit_suggestion(
    suggestion, user, *, name=None, quantity_total=None, unit=None
) -> ItemSuggestion:
    """Edit an own pending suggestion.

    Args:
        suggestion: The ItemSuggestion to edit.
        user: The user performing the edit (must be the suggester).
        name: New name (optional, keeps current if None).
        quantity_total: New quantity (optional).
        unit: New unit (optional).

    Returns:
        The updated ItemSuggestion.

    Raises:
        ModerationError: If validation fails.
    """
    if suggestion.suggested_by_user != user:
        raise ModerationError("Solo podés editar tus propias sugerencias.")

    if suggestion.status != SuggestionStatus.PENDING_APPROVAL:
        raise ModerationError("Solo se pueden editar sugerencias pendientes.")

    if suggestion.event.status != EventStatus.ACTIVE:
        raise ModerationError(
            "No se pueden editar sugerencias en un evento cerrado o cancelado."
        )

    if name is not None:
        suggestion.name = name

    if quantity_total is not None:
        if quantity_total <= 0:
            raise ModerationError("La cantidad debe ser mayor a cero.")
        suggestion.quantity_total = quantity_total
    elif quantity_total is None and unit is None and name is not None:
        # Only name changed — keep existing quantity/unit
        pass

    if unit is not None:
        suggestion.unit = unit

    # Validate consistency
    if suggestion.quantity_total is not None and not suggestion.unit:
        raise ModerationError("La unidad es obligatoria cuando se especifica cantidad.")

    suggestion.save(
        update_fields=["name", "quantity_total", "unit", "updated_at"]
    )
    return suggestion


def delete_suggestion(suggestion, user) -> None:
    """Delete an own pending suggestion.

    Args:
        suggestion: The ItemSuggestion to delete.
        user: The user performing the delete (must be the suggester).

    Raises:
        ModerationError: If validation fails.
    """
    if suggestion.suggested_by_user != user:
        raise ModerationError("Solo podés eliminar tus propias sugerencias.")

    if suggestion.status != SuggestionStatus.PENDING_APPROVAL:
        raise ModerationError("Solo se pueden eliminar sugerencias pendientes.")

    suggestion.delete()


def approve_suggestion(
    suggestion, user, *, name=None, quantity_total=None, unit=None
) -> EventItem:
    """Approve a pending suggestion and create an official item.

    Owner/Co-admin can optionally override the name, quantity, and unit
    before approval.

    Args:
        suggestion: The ItemSuggestion to approve.
        user: The user approving (must be owner or co-admin).
        name: Override name (optional, uses suggestion name if None).
        quantity_total: Override quantity (optional).
        unit: Override unit (optional).

    Returns:
        The created EventItem.

    Raises:
        ModerationError: If validation fails.
    """
    if suggestion.status != SuggestionStatus.PENDING_APPROVAL:
        raise ModerationError("Solo se pueden aprobar sugerencias pendientes.")

    _validate_admin(suggestion.event, user)

    # Determine final values (override or suggestion original)
    final_name = name if name is not None else suggestion.name
    final_quantity = quantity_total if quantity_total is not None else suggestion.quantity_total
    final_unit = unit if unit is not None else suggestion.unit

    # Validate consistency
    if final_quantity is not None and not final_unit:
        raise ModerationError("La unidad es obligatoria cuando se especifica cantidad.")

    if final_quantity is not None and final_quantity <= 0:
        raise ModerationError("La cantidad debe ser mayor a cero.")

    with transaction.atomic():
        # Create official item
        item = EventItem.objects.create(
            event=suggestion.event,
            name=final_name,
            quantity_total=final_quantity,
            unit=final_unit,
            created_by_user=user,
            source_suggestion=suggestion,
        )

        # Update suggestion status
        suggestion.status = SuggestionStatus.APPROVED
        suggestion.reviewed_by_user = user
        suggestion.reviewed_at = timezone.now()
        suggestion.converted_event_item = item
        suggestion.save(
            update_fields=[
                "status",
                "reviewed_by_user",
                "reviewed_at",
                "converted_event_item",
                "updated_at",
            ]
        )

    return item


def reject_suggestion(suggestion, user, *, rejection_note=None) -> ItemSuggestion:
    """Reject a pending suggestion with an optional note.

    Args:
        suggestion: The ItemSuggestion to reject.
        user: The user rejecting (must be owner or co-admin).
        rejection_note: Optional reason for rejection.

    Returns:
        The updated ItemSuggestion.

    Raises:
        ModerationError: If validation fails.
    """
    if suggestion.status != SuggestionStatus.PENDING_APPROVAL:
        raise ModerationError("Solo se pueden rechazar sugerencias pendientes.")

    _validate_admin(suggestion.event, user)

    suggestion.status = SuggestionStatus.REJECTED
    suggestion.reviewed_by_user = user
    suggestion.reviewed_at = timezone.now()
    suggestion.rejection_note = rejection_note or ""
    suggestion.save(
        update_fields=[
            "status",
            "reviewed_by_user",
            "reviewed_at",
            "rejection_note",
            "updated_at",
        ]
    )
    return suggestion


def get_pending_suggestions(event):
    """Get all pending suggestions for an event (for admin view)."""
    return (
        ItemSuggestion.objects.filter(
            event=event, status=SuggestionStatus.PENDING_APPROVAL
        )
        .select_related("suggested_by_user")
        .order_by("created_at")
    )


def get_user_suggestions(event, user):
    """Get all suggestions by a specific user for an event."""
    return (
        ItemSuggestion.objects.filter(event=event, suggested_by_user=user)
        .select_related("reviewed_by_user")
        .order_by("-created_at")
    )


# --- Private helpers ---


def _validate_accepted_participant(event, user) -> None:
    """Validate that user is an accepted participant of the event."""
    is_participant = EventParticipation.objects.filter(
        event=event,
        user=user,
        access_status=AccessStatus.ACCEPTED,
    ).exists()

    if not is_participant:
        raise ModerationError(
            "Solo los participantes aceptados pueden sugerir ítems."
        )


def _validate_admin(event, user) -> None:
    """Validate that user is the event owner or an accepted co-admin."""
    if event.owner_user == user:
        return

    is_co_admin = EventParticipation.objects.filter(
        event=event,
        user=user,
        role=EventRole.CO_ADMIN,
        access_status=AccessStatus.ACCEPTED,
    ).exists()

    if not is_co_admin:
        raise ModerationError(
            "Solo el organizador o co-admins pueden moderar sugerencias."
        )
