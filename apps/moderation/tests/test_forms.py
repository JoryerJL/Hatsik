"""Tests for moderation forms."""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event, EventStatus
from apps.items.models import ItemUnit
from apps.moderation.forms import (
    ApproveSuggestionForm,
    EditSuggestionForm,
    RejectSuggestionForm,
    SuggestItemForm,
)
from apps.moderation.models import ItemSuggestion, SuggestionStatus


class SuggestItemFormTests(TestCase):
    """Tests for SuggestItemForm validation."""

    def test_valid_quantified_suggestion(self):
        """Form is valid with name, quantity, and unit."""
        form = SuggestItemForm(
            data={
                "name": "Postre",
                "quantity_total": "2",
                "unit": ItemUnit.PIECES,
            }
        )
        self.assertTrue(form.is_valid())

    def test_valid_binary_suggestion(self):
        """Form is valid with just a name."""
        form = SuggestItemForm(
            data={
                "name": "Servilletas",
                "quantity_total": "",
                "unit": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_quantity_without_unit(self):
        """Quantity without unit is invalid."""
        form = SuggestItemForm(
            data={
                "name": "Carne",
                "quantity_total": "5",
                "unit": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("unit", form.errors)

    def test_invalid_unit_without_quantity(self):
        """Unit without quantity is invalid."""
        form = SuggestItemForm(
            data={
                "name": "Carne",
                "quantity_total": "",
                "unit": ItemUnit.KG,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantity_total", form.errors)

    def test_invalid_quantity_zero(self):
        """Zero quantity is invalid."""
        form = SuggestItemForm(
            data={
                "name": "Carne",
                "quantity_total": "0",
                "unit": ItemUnit.KG,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantity_total", form.errors)

    def test_name_required(self):
        """Name is required."""
        form = SuggestItemForm(
            data={
                "name": "",
                "quantity_total": "",
                "unit": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)


class ApproveSuggestionFormTests(TestCase):
    """Tests for ApproveSuggestionForm."""

    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.com",
            password="testpass123",
            display_name="Owner",
        )
        self.event = Event.objects.create(
            owner_user=self.owner,
            name="Test Event",
            event_date=timezone.now().date(),
            status=EventStatus.ACTIVE,
        )
        self.suggestion = ItemSuggestion.objects.create(
            event=self.event,
            suggested_by_user=self.owner,
            name="Postre",
            quantity_total=Decimal("2"),
            unit=ItemUnit.PIECES,
            status=SuggestionStatus.PENDING_APPROVAL,
        )

    def test_prefills_from_instance(self):
        """Form pre-fills from suggestion instance."""
        form = ApproveSuggestionForm(instance=self.suggestion)
        self.assertEqual(form.initial["name"], "Postre")
        self.assertEqual(form.initial["quantity_total"], Decimal("2"))
        self.assertEqual(form.initial["unit"], ItemUnit.PIECES)

    def test_valid_with_overrides(self):
        """Form accepts override values."""
        form = ApproveSuggestionForm(
            data={
                "name": "Torta de chocolate",
                "quantity_total": "1",
                "unit": ItemUnit.PIECES,
            },
            instance=self.suggestion,
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Torta de chocolate")

    def test_invalid_quantity_without_unit(self):
        """Same validation as other forms."""
        form = ApproveSuggestionForm(
            data={
                "name": "Postre",
                "quantity_total": "3",
                "unit": "",
            },
            instance=self.suggestion,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("unit", form.errors)


class EditSuggestionFormTests(TestCase):
    """Tests for EditSuggestionForm (inherits from SuggestItemForm)."""

    def test_valid_edit(self):
        """Edit form validates the same way as suggest form."""
        form = EditSuggestionForm(
            data={
                "name": "Torta",
                "quantity_total": "1",
                "unit": ItemUnit.PIECES,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_quantity_negative(self):
        """Negative quantity is invalid."""
        form = EditSuggestionForm(
            data={
                "name": "Torta",
                "quantity_total": "-1",
                "unit": ItemUnit.PIECES,
            }
        )
        self.assertFalse(form.is_valid())


class RejectSuggestionFormTests(TestCase):
    """Tests for RejectSuggestionForm."""

    def test_valid_with_note(self):
        """Form is valid with a rejection note."""
        form = RejectSuggestionForm(data={"rejection_note": "Ya lo tenemos"})
        self.assertTrue(form.is_valid())

    def test_valid_without_note(self):
        """Form is valid without a rejection note."""
        form = RejectSuggestionForm(data={"rejection_note": ""})
        self.assertTrue(form.is_valid())
