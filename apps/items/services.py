"""Business logic for event item operations."""

from decimal import Decimal

from django.db.models import Count, Q, Sum

from apps.events.models import EventStatus
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
