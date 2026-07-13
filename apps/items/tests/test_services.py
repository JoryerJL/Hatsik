"""Tests for items service layer."""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import (
    AccessStatus,
    Event,
    EventParticipation,
    EventRole,
    EventStatus,
)
from apps.items.models import EventItem, ItemAssignment, ItemUnit
from apps.items.services import (
    STATUS_BOUGHT,
    STATUS_COVERED,
    STATUS_PARTIALLY_BOUGHT,
    STATUS_PARTIALLY_COVERED,
    STATUS_UNASSIGNED,
    ItemError,
    add_item,
    compute_item_status,
    delete_item,
    edit_item,
    get_computed_status_from_annotations,
    get_items_with_status,
)


class ItemServiceTestBase(TestCase):
    """Base class with common setup for item service tests."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            display_name="Owner",
        )
        self.participant = User.objects.create_user(
            email="participant@test.com",
            password="testpass123",
            display_name="Participant",
        )
        self.event = Event.objects.create(
            owner_user=self.owner,
            name="Test Event",
            event_date=timezone.now().date(),
            status=EventStatus.ACTIVE,
        )
        EventParticipation.objects.create(
            event=self.event,
            user=self.owner,
            role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
        EventParticipation.objects.create(
            event=self.event,
            user=self.participant,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )


class AddItemTests(ItemServiceTestBase):
    """Tests for add_item service function."""

    def test_add_item_quantified_happy_path(self):
        """Owner can add a quantified item to an active event."""
        item = add_item(
            self.event,
            self.owner,
            name="Coca-Cola",
            quantity_total=Decimal("6"),
            unit=ItemUnit.BOTTLES,
        )
        self.assertEqual(item.name, "Coca-Cola")
        self.assertEqual(item.quantity_total, Decimal("6"))
        self.assertEqual(item.unit, ItemUnit.BOTTLES)
        self.assertEqual(item.event, self.event)
        self.assertEqual(item.created_by_user, self.owner)

    def test_add_item_binary_happy_path(self):
        """Owner can add a binary item (no quantity/unit)."""
        item = add_item(
            self.event,
            self.owner,
            name="Mantel",
        )
        self.assertEqual(item.name, "Mantel")
        self.assertIsNone(item.quantity_total)
        self.assertIsNone(item.unit)

    def test_add_item_blocked_on_closed_event(self):
        """Cannot add items to a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()

        with self.assertRaises(ItemError) as ctx:
            add_item(self.event, self.owner, name="Hielo")

        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_add_item_blocked_on_cancelled_event(self):
        """Cannot add items to a cancelled event."""
        self.event.status = EventStatus.CANCELLED
        self.event.save()

        with self.assertRaises(ItemError) as ctx:
            add_item(self.event, self.owner, name="Hielo")

        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_add_item_blocked_for_non_owner(self):
        """Non-owner cannot add items."""
        with self.assertRaises(ItemError) as ctx:
            add_item(self.event, self.participant, name="Hielo")

        self.assertIn("organizador", str(ctx.exception))

    def test_add_item_quantity_without_unit_fails(self):
        """Cannot add item with quantity but no unit."""
        with self.assertRaises(ItemError) as ctx:
            add_item(
                self.event,
                self.owner,
                name="Carne",
                quantity_total=Decimal("5"),
            )

        self.assertIn("unidad es obligatoria", str(ctx.exception))

    def test_add_item_quantity_zero_or_negative_fails(self):
        """Cannot add item with quantity <= 0."""
        with self.assertRaises(ItemError):
            add_item(
                self.event,
                self.owner,
                name="Carne",
                quantity_total=Decimal("0"),
                unit=ItemUnit.KG,
            )

        with self.assertRaises(ItemError):
            add_item(
                self.event,
                self.owner,
                name="Carne",
                quantity_total=Decimal("-1"),
                unit=ItemUnit.KG,
            )


class EditItemTests(ItemServiceTestBase):
    """Tests for edit_item service function."""

    def setUp(self):
        super().setUp()
        self.item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )

    def test_edit_item_no_assignments_all_fields(self):
        """When no assignments, all fields can be edited."""
        result = edit_item(
            self.item,
            self.owner,
            name="Pollo",
            quantity_total=Decimal("3"),
            unit=ItemUnit.PIECES,
        )
        result.refresh_from_db()
        self.assertEqual(result.name, "Pollo")
        self.assertEqual(result.quantity_total, Decimal("3"))
        self.assertEqual(result.unit, ItemUnit.PIECES)

    def test_edit_item_with_assignments_only_quantity(self):
        """When item has assignments, only quantity_total can be changed."""
        # Create an active assignment
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("2"),
        )

        result = edit_item(
            self.item,
            self.owner,
            name="Should Be Ignored",
            quantity_total=Decimal("8"),
            unit=ItemUnit.G,  # Should be ignored
        )
        result.refresh_from_db()
        # Name and unit should NOT change
        self.assertEqual(result.name, "Carne")
        self.assertEqual(result.unit, ItemUnit.KG)
        # Quantity should change
        self.assertEqual(result.quantity_total, Decimal("8"))

    def test_edit_item_cannot_reduce_below_assigned(self):
        """Cannot reduce quantity below sum of active assignments."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("3"),
        )

        with self.assertRaises(ItemError) as ctx:
            edit_item(self.item, self.owner, quantity_total=Decimal("2"))

        self.assertIn("por debajo de lo asignado", str(ctx.exception))

    def test_edit_item_can_reduce_to_assigned_sum(self):
        """Can reduce quantity to exactly the assigned sum."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("3"),
        )

        result = edit_item(self.item, self.owner, quantity_total=Decimal("3"))
        result.refresh_from_db()
        self.assertEqual(result.quantity_total, Decimal("3"))

    def test_edit_item_cancelled_assignments_ignored(self):
        """Cancelled assignments don't count toward the assigned sum."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("4"),
            cancelled_at=timezone.now(),
        )

        # Should succeed because the assignment is cancelled
        result = edit_item(self.item, self.owner, quantity_total=Decimal("1"))
        result.refresh_from_db()
        self.assertEqual(result.quantity_total, Decimal("1"))

    def test_edit_item_blocked_on_closed_event(self):
        """Cannot edit items in a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()

        with self.assertRaises(ItemError):
            edit_item(self.item, self.owner, name="Nuevo")

    def test_edit_item_blocked_for_non_owner(self):
        """Non-owner cannot edit items."""
        with self.assertRaises(ItemError):
            edit_item(self.item, self.participant, name="Nuevo")


class DeleteItemTests(ItemServiceTestBase):
    """Tests for delete_item service function."""

    def setUp(self):
        super().setUp()
        self.item = EventItem.objects.create(
            event=self.event,
            name="Hielo",
            quantity_total=Decimal("10"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )

    def test_delete_item_happy_path(self):
        """Owner can delete an item."""
        item_pk = self.item.pk
        delete_item(self.item, self.owner)
        self.assertFalse(EventItem.objects.filter(pk=item_pk).exists())

    def test_delete_item_cascades_assignments(self):
        """Deleting an item also deletes its assignments."""
        assignment = ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("5"),
        )
        assignment_pk = assignment.pk

        delete_item(self.item, self.owner)
        self.assertFalse(ItemAssignment.objects.filter(pk=assignment_pk).exists())

    def test_delete_item_blocked_on_closed_event(self):
        """Cannot delete items in a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()

        with self.assertRaises(ItemError):
            delete_item(self.item, self.owner)

    def test_delete_item_blocked_on_cancelled_event(self):
        """Cannot delete items in a cancelled event."""
        self.event.status = EventStatus.CANCELLED
        self.event.save()

        with self.assertRaises(ItemError):
            delete_item(self.item, self.owner)

    def test_delete_item_blocked_for_non_owner(self):
        """Non-owner cannot delete items."""
        with self.assertRaises(ItemError):
            delete_item(self.item, self.participant)


class ComputeItemStatusTests(ItemServiceTestBase):
    """Tests for compute_item_status function."""

    def test_no_assignments_returns_unassigned(self):
        """Item with no assignments has status sin_asignar."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        self.assertEqual(compute_item_status(item), STATUS_UNASSIGNED)

    def test_partially_covered(self):
        """Item with assignments below total is parcialmente_cubierto."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("3"),
        )
        self.assertEqual(compute_item_status(item), STATUS_PARTIALLY_COVERED)

    def test_fully_covered(self):
        """Item with assignments equal to total is cubierto."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("5"),
        )
        self.assertEqual(compute_item_status(item), STATUS_COVERED)

    def test_partially_bought(self):
        """Item with some but not all purchased is parcialmente_comprado."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        other_user = User.objects.create_user(
            email="other@test.com", password="testpass123", display_name="Other"
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("3"),
            purchased_at=timezone.now(),
            purchased_by_user=self.participant,
        )
        ItemAssignment.objects.create(
            item=item,
            user=other_user,
            quantity_assigned=Decimal("2"),
        )
        self.assertEqual(compute_item_status(item), STATUS_PARTIALLY_BOUGHT)

    def test_all_bought(self):
        """Item with all assignments purchased is comprado."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("5"),
            purchased_at=timezone.now(),
            purchased_by_user=self.participant,
        )
        self.assertEqual(compute_item_status(item), STATUS_BOUGHT)

    def test_binary_item_unassigned(self):
        """Binary item with no assignments is sin_asignar."""
        item = EventItem.objects.create(
            event=self.event,
            name="Mantel",
            created_by_user=self.owner,
        )
        self.assertEqual(compute_item_status(item), STATUS_UNASSIGNED)

    def test_binary_item_covered(self):
        """Binary item with an assignment is cubierto."""
        item = EventItem.objects.create(
            event=self.event,
            name="Mantel",
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
        )
        self.assertEqual(compute_item_status(item), STATUS_COVERED)

    def test_binary_item_bought(self):
        """Binary item with purchased assignment is comprado."""
        item = EventItem.objects.create(
            event=self.event,
            name="Mantel",
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            purchased_at=timezone.now(),
            purchased_by_user=self.participant,
        )
        self.assertEqual(compute_item_status(item), STATUS_BOUGHT)

    def test_cancelled_assignments_ignored(self):
        """Cancelled assignments are not counted for status computation."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("5"),
            cancelled_at=timezone.now(),
        )
        self.assertEqual(compute_item_status(item), STATUS_UNASSIGNED)


class GetItemsWithStatusTests(ItemServiceTestBase):
    """Tests for get_items_with_status and get_computed_status_from_annotations."""

    def test_annotated_queryset_returns_correct_status(self):
        """Annotated queryset + helper gives same result as compute_item_status."""
        item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item,
            user=self.participant,
            quantity_assigned=Decimal("3"),
        )

        items = get_items_with_status(self.event)
        annotated_item = items.get(pk=item.pk)
        status = get_computed_status_from_annotations(annotated_item)

        self.assertEqual(status, STATUS_PARTIALLY_COVERED)
        # Should match the per-item computation
        self.assertEqual(status, compute_item_status(item))

    def test_annotated_queryset_multiple_items(self):
        """Annotated queryset handles multiple items correctly."""
        item1 = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        item2 = EventItem.objects.create(
            event=self.event,
            name="Mantel",
            created_by_user=self.owner,
        )
        ItemAssignment.objects.create(
            item=item1,
            user=self.participant,
            quantity_assigned=Decimal("5"),
        )

        items = get_items_with_status(self.event)
        status1 = get_computed_status_from_annotations(items.get(pk=item1.pk))
        status2 = get_computed_status_from_annotations(items.get(pk=item2.pk))

        self.assertEqual(status1, STATUS_COVERED)
        self.assertEqual(status2, STATUS_UNASSIGNED)

    def test_annotated_queryset_ordered_by_created_at(self):
        """Items are ordered by created_at."""
        item1 = EventItem.objects.create(
            event=self.event,
            name="First",
            created_by_user=self.owner,
        )
        item2 = EventItem.objects.create(
            event=self.event,
            name="Second",
            created_by_user=self.owner,
        )

        items = list(get_items_with_status(self.event))
        self.assertEqual(items[0].pk, item1.pk)
        self.assertEqual(items[1].pk, item2.pk)
