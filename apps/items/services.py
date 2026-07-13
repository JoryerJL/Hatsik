"""Business logic for event item operations."""

from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.events.models import AccessStatus, EventParticipation, EventStatus
from apps.items.models import EventItem, ItemAssignment


class ItemError(Exception):
    """Domain error for item operations."""

    pass


def add_item(event, user, *, name, quantity_total=None, unit=None) -> EventItem:
    """Add an item to an event's shopping list.

    Args:
        event: The event to add the item to.
        user: The user performing the action (must be event owner).
        name: Item name (required).
        quantity_total: Total quantity needed (optional, None = binary item).
        unit: Unit of measurement (required if quantity_total is set).

    Returns:
        The created EventItem.

    Raises:
        ItemError: If event is not active or user is not the owner.
    """
    if event.status != EventStatus.ACTIVE:
        raise ItemError("No se pueden agregar ítems a un evento cerrado o cancelado.")

    if event.owner_user != user:
        raise ItemError("Solo el organizador puede agregar ítems.")

    if quantity_total is not None and not unit:
        raise ItemError("La unidad es obligatoria cuando se especifica cantidad.")

    if quantity_total is not None and quantity_total <= 0:
        raise ItemError("La cantidad debe ser mayor a cero.")

    return EventItem.objects.create(
        event=event,
        name=name,
        quantity_total=quantity_total,
        unit=unit,
        created_by_user=user,
    )


def edit_item(item, user, *, name=None, quantity_total=None, unit=None) -> EventItem:
    """Edit an existing item.

    If the item has active assignments, only quantity_total can be edited.
    Cannot reduce quantity below sum of active assignments.

    Args:
        item: The EventItem to edit.
        user: The user performing the action (must be event owner).
        name: New name (ignored if item has assignments).
        quantity_total: New total quantity.
        unit: New unit (ignored if item has assignments).

    Returns:
        The updated EventItem.

    Raises:
        ItemError: If validation fails.
    """
    event = item.event

    if event.status != EventStatus.ACTIVE:
        raise ItemError("No se pueden editar ítems de un evento cerrado o cancelado.")

    if event.owner_user != user:
        raise ItemError("Solo el organizador puede editar ítems.")

    has_assignments = _has_active_assignments(item)

    if has_assignments:
        # Only quantity_total can be changed
        if quantity_total is not None:
            assigned_sum = _get_assigned_sum(item)
            if quantity_total < assigned_sum:
                raise ItemError(
                    f"No se puede reducir la cantidad por debajo de lo asignado ({assigned_sum})."
                )
            item.quantity_total = quantity_total
            item.save(update_fields=["quantity_total", "updated_at"])
    else:
        # All fields editable
        if name is not None:
            item.name = name
        if quantity_total is not None:
            if quantity_total <= 0:
                raise ItemError("La cantidad debe ser mayor a cero.")
            item.quantity_total = quantity_total
        elif quantity_total is None and "quantity_total" in (name, unit):
            # This branch handles explicit None to clear quantity
            pass

        if unit is not None:
            item.unit = unit

        # Validate unit required if quantity set
        if item.quantity_total is not None and not item.unit:
            raise ItemError("La unidad es obligatoria cuando se especifica cantidad.")

        item.save(update_fields=["name", "quantity_total", "unit", "updated_at"])

    return item


def delete_item(item, user) -> None:
    """Delete an item and all its assignments.

    Args:
        item: The EventItem to delete.
        user: The user performing the action (must be event owner).

    Raises:
        ItemError: If event is not active or user is not the owner.
    """
    event = item.event

    if event.status != EventStatus.ACTIVE:
        raise ItemError("No se pueden eliminar ítems de un evento cerrado o cancelado.")

    if event.owner_user != user:
        raise ItemError("Solo el organizador puede eliminar ítems.")

    item.delete()


# --- Status Computation ---

# Status constants
STATUS_UNASSIGNED = "sin_asignar"
STATUS_PARTIALLY_COVERED = "parcialmente_cubierto"
STATUS_COVERED = "cubierto"
STATUS_PARTIALLY_BOUGHT = "parcialmente_comprado"
STATUS_BOUGHT = "comprado"

# Color tokens for template rendering
STATUS_COLORS = {
    STATUS_UNASSIGNED: "#FCA5A5",
    STATUS_PARTIALLY_COVERED: "#FDBA74",
    STATUS_COVERED: "#86EFAC",
    STATUS_PARTIALLY_BOUGHT: "#93C5FD",
    STATUS_BOUGHT: "#4ADE80",
}

STATUS_LABELS = {
    STATUS_UNASSIGNED: "Sin asignar",
    STATUS_PARTIALLY_COVERED: "Parcialmente cubierto",
    STATUS_COVERED: "Cubierto",
    STATUS_PARTIALLY_BOUGHT: "Parcialmente comprado",
    STATUS_BOUGHT: "Comprado",
}


def compute_item_status(item) -> str:
    """Compute the status of an item based on its assignments.

    This is a pure computation function — does not write to DB.

    For quantified items:
        - No active assignments → sin_asignar
        - Sum < quantity_total → parcialmente_cubierto
        - Sum = quantity_total → cubierto
        - Some purchased → parcialmente_comprado
        - All purchased → comprado

    For binary items (no quantity):
        - No active assignments → sin_asignar
        - Has assignment(s) → cubierto
        - All assignments purchased → comprado

    Returns:
        Status string constant.
    """
    active_assignments = item.assignments.filter(cancelled_at__isnull=True)

    if not active_assignments.exists():
        return STATUS_UNASSIGNED

    total_active = active_assignments.count()
    purchased_count = active_assignments.filter(purchased_at__isnull=False).count()

    # Check purchased states first
    if purchased_count == total_active:
        return STATUS_BOUGHT

    if purchased_count > 0:
        return STATUS_PARTIALLY_BOUGHT

    # Not purchased — check coverage
    if item.quantity_total is None:
        # Binary item: has assignment = covered
        return STATUS_COVERED

    # Quantified item: compare assigned sum to total
    assigned_sum = active_assignments.aggregate(total=Sum("quantity_assigned"))[
        "total"
    ] or Decimal("0")

    if assigned_sum >= item.quantity_total:
        return STATUS_COVERED

    return STATUS_PARTIALLY_COVERED


def get_items_with_status(event):
    """Get all items for an event with computed status annotations.

    Uses DB-level annotations to avoid N+1 queries. Returns a queryset
    where each item has:
        - active_assigned_sum: Sum of active assignment quantities
        - total_active_assignments: Count of active assignments
        - purchased_count: Count of purchased active assignments

    The template or view layer uses these to determine the display status.
    """
    return (
        event.items.annotate(
            active_assigned_sum=Sum(
                "assignments__quantity_assigned",
                filter=Q(assignments__cancelled_at__isnull=True),
                default=Decimal("0"),
            ),
            total_active_assignments=Count(
                "assignments",
                filter=Q(assignments__cancelled_at__isnull=True),
            ),
            purchased_count=Count(
                "assignments",
                filter=Q(
                    assignments__cancelled_at__isnull=True,
                    assignments__purchased_at__isnull=False,
                ),
            ),
        )
        .select_related("created_by_user")
        .order_by("created_at")
    )


def get_computed_status_from_annotations(item) -> str:
    """Derive status string from pre-annotated queryset item.

    Use this after calling get_items_with_status() to avoid
    extra queries per item.
    """
    total_active = getattr(item, "total_active_assignments", 0)
    purchased_count = getattr(item, "purchased_count", 0)
    active_sum = getattr(item, "active_assigned_sum", Decimal("0"))

    if total_active == 0:
        return STATUS_UNASSIGNED

    if purchased_count == total_active:
        return STATUS_BOUGHT

    if purchased_count > 0:
        return STATUS_PARTIALLY_BOUGHT

    # Not purchased — check coverage
    if item.quantity_total is None:
        return STATUS_COVERED

    if active_sum >= item.quantity_total:
        return STATUS_COVERED

    return STATUS_PARTIALLY_COVERED


# --- Private helpers ---


def _has_active_assignments(item) -> bool:
    """Check if an item has any non-cancelled assignments."""
    return ItemAssignment.objects.filter(item=item, cancelled_at__isnull=True).exists()


def _get_assigned_sum(item) -> Decimal:
    """Get the sum of active assignment quantities for an item."""
    result = ItemAssignment.objects.filter(
        item=item, cancelled_at__isnull=True
    ).aggregate(total=Sum("quantity_assigned"))
    return result["total"] or Decimal("0")


# --- Assignment Operations ---

# Allowed actions per event status
_ALLOWED_ACTIONS = {
    EventStatus.ACTIVE: {"claim", "modify", "cancel", "purchase"},
    EventStatus.CLOSED: {"purchase"},
    EventStatus.CANCELLED: set(),
}


def _check_event_allows_action(event, action: str) -> None:
    """Raise ItemError if event status blocks the action.

    Args:
        event: The event to check.
        action: One of "claim", "modify", "cancel", "purchase".

    Raises:
        ItemError: With a user-facing Spanish message.
    """
    allowed = _ALLOWED_ACTIONS.get(event.status, set())
    if action not in allowed:
        messages = {
            "claim": "No se pueden tomar ítems en un evento cerrado o cancelado.",
            "modify": "No se pueden modificar asignaciones en un evento cerrado o cancelado.",
            "cancel": "No se pueden cancelar asignaciones en un evento cerrado o cancelado.",
            "purchase": "No se pueden marcar compras en un evento cancelado.",
        }
        raise ItemError(messages.get(action, "Acción no permitida."))


def _check_user_is_participant(event, user) -> None:
    """Raise ItemError if user is not an accepted participant."""
    exists = EventParticipation.objects.filter(
        event=event, user=user, access_status=AccessStatus.ACCEPTED
    ).exists()
    if not exists:
        raise ItemError(
            "Solo los participantes confirmados pueden realizar esta acción."
        )


def get_available_quantity(item) -> Decimal | None:
    """Return the remaining claimable quantity for an item.

    Returns None for binary items (no quantity concept).
    For quantified items, returns quantity_total - sum of active assignments.
    """
    if item.quantity_total is None:
        return None

    assigned = _get_assigned_sum(item)
    return item.quantity_total - assigned


def claim_item(item, user, *, quantity_assigned=None) -> ItemAssignment:
    """Claim an item (or a portion of it) for a participant.

    Args:
        item: The EventItem to claim.
        user: The participant claiming the item.
        quantity_assigned: Amount to claim (required for quantified items, None for binary).

    Returns:
        The created ItemAssignment.

    Raises:
        ItemError: If validation fails.
    """
    event = item.event
    _check_event_allows_action(event, "claim")
    _check_user_is_participant(event, user)

    # Check for existing active assignment (redundant with DB constraint but better UX)
    if ItemAssignment.objects.filter(
        item=item, user=user, cancelled_at__isnull=True
    ).exists():
        raise ItemError("Ya tenés una asignación activa para este ítem.")

    if item.quantity_total is not None:
        # Quantified item
        if quantity_assigned is None or quantity_assigned <= 0:
            raise ItemError("La cantidad debe ser mayor a cero.")

        with transaction.atomic():
            # Lock item row to prevent race condition
            locked_item = EventItem.objects.select_for_update().get(pk=item.pk)
            available = get_available_quantity(locked_item)
            if quantity_assigned > available:
                raise ItemError(
                    f"Cantidad no disponible. Máximo: {available} {locked_item.unit}."
                )

            return ItemAssignment.objects.create(
                item=locked_item,
                user=user,
                quantity_assigned=quantity_assigned,
            )
    else:
        # Binary item
        if quantity_assigned is not None:
            raise ItemError("Los ítems binarios no tienen cantidad.")

        # Check if item is already fully covered (has any active assignment)
        if ItemAssignment.objects.filter(item=item, cancelled_at__isnull=True).exists():
            raise ItemError("Este ítem ya fue tomado por otro participante.")

        return ItemAssignment.objects.create(
            item=item,
            user=user,
            quantity_assigned=None,
        )


def modify_assignment(assignment, user, *, quantity_assigned) -> ItemAssignment:
    """Modify the quantity of an existing assignment.

    Args:
        assignment: The ItemAssignment to modify.
        user: The user performing the modification (must be the assignee).
        quantity_assigned: New quantity.

    Returns:
        The updated ItemAssignment.

    Raises:
        ItemError: If validation fails.
    """
    item = assignment.item
    event = item.event
    _check_event_allows_action(event, "modify")

    if assignment.user != user:
        raise ItemError("Solo podés modificar tus propias asignaciones.")

    if assignment.purchased_at is not None:
        raise ItemError("No se puede modificar una asignación ya comprada.")

    if assignment.cancelled_at is not None:
        raise ItemError("No se puede modificar una asignación cancelada.")

    if item.quantity_total is None:
        raise ItemError("Los ítems binarios no tienen cantidad para modificar.")

    if quantity_assigned is None or quantity_assigned <= 0:
        raise ItemError("La cantidad debe ser mayor a cero.")

    with transaction.atomic():
        locked_item = EventItem.objects.select_for_update().get(pk=item.pk)
        # Available = total - other active assignments (excluding current)
        others_sum = ItemAssignment.objects.filter(
            item=locked_item, cancelled_at__isnull=True
        ).exclude(pk=assignment.pk).aggregate(total=Sum("quantity_assigned"))[
            "total"
        ] or Decimal("0")
        available = locked_item.quantity_total - others_sum
        if quantity_assigned > available:
            raise ItemError(
                f"Cantidad no disponible. Máximo: {available} {locked_item.unit}."
            )

        assignment.quantity_assigned = quantity_assigned
        assignment.save(update_fields=["quantity_assigned", "updated_at"])

    return assignment


def cancel_assignment(assignment, user) -> ItemAssignment:
    """Cancel an assignment (own or owner cancels others).

    Args:
        assignment: The ItemAssignment to cancel.
        user: The user performing the cancellation.

    Returns:
        The updated ItemAssignment.

    Raises:
        ItemError: If validation fails.
    """
    item = assignment.item
    event = item.event
    _check_event_allows_action(event, "cancel")

    if assignment.purchased_at is not None:
        raise ItemError("No se puede cancelar una asignación ya comprada.")

    if assignment.cancelled_at is not None:
        raise ItemError("Esta asignación ya fue cancelada.")

    # Permission: own assignment OR event owner
    is_own = assignment.user == user
    is_owner = event.owner_user == user
    if not is_own and not is_owner:
        raise ItemError("No tenés permiso para cancelar esta asignación.")

    assignment.cancelled_at = timezone.now()
    assignment.cancelled_by_user = user
    assignment.save(update_fields=["cancelled_at", "cancelled_by_user", "updated_at"])
    return assignment


def mark_as_purchased(assignment, user) -> ItemAssignment:
    """Mark an assignment as purchased.

    Args:
        assignment: The ItemAssignment to mark.
        user: The user marking it (assignee, owner, or co-admin).

    Returns:
        The updated ItemAssignment.

    Raises:
        ItemError: If validation fails.
    """
    item = assignment.item
    event = item.event
    _check_event_allows_action(event, "purchase")

    if assignment.purchased_at is not None:
        raise ItemError("Esta asignación ya fue marcada como comprada.")

    if assignment.cancelled_at is not None:
        raise ItemError("No se puede marcar como comprada una asignación cancelada.")

    # Permission: own assignment OR event admin (owner/co-admin)
    is_own = assignment.user == user
    is_admin = EventParticipation.objects.filter(
        event=event,
        user=user,
        access_status=AccessStatus.ACCEPTED,
        role__in=["owner", "co_admin"],
    ).exists()

    if not is_own and not is_admin:
        raise ItemError("No tenés permiso para marcar esta asignación como comprada.")

    assignment.purchased_at = timezone.now()
    assignment.purchased_by_user = user
    assignment.save(update_fields=["purchased_at", "purchased_by_user", "updated_at"])
    return assignment


def compute_event_progress(event) -> dict:
    """Compute overall event progress based on item coverage.

    Returns dict with:
        - percentage: int (0-100)
        - covered: number of items with status >= cubierto
        - total: total item count
    """
    items = get_items_with_status(event)
    total = items.count()
    if total == 0:
        return {"percentage": 0, "covered": 0, "total": total}

    covered = 0
    for item in items:
        status = get_computed_status_from_annotations(item)
        if status in (STATUS_COVERED, STATUS_PARTIALLY_BOUGHT, STATUS_BOUGHT):
            covered += 1

    percentage = int((covered / total) * 100)
    return {"percentage": percentage, "covered": covered, "total": total}
