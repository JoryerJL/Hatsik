"""Integration tests for moderation views."""

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
from apps.items.models import EventItem, ItemUnit
from apps.moderation.models import ItemSuggestion, SuggestionStatus


class ModerationViewTestBase(TestCase):
    """Base class with common setup for moderation view tests."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            display_name="Owner",
        )
        self.owner.email_verified_at = timezone.now()
        self.owner.save()

        self.co_admin = User.objects.create_user(
            email="coadmin@test.com",
            password="testpass123",
            display_name="Co-admin",
        )
        self.co_admin.email_verified_at = timezone.now()
        self.co_admin.save()

        self.participant = User.objects.create_user(
            email="participant@test.com",
            password="testpass123",
            display_name="Participant",
        )
        self.participant.email_verified_at = timezone.now()
        self.participant.save()

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
        EventParticipation.objects.create(
            event=self.event,
            user=self.owner,
            role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
        EventParticipation.objects.create(
            event=self.event,
            user=self.co_admin,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        EventParticipation.objects.create(
            event=self.event,
            user=self.participant,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )


class SuggestItemViewTests(ModerationViewTestBase):
    """Tests for suggest_item_view."""

    def get_url(self):
        return reverse("moderation:suggest", kwargs={"pk": self.event.pk})

    def test_get_renders_form_for_participant(self):
        """Participant can see the suggest item form."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sugerir")

    def test_get_renders_form_for_owner(self):
        """Owner (also a participant) can see the suggest item form."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_get_forbidden_for_non_participant(self):
        """Non-participant gets 403."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_redirects_for_anonymous(self):
        """Anonymous user is redirected to login."""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_post_creates_suggestion_with_quantity(self):
        """Participant can suggest a quantified item."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Coca-Cola",
                "quantity_total": "6",
                "unit": ItemUnit.LITERS,
            },
        )
        self.assertEqual(response.status_code, 302)
        suggestion = ItemSuggestion.objects.get(
            event=self.event, name="Coca-Cola"
        )
        self.assertEqual(suggestion.suggested_by_user, self.participant)
        self.assertEqual(suggestion.quantity_total, Decimal("6"))
        self.assertEqual(suggestion.unit, ItemUnit.LITERS)
        self.assertEqual(suggestion.status, SuggestionStatus.PENDING_APPROVAL)

    def test_post_creates_binary_suggestion(self):
        """Participant can suggest a binary item (no quantity)."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Mantel", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 302)
        suggestion = ItemSuggestion.objects.get(
            event=self.event, name="Mantel"
        )
        self.assertIsNone(suggestion.quantity_total)
        self.assertIsNone(suggestion.unit)

    def test_post_invalid_form_shows_errors(self):
        """Invalid form data re-renders with errors."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 200)

    def test_post_forbidden_for_non_participant(self):
        """Non-participant cannot POST suggestions."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Hielo", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 403)


class EditSuggestionViewTests(ModerationViewTestBase):
    """Tests for edit_suggestion_view."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Papas",
            quantity_total=Decimal("2"),
            unit=ItemUnit.KG,
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def get_url(self, suggestion_pk=None):
        return reverse(
            "moderation:edit",
            kwargs={
                "pk": self.event.pk,
                "suggestion_pk": suggestion_pk or self.suggestion.pk,
            },
        )

    def test_get_renders_form_for_owner_of_suggestion(self):
        """Suggestion owner can see the edit form (pre-filled)."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Papas")

    def test_get_404_for_other_participants_suggestion(self):
        """Another participant gets 404 (filter by user)."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    def test_get_forbidden_for_non_participant(self):
        """Non-participant gets 403 from decorator."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_404_for_approved_suggestion(self):
        """Cannot edit an already approved suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 404)

    def test_post_updates_suggestion(self):
        """Owner of suggestion can update it."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Papas fritas",
                "quantity_total": "3",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.name, "Papas fritas")
        self.assertEqual(self.suggestion.quantity_total, Decimal("3"))

    def test_post_forbidden_for_non_participant(self):
        """Non-participant cannot POST edits."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"name": "Hack", "quantity_total": "", "unit": ""},
        )
        self.assertEqual(response.status_code, 403)


class DeleteSuggestionViewTests(ModerationViewTestBase):
    """Tests for delete_suggestion_view."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Servilletas",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def get_url(self, suggestion_pk=None):
        return reverse(
            "moderation:delete",
            kwargs={
                "pk": self.event.pk,
                "suggestion_pk": suggestion_pk or self.suggestion.pk,
            },
        )

    def test_post_deletes_own_suggestion(self):
        """Participant can delete their own pending suggestion."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            ItemSuggestion.objects.filter(pk=self.suggestion.pk).exists()
        )

    def test_post_htmx_returns_empty(self):
        """HTMX delete returns empty response."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(), HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.assertFalse(
            ItemSuggestion.objects.filter(pk=self.suggestion.pk).exists()
        )

    def test_post_404_for_other_users_suggestion(self):
        """Cannot delete another user's suggestion."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 404)

    def test_post_forbidden_for_non_participant(self):
        """Non-participant gets 403."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_redirects_to_detail(self):
        """GET on delete URL redirects back to event detail."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_post_404_for_approved_suggestion(self):
        """Cannot delete an already approved suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 404)


class ApproveSuggestionViewTests(ModerationViewTestBase):
    """Tests for approve_suggestion_view."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Helado",
            quantity_total=Decimal("2"),
            unit=ItemUnit.KG,
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def get_url(self, suggestion_pk=None):
        return reverse(
            "moderation:approve",
            kwargs={
                "pk": self.event.pk,
                "suggestion_pk": suggestion_pk or self.suggestion.pk,
            },
        )

    def test_get_renders_form_for_owner(self):
        """Owner can see the approve form (pre-filled)."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Helado")

    def test_get_renders_form_for_co_admin(self):
        """Co-admin can see the approve form."""
        self.client.login(email="coadmin@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    def test_get_forbidden_for_participant(self):
        """Regular participant gets 403."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_forbidden_for_non_participant(self):
        """Non-participant gets 403."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_post_approves_and_creates_item(self):
        """Owner can approve a suggestion, creating an EventItem."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Helado",
                "quantity_total": "2",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.APPROVED)
        self.assertTrue(
            EventItem.objects.filter(event=self.event, name="Helado").exists()
        )

    def test_post_approves_with_overrides(self):
        """Admin can override name/quantity when approving."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Helado de Chocolate",
                "quantity_total": "5",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 302)
        item = EventItem.objects.get(
            event=self.event, name="Helado de Chocolate"
        )
        self.assertEqual(item.quantity_total, Decimal("5"))

    def test_post_co_admin_can_approve(self):
        """Co-admin can also approve suggestions."""
        self.client.login(email="coadmin@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Helado",
                "quantity_total": "2",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.APPROVED)

    def test_post_forbidden_for_participant(self):
        """Regular participant cannot approve."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={
                "name": "Helado",
                "quantity_total": "2",
                "unit": ItemUnit.KG,
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_get_redirects_for_anonymous(self):
        """Anonymous user is redirected to login."""
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class RejectSuggestionViewTests(ModerationViewTestBase):
    """Tests for reject_suggestion_view."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Cerveza",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def get_url(self, suggestion_pk=None):
        return reverse(
            "moderation:reject",
            kwargs={
                "pk": self.event.pk,
                "suggestion_pk": suggestion_pk or self.suggestion.pk,
            },
        )

    def test_post_rejects_suggestion_by_owner(self):
        """Owner can reject a suggestion."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.REJECTED)

    def test_post_rejects_with_note(self):
        """Owner can reject with a rejection note."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"rejection_note": "No se permite alcohol."},
        )
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.REJECTED)
        self.assertEqual(self.suggestion.rejection_note, "No se permite alcohol.")

    def test_post_htmx_returns_empty(self):
        """HTMX reject returns empty response."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(
            self.get_url(),
            data={"rejection_note": ""},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.REJECTED)

    def test_post_co_admin_can_reject(self):
        """Co-admin can also reject suggestions."""
        self.client.login(email="coadmin@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.REJECTED)

    def test_post_forbidden_for_participant(self):
        """Regular participant cannot reject."""
        self.client.login(email="participant@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_post_forbidden_for_non_participant(self):
        """Non-participant gets 403."""
        self.client.login(email="outsider@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 403)

    def test_get_redirects_to_detail(self):
        """GET on reject URL redirects to event detail (POST only)."""
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)

    def test_post_404_for_already_rejected(self):
        """Cannot reject an already rejected suggestion."""
        self.suggestion.status = SuggestionStatus.REJECTED
        self.suggestion.save()
        self.client.login(email="owner@test.com", password="testpass123")
        response = self.client.post(self.get_url())
        self.assertEqual(response.status_code, 404)
