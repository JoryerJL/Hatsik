"""Tests for assignment operations (Phase 6)."""

from decimal import Decimal

from django.test import TestCase, override_settings
from django.urls import reverse
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
    ItemError,
    cancel_assignment,
    claim_item,
    compute_event_progress,
    get_available_quantity,
    mark_as_purchased,
    modify_assignment,
)


class AssignmentServiceTestBase(TestCase):
    """Base class with common setup for assignment tests."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            display_name="Owner",
        )
        self.owner.email_verified_at = timezone.now()
        self.owner.save()

        self.participant = User.objects.create_user(
            email="participant@test.com",
            password="testpass123",
            display_name="Participant",
        )
        self.participant.email_verified_at = timezone.now()
        self.participant.save()

        self.co_admin = User.objects.create_user(
            email="coadmin@test.com",
            password="testpass123",
            display_name="CoAdmin",
        )
        self.co_admin.email_verified_at = timezone.now()
        self.co_admin.save()

        self.outsider = User.objects.create_user(
            email="outsider@test.com",
            password="testpass123",
            display_name="Outsider",
        )
        self.outsider.email_verified_at = timezone.now()
        self.outsider.save()
        self.event = Event.objects.create(
            owner_user=self.owner,
            name="Test Event",
            event_date=timezone.now().date(),
            status=EventStatus.ACTIVE,
        )
        # Owner participation
        EventParticipation.objects.create(
            event=self.event,
            user=self.owner,
            role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
        # Participant participation
        EventParticipation.objects.create(
            event=self.event,
            user=self.participant,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        # Co-admin participation
        EventParticipation.objects.create(
            event=self.event,
            user=self.co_admin,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        # Quantified item
        self.q_item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5.00"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )
        # Binary item
        self.b_item = EventItem.objects.create(
            event=self.event,
            name="Mantel",
            quantity_total=None,
            unit=None,
            created_by_user=self.owner,
        )


class TestClaimItem(AssignmentServiceTestBase):
    """Tests for claim_item service function."""

    def test_claim_quantified_item_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.assertEqual(assignment.item, self.q_item)
        self.assertEqual(assignment.user, self.participant)
        self.assertEqual(assignment.quantity_assigned, Decimal("2.00"))
        self.assertIsNone(assignment.cancelled_at)

    def test_claim_binary_item_success(self):
        assignment = claim_item(self.b_item, self.participant)
        self.assertEqual(assignment.item, self.b_item)
        self.assertEqual(assignment.user, self.participant)
        self.assertIsNone(assignment.quantity_assigned)

    def test_claim_exceeds_available_blocked(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("4.00"))
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.owner, quantity_assigned=Decimal("2.00"))
        self.assertIn("Cantidad no disponible", str(ctx.exception))

    def test_claim_exact_max_succeeds(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("3.00"))
        assignment = claim_item(
            self.q_item, self.owner, quantity_assigned=Decimal("2.00")
        )
        self.assertEqual(assignment.quantity_assigned, Decimal("2.00"))

    def test_claim_duplicate_blocked(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("1.00"))
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.participant, quantity_assigned=Decimal("1.00"))
        self.assertIn("Ya tenés una asignación activa", str(ctx.exception))

    def test_claim_closed_event_blocked(self):
        self.event.status = EventStatus.CLOSED
        self.event.save()
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.participant, quantity_assigned=Decimal("1.00"))
        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_claim_cancelled_event_blocked(self):
        self.event.status = EventStatus.CANCELLED
        self.event.save()
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.participant, quantity_assigned=Decimal("1.00"))
        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_claim_non_participant_blocked(self):
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.outsider, quantity_assigned=Decimal("1.00"))
        self.assertIn("participantes confirmados", str(ctx.exception))

    def test_claim_quantified_zero_blocked(self):
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.q_item, self.participant, quantity_assigned=Decimal("0"))
        self.assertIn("mayor a cero", str(ctx.exception))

    def test_claim_binary_with_quantity_blocked(self):
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.b_item, self.participant, quantity_assigned=Decimal("1.00"))
        self.assertIn("binarios no tienen cantidad", str(ctx.exception))

    def test_claim_binary_already_covered_blocked(self):
        claim_item(self.b_item, self.participant)
        with self.assertRaises(ItemError) as ctx:
            claim_item(self.b_item, self.owner)
        self.assertIn("ya fue tomado", str(ctx.exception))


class TestModifyAssignment(AssignmentServiceTestBase):
    """Tests for modify_assignment service function."""

    def test_modify_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        updated = modify_assignment(
            assignment, self.participant, quantity_assigned=Decimal("3.00")
        )
        self.assertEqual(updated.quantity_assigned, Decimal("3.00"))

    def test_modify_exceeds_available_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        claim_item(self.q_item, self.owner, quantity_assigned=Decimal("3.00"))
        with self.assertRaises(ItemError) as ctx:
            modify_assignment(
                assignment, self.participant, quantity_assigned=Decimal("3.00")
            )
        self.assertIn("Cantidad no disponible", str(ctx.exception))

    def test_modify_other_user_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        with self.assertRaises(ItemError) as ctx:
            modify_assignment(assignment, self.owner, quantity_assigned=Decimal("2.00"))
        self.assertIn("propias asignaciones", str(ctx.exception))

    def test_modify_purchased_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        mark_as_purchased(assignment, self.participant)
        assignment.refresh_from_db()
        with self.assertRaises(ItemError) as ctx:
            modify_assignment(
                assignment, self.participant, quantity_assigned=Decimal("2.00")
            )
        self.assertIn("ya comprada", str(ctx.exception))

    def test_modify_closed_event_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        self.event.status = EventStatus.CLOSED
        self.event.save()
        with self.assertRaises(ItemError) as ctx:
            modify_assignment(
                assignment, self.participant, quantity_assigned=Decimal("2.00")
            )
        self.assertIn("cerrado o cancelado", str(ctx.exception))


class TestCancelAssignment(AssignmentServiceTestBase):
    """Tests for cancel_assignment service function."""

    def test_cancel_own_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        cancelled = cancel_assignment(assignment, self.participant)
        self.assertIsNotNone(cancelled.cancelled_at)
        self.assertEqual(cancelled.cancelled_by_user, self.participant)

    def test_owner_cancel_others_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        cancelled = cancel_assignment(assignment, self.owner)
        self.assertIsNotNone(cancelled.cancelled_at)
        self.assertEqual(cancelled.cancelled_by_user, self.owner)

    def test_co_admin_cannot_cancel_others(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        with self.assertRaises(ItemError) as ctx:
            cancel_assignment(assignment, self.co_admin)
        self.assertIn("No tenés permiso", str(ctx.exception))

    def test_cancel_purchased_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        mark_as_purchased(assignment, self.participant)
        assignment.refresh_from_db()
        with self.assertRaises(ItemError) as ctx:
            cancel_assignment(assignment, self.participant)
        self.assertIn("ya comprada", str(ctx.exception))

    def test_cancel_closed_event_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.event.status = EventStatus.CLOSED
        self.event.save()
        with self.assertRaises(ItemError) as ctx:
            cancel_assignment(assignment, self.participant)
        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_cancel_frees_quantity(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("3.00")
        )
        self.assertEqual(get_available_quantity(self.q_item), Decimal("2.00"))
        cancel_assignment(assignment, self.participant)
        self.assertEqual(get_available_quantity(self.q_item), Decimal("5.00"))

    def test_can_reclaim_after_cancel(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        cancel_assignment(assignment, self.participant)
        # Should be able to claim again
        new_assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("1.00")
        )
        self.assertIsNotNone(new_assignment.pk)


class TestMarkAsPurchased(AssignmentServiceTestBase):
    """Tests for mark_as_purchased service function."""

    def test_self_purchase_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        purchased = mark_as_purchased(assignment, self.participant)
        self.assertIsNotNone(purchased.purchased_at)
        self.assertEqual(purchased.purchased_by_user, self.participant)

    def test_admin_purchase_others_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        purchased = mark_as_purchased(assignment, self.co_admin)
        self.assertIsNotNone(purchased.purchased_at)
        self.assertEqual(purchased.purchased_by_user, self.co_admin)

    def test_owner_purchase_others_success(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        purchased = mark_as_purchased(assignment, self.owner)
        self.assertEqual(purchased.purchased_by_user, self.owner)

    def test_regular_participant_cannot_purchase_others(self):
        assignment = claim_item(
            self.q_item, self.owner, quantity_assigned=Decimal("2.00")
        )
        with self.assertRaises(ItemError) as ctx:
            mark_as_purchased(assignment, self.participant)
        self.assertIn("No tenés permiso", str(ctx.exception))

    def test_purchase_cancelled_event_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.event.status = EventStatus.CANCELLED
        self.event.save()
        with self.assertRaises(ItemError) as ctx:
            mark_as_purchased(assignment, self.participant)
        self.assertIn("cancelado", str(ctx.exception))

    def test_purchase_closed_event_allowed(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.event.status = EventStatus.CLOSED
        self.event.save()
        purchased = mark_as_purchased(assignment, self.participant)
        self.assertIsNotNone(purchased.purchased_at)

    def test_already_purchased_blocked(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        mark_as_purchased(assignment, self.participant)
        assignment.refresh_from_db()
        with self.assertRaises(ItemError) as ctx:
            mark_as_purchased(assignment, self.participant)
        self.assertIn("ya fue marcada como comprada", str(ctx.exception))

    def test_purchased_immutable_no_modify(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        mark_as_purchased(assignment, self.participant)
        assignment.refresh_from_db()
        with self.assertRaises(ItemError):
            modify_assignment(
                assignment, self.participant, quantity_assigned=Decimal("3.00")
            )

    def test_purchased_immutable_no_cancel(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        mark_as_purchased(assignment, self.participant)
        assignment.refresh_from_db()
        with self.assertRaises(ItemError):
            cancel_assignment(assignment, self.participant)


class TestGetAvailableQuantity(AssignmentServiceTestBase):
    """Tests for get_available_quantity."""

    def test_binary_item_returns_none(self):
        self.assertIsNone(get_available_quantity(self.b_item))

    def test_no_assignments_returns_full(self):
        self.assertEqual(get_available_quantity(self.q_item), Decimal("5.00"))

    def test_partial_assignments(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("2.00"))
        self.assertEqual(get_available_quantity(self.q_item), Decimal("3.00"))

    def test_fully_assigned(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("3.00"))
        claim_item(self.q_item, self.owner, quantity_assigned=Decimal("2.00"))
        self.assertEqual(get_available_quantity(self.q_item), Decimal("0.00"))

    def test_cancelled_not_counted(self):
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("3.00")
        )
        cancel_assignment(assignment, self.participant)
        self.assertEqual(get_available_quantity(self.q_item), Decimal("5.00"))


class TestComputeEventProgress(AssignmentServiceTestBase):
    """Tests for compute_event_progress."""

    def test_empty_event(self):
        empty_event = Event.objects.create(
            owner_user=self.owner,
            name="Empty",
            event_date=timezone.now().date(),
            status=EventStatus.ACTIVE,
        )
        progress = compute_event_progress(empty_event)
        self.assertEqual(progress["percentage"], 0)
        self.assertEqual(progress["total"], 0)

    def test_no_assignments_zero_progress(self):
        progress = compute_event_progress(self.event)
        self.assertEqual(progress["percentage"], 0)
        self.assertEqual(progress["covered"], 0)
        self.assertEqual(progress["total"], 2)

    def test_partial_coverage(self):
        # Cover the quantified item fully
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("5.00"))
        progress = compute_event_progress(self.event)
        self.assertEqual(progress["covered"], 1)
        self.assertEqual(progress["total"], 2)
        self.assertEqual(progress["percentage"], 50)

    def test_full_coverage(self):
        claim_item(self.q_item, self.participant, quantity_assigned=Decimal("5.00"))
        claim_item(self.b_item, self.owner)
        progress = compute_event_progress(self.event)
        self.assertEqual(progress["covered"], 2)
        self.assertEqual(progress["percentage"], 100)


@override_settings(ROOT_URLCONF="config.urls")
class TestAssignmentViews(AssignmentServiceTestBase):
    """Integration tests for assignment views."""

    def test_claim_item_view_post_success(self):
        self.client.login(email="participant@test.com", password="testpass123")
        url = reverse(
            "items:claim", kwargs={"pk": self.event.pk, "item_pk": self.q_item.pk}
        )
        response = self.client.post(
            url,
            {"quantity_assigned": "2.00"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Trigger"], "progress-updated")
        self.assertTrue(
            ItemAssignment.objects.filter(
                item=self.q_item, user=self.participant, cancelled_at__isnull=True
            ).exists()
        )

    def test_claim_item_view_unauthenticated_redirects(self):
        url = reverse(
            "items:claim", kwargs={"pk": self.event.pk, "item_pk": self.q_item.pk}
        )
        response = self.client.post(url, {"quantity_assigned": "1.00"})
        self.assertEqual(response.status_code, 302)

    def test_claim_item_view_non_participant_forbidden(self):
        self.client.login(email="outsider@test.com", password="testpass123")
        url = reverse(
            "items:claim", kwargs={"pk": self.event.pk, "item_pk": self.q_item.pk}
        )
        response = self.client.post(url, {"quantity_assigned": "1.00"})
        self.assertEqual(response.status_code, 403)

    def test_cancel_assignment_view_success(self):
        self.client.login(email="participant@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        url = reverse(
            "items:cancel_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.cancelled_at)

    def test_purchase_assignment_view_success(self):
        self.client.login(email="participant@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        url = reverse(
            "items:purchase_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.purchased_at)

    def test_purchase_closed_event_allowed(self):
        self.client.login(email="participant@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.event.status = EventStatus.CLOSED
        self.event.save()
        url = reverse(
            "items:purchase_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.purchased_at)

    def test_purchase_cancelled_event_blocked(self):
        self.client.login(email="participant@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        self.event.status = EventStatus.CANCELLED
        self.event.save()
        url = reverse(
            "items:purchase_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 422)

    def test_progress_bar_view(self):
        self.client.login(email="participant@test.com", password="testpass123")
        url = reverse("items:progress", kwargs={"pk": self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0%")

    def test_owner_cancel_others_via_view(self):
        self.client.login(email="owner@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        url = reverse(
            "items:cancel_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        assignment.refresh_from_db()
        self.assertIsNotNone(assignment.cancelled_at)
        self.assertEqual(assignment.cancelled_by_user, self.owner)

    def test_co_admin_cannot_cancel_others_via_view(self):
        self.client.login(email="coadmin@test.com", password="testpass123")
        assignment = claim_item(
            self.q_item, self.participant, quantity_assigned=Decimal("2.00")
        )
        url = reverse(
            "items:cancel_assignment",
            kwargs={"pk": self.event.pk, "assignment_pk": assignment.pk},
        )
        response = self.client.post(url, HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 422)
        assignment.refresh_from_db()
        self.assertIsNone(assignment.cancelled_at)
