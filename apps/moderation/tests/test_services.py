"""Tests for moderation service layer."""

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
from apps.items.models import EventItem, ItemUnit
from apps.moderation.models import ItemSuggestion, SuggestionStatus
from apps.moderation.services import (
    ModerationError,
    approve_suggestion,
    delete_suggestion,
    edit_suggestion,
    get_pending_suggestions,
    get_user_suggestions,
    reject_suggestion,
    suggest_item,
)


class ModerationTestBase(TestCase):
    """Base class with common setup for moderation tests."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            display_name="Owner",
        )
        self.co_admin = User.objects.create_user(
            email="coadmin@test.com",
            password="testpass123",
            display_name="Co-admin",
        )
        self.participant = User.objects.create_user(
            email="participant@test.com",
            password="testpass123",
            display_name="Participant",
        )
        self.outsider = User.objects.create_user(
            email="outsider@test.com",
            password="testpass123",
            display_name="Outsider",
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


class SuggestItemTests(ModerationTestBase):
    """Tests for suggest_item service function."""

    def test_suggest_item_happy_path(self):
        """Participant can suggest an item."""
        suggestion = suggest_item(
            self.event,
            self.participant,
            name="Postre",
            quantity_total=Decimal("2"),
            unit=ItemUnit.PIECES,
        )
        self.assertEqual(suggestion.name, "Postre")
        self.assertEqual(suggestion.quantity_total, Decimal("2"))
        self.assertEqual(suggestion.unit, ItemUnit.PIECES)
        self.assertEqual(suggestion.status, SuggestionStatus.PENDING_APPROVAL)
        self.assertEqual(suggestion.suggested_by_user, self.participant)
        self.assertEqual(suggestion.event, self.event)

    def test_suggest_binary_item(self):
        """Participant can suggest a binary item (no quantity)."""
        suggestion = suggest_item(
            self.event,
            self.participant,
            name="Servilletas",
        )
        self.assertIsNone(suggestion.quantity_total)
        self.assertIsNone(suggestion.unit)

    def test_suggest_blocked_on_closed_event(self):
        """Cannot suggest items on a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()

        with self.assertRaises(ModerationError) as ctx:
            suggest_item(self.event, self.participant, name="Hielo")

        self.assertIn("cerrado o cancelado", str(ctx.exception))

    def test_suggest_blocked_on_cancelled_event(self):
        """Cannot suggest items on a cancelled event."""
        self.event.status = EventStatus.CANCELLED
        self.event.save()

        with self.assertRaises(ModerationError):
            suggest_item(self.event, self.participant, name="Hielo")

    def test_suggest_blocked_for_non_participant(self):
        """Non-participant cannot suggest items."""
        with self.assertRaises(ModerationError) as ctx:
            suggest_item(self.event, self.outsider, name="Hielo")

        self.assertIn("participantes aceptados", str(ctx.exception))

    def test_suggest_quantity_without_unit_fails(self):
        """Cannot suggest with quantity but no unit."""
        with self.assertRaises(ModerationError):
            suggest_item(
                self.event,
                self.participant,
                name="Carne",
                quantity_total=Decimal("5"),
            )

    def test_suggest_quantity_zero_fails(self):
        """Cannot suggest with quantity <= 0."""
        with self.assertRaises(ModerationError):
            suggest_item(
                self.event,
                self.participant,
                name="Carne",
                quantity_total=Decimal("0"),
                unit=ItemUnit.KG,
            )

    def test_owner_can_also_suggest(self):
        """Owner is also an accepted participant and can suggest."""
        suggestion = suggest_item(
            self.event,
            self.owner,
            name="Vino",
        )
        self.assertEqual(suggestion.suggested_by_user, self.owner)


class EditSuggestionTests(ModerationTestBase):
    """Tests for edit_suggestion service function."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Postre",
            quantity_total=Decimal("2"),
            unit=ItemUnit.PIECES,
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def test_edit_own_pending_suggestion(self):
        """Participant can edit their own pending suggestion."""
        result = edit_suggestion(
            self.suggestion,
            self.participant,
            name="Torta",
            quantity_total=Decimal("1"),
            unit=ItemUnit.PIECES,
        )
        result.refresh_from_db()
        self.assertEqual(result.name, "Torta")
        self.assertEqual(result.quantity_total, Decimal("1"))

    def test_edit_blocked_for_other_user(self):
        """Cannot edit another user's suggestion."""
        with self.assertRaises(ModerationError) as ctx:
            edit_suggestion(self.suggestion, self.owner, name="Otro")

        self.assertIn("propias sugerencias", str(ctx.exception))

    def test_edit_blocked_for_approved_suggestion(self):
        """Cannot edit an approved suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()

        with self.assertRaises(ModerationError) as ctx:
            edit_suggestion(self.suggestion, self.participant, name="Otro")

        self.assertIn("pendientes", str(ctx.exception))

    def test_edit_blocked_for_rejected_suggestion(self):
        """Cannot edit a rejected suggestion."""
        self.suggestion.status = SuggestionStatus.REJECTED
        self.suggestion.save()

        with self.assertRaises(ModerationError):
            edit_suggestion(self.suggestion, self.participant, name="Otro")

    def test_edit_blocked_on_closed_event(self):
        """Cannot edit suggestions on a closed event."""
        self.event.status = EventStatus.CLOSED
        self.event.save()

        with self.assertRaises(ModerationError):
            edit_suggestion(self.suggestion, self.participant, name="Otro")


class DeleteSuggestionTests(ModerationTestBase):
    """Tests for delete_suggestion service function."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Postre",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def test_delete_own_pending_suggestion(self):
        """Participant can delete their own pending suggestion."""
        pk = self.suggestion.pk
        delete_suggestion(self.suggestion, self.participant)
        self.assertFalse(ItemSuggestion.objects.filter(pk=pk).exists())

    def test_delete_blocked_for_other_user(self):
        """Cannot delete another user's suggestion."""
        with self.assertRaises(ModerationError):
            delete_suggestion(self.suggestion, self.owner)

    def test_delete_blocked_for_non_pending(self):
        """Cannot delete a non-pending suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()

        with self.assertRaises(ModerationError):
            delete_suggestion(self.suggestion, self.participant)


class ApproveSuggestionTests(ModerationTestBase):
    """Tests for approve_suggestion service function."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Postre",
            quantity_total=Decimal("2"),
            unit=ItemUnit.PIECES,
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def test_owner_can_approve(self):
        """Owner can approve a suggestion."""
        item = approve_suggestion(self.suggestion, self.owner)

        self.assertIsInstance(item, EventItem)
        self.assertEqual(item.name, "Postre")
        self.assertEqual(item.quantity_total, Decimal("2"))
        self.assertEqual(item.unit, ItemUnit.PIECES)
        self.assertEqual(item.event, self.event)
        self.assertEqual(item.created_by_user, self.owner)
        self.assertEqual(item.source_suggestion, self.suggestion)

        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.status, SuggestionStatus.APPROVED)
        self.assertEqual(self.suggestion.reviewed_by_user, self.owner)
        self.assertIsNotNone(self.suggestion.reviewed_at)
        self.assertEqual(self.suggestion.converted_event_item, item)

    def test_co_admin_can_approve(self):
        """Co-admin can approve a suggestion."""
        item = approve_suggestion(self.suggestion, self.co_admin)
        self.assertEqual(item.name, "Postre")
        self.suggestion.refresh_from_db()
        self.assertEqual(self.suggestion.reviewed_by_user, self.co_admin)

    def test_approve_with_overridden_values(self):
        """Admin can override name, quantity, unit during approval."""
        item = approve_suggestion(
            self.suggestion,
            self.owner,
            name="Torta de chocolate",
            quantity_total=Decimal("1"),
            unit=ItemUnit.PIECES,
        )
        self.assertEqual(item.name, "Torta de chocolate")
        self.assertEqual(item.quantity_total, Decimal("1"))

    def test_approve_blocked_for_participant(self):
        """Regular participant cannot approve suggestions."""
        with self.assertRaises(ModerationError) as ctx:
            approve_suggestion(self.suggestion, self.participant)

        self.assertIn("organizador o co-admins", str(ctx.exception))

    def test_approve_already_approved_fails(self):
        """Cannot approve an already approved suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()

        with self.assertRaises(ModerationError) as ctx:
            approve_suggestion(self.suggestion, self.owner)

        self.assertIn("pendientes", str(ctx.exception))

    def test_approve_rejected_fails(self):
        """Cannot approve a rejected suggestion."""
        self.suggestion.status = SuggestionStatus.REJECTED
        self.suggestion.save()

        with self.assertRaises(ModerationError):
            approve_suggestion(self.suggestion, self.owner)

    def test_approve_creates_item_linked_to_suggestion(self):
        """Approved item links back to the suggestion."""
        item = approve_suggestion(self.suggestion, self.owner)
        self.assertEqual(item.source_suggestion, self.suggestion)


class RejectSuggestionTests(ModerationTestBase):
    """Tests for reject_suggestion service function."""

    def setUp(self):
        super().setUp()
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Postre",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def test_owner_can_reject(self):
        """Owner can reject a suggestion."""
        result = reject_suggestion(
            self.suggestion, self.owner, rejection_note="Ya lo tenemos"
        )
        result.refresh_from_db()
        self.assertEqual(result.status, SuggestionStatus.REJECTED)
        self.assertEqual(result.rejection_note, "Ya lo tenemos")
        self.assertEqual(result.reviewed_by_user, self.owner)
        self.assertIsNotNone(result.reviewed_at)

    def test_co_admin_can_reject(self):
        """Co-admin can reject a suggestion."""
        result = reject_suggestion(self.suggestion, self.co_admin)
        result.refresh_from_db()
        self.assertEqual(result.status, SuggestionStatus.REJECTED)

    def test_reject_without_note(self):
        """Rejection note is optional."""
        result = reject_suggestion(self.suggestion, self.owner)
        result.refresh_from_db()
        self.assertEqual(result.rejection_note, "")

    def test_reject_blocked_for_participant(self):
        """Regular participant cannot reject suggestions."""
        with self.assertRaises(ModerationError):
            reject_suggestion(self.suggestion, self.participant)

    def test_reject_already_approved_fails(self):
        """Cannot reject an already approved suggestion."""
        self.suggestion.status = SuggestionStatus.APPROVED
        self.suggestion.save()

        with self.assertRaises(ModerationError):
            reject_suggestion(self.suggestion, self.owner)

    def test_reject_already_rejected_fails(self):
        """Cannot reject an already rejected suggestion."""
        self.suggestion.status = SuggestionStatus.REJECTED
        self.suggestion.save()

        with self.assertRaises(ModerationError):
            reject_suggestion(self.suggestion, self.owner)


class QueryHelperTests(ModerationTestBase):
    """Tests for get_pending_suggestions and get_user_suggestions."""

    def test_get_pending_suggestions(self):
        """Returns only pending suggestions for the event."""
        s1 = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Pending 1",
            status=SuggestionStatus.PENDING_APPROVAL,
        )
        ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Approved",
            status=SuggestionStatus.APPROVED,
        )
        s3 = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.co_admin,
            name="Pending 2",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

        pending = list(get_pending_suggestions(self.event))
        self.assertEqual(len(pending), 2)
        self.assertEqual(pending[0].pk, s1.pk)
        self.assertEqual(pending[1].pk, s3.pk)

    def test_get_user_suggestions(self):
        """Returns all suggestions by a specific user."""
        ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Mine 1",
            status=SuggestionStatus.PENDING_APPROVAL,
        )
        ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.participant,
            name="Mine 2",
            status=SuggestionStatus.REJECTED,
        )
        ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.co_admin,
            name="Not mine",
            status=SuggestionStatus.PENDING_APPROVAL,
        )

        user_suggestions = list(get_user_suggestions(self.event, self.participant))
        self.assertEqual(len(user_suggestions), 2)
        # Ordered by -created_at, so Mine 2 first
        self.assertEqual(user_suggestions[0].name, "Mine 2")
        self.assertEqual(user_suggestions[1].name, "Mine 1")
