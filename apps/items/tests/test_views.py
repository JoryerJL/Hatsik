"""Integration tests for items views."""

from decimal import Decimal

from django.test import TestCase
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


class ItemViewTestBase(TestCase):
    """Base class with common setup for item view tests."""

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


class AddItemViewTests(ItemViewTestBase):
    """Tests for add_item_view."""

    def get_url(self):
        return reverse("items:add", kwargs={"pk": self.event.pk})

    def test_get_renders_form_for_owner(self):
        """Owner can see the add item form."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nombre")

    def test_get_forbidden_for_participant(self):
        """Participant gets 403 on the add item page."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_redirects_for_anonymous(self):
        """Anonymous user is redirected to login."""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_post_creates_quantified_item(self):
        """Owner can create a quantified item via POST."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Coca-Cola",
                "quantity_total": "6",
                "unit": ItemUnit.BOTTLES,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EventItem.objects.filter(event=self.event, name="Coca-Cola").exists()
        )

    def test_post_creates_binary_item(self):
        """Owner can create a binary item (no quantity)."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Mantel", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 302)
        item = EventItem.objects.get(event=self.event, name="Mantel")
        self.assertIsNone(item.quantity_total)
        self.assertIsNone(item.unit)

    def test_post_invalid_form_shows_errors(self):
        """Invalid form data re-renders with errors."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "obligatorio")

    def test_post_blocked_on_closed_event(self):
        """Adding items to a closed event shows error."""
        self.event.status = EventStatus.CLOSED
        self.event.save()
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Hielo", "quantity_total": "", "unit": ""},
        )
        # Service error is added to form — re-renders with 200
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cerrado o cancelado")

    def test_post_forbidden_for_participant(self):
        """Participant cannot POST to add item."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Hielo", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 403)


class EditItemViewTests(ItemViewTestBase):
    """Tests for edit_item_view."""

    def setUp(self):
        super().setUp()
        self.item = EventItem.objects.create(
            event=self.event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )

    def get_url(self):
        return reverse(
            "items:edit", kwargs={"pk": self.event.pk, "item_pk": self.item.pk}
        )

    def test_get_renders_form_for_owner(self):
        """Owner can see the edit item form (pre-filled)."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carne")

    def test_get_forbidden_for_participant(self):
        """Participant gets 403 on the edit item page."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_shows_warning_when_has_assignments(self):
        """Edit form shows warning banner when item has assignments."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("2"),
        )
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["has_assignments"])

    def test_post_updates_item_no_assignments(self):
        """Owner can update all fields when no assignments."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Pollo",
                "quantity_total": "3",
                "unit": ItemUnit.PIECES,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Pollo")
        self.assertEqual(self.item.quantity_total, Decimal("3"))
        self.assertEqual(self.item.unit, ItemUnit.PIECES)

    def test_post_updates_quantity_with_assignments(self):
        """With assignments, only quantity_total is updated."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("2"),
        )
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Should Not Change",
                "quantity_total": "8",
                "unit": ItemUnit.G,  # Should not change
            },
        )
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, "Carne")  # unchanged
        self.assertEqual(self.item.quantity_total, Decimal("8"))
        self.assertEqual(self.item.unit, ItemUnit.KG)  # unchanged

    def test_post_blocked_below_assigned_sum(self):
        """Cannot reduce quantity below assigned sum."""
        ItemAssignment.objects.create(
            item=self.item,
            user=self.participant,
            quantity_assigned=Decimal("4"),
        )
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Carne",
                "quantity_total": "2",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "por debajo de lo asignado")


class DeleteItemViewTests(ItemViewTestBase):
    """Tests for delete_item_view."""

    def setUp(self):
        super().setUp()
        self.item = EventItem.objects.create(
            event=self.event,
            name="Hielo",
            quantity_total=Decimal("10"),
            unit=ItemUnit.KG,
            created_by_user=self.owner,
        )

    def get_url(self):
        return reverse(
            "items:delete", kwargs={"pk": self.event.pk, "item_pk": self.item.pk}
        )

    def test_post_deletes_item(self):
        """Owner can delete an item via POST."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertFalse(EventItem.objects.filter(pk=self.item.pk).exists())

    def test_post_htmx_returns_empty(self):
        """HTMX delete returns empty response."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(EventItem.objects.filter(pk=self.item.pk).exists())

    def test_post_forbidden_for_participant(self):
        """Participant cannot delete items."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_post_blocked_on_closed_event(self):
        """Cannot delete items in a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 422)
        self.assertTrue(EventItem.objects.filter(pk=self.item.pk).exists())

    def test_get_redirects_to_detail(self):
        """GET on delete URL redirects back to event detail."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
