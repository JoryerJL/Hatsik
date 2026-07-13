"""Tests for items forms."""

from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.events.models import Event, EventStatus
from apps.items.forms import AddItemForm, EditItemForm
from apps.items.models import EventItem, ItemUnit


class AddItemFormTests(TestCase):
    """Tests for AddItemForm validation."""

    def test_valid_quantified_item(self):
        """Form is valid with name, quantity, and unit."""
        form = AddItemForm(
            data={
                "name": "Coca-Cola",
                "quantity_total": "6",
                "unit": ItemUnit.BOTTLES,
            }
        )
        self.assertTrue(form.is_valid())

    def test_valid_binary_item(self):
        """Form is valid with just a name (binary item)."""
        form = AddItemForm(
            data={
                "name": "Mantel",
                "quantity_total": "",
                "unit": "",
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_quantity_without_unit(self):
        """Quantity without unit is invalid."""
        form = AddItemForm(
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
        form = AddItemForm(
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
        form = AddItemForm(
            data={
                "name": "Carne",
                "quantity_total": "0",
                "unit": ItemUnit.KG,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantity_total", form.errors)

    def test_invalid_quantity_negative(self):
        """Negative quantity is invalid."""
        form = AddItemForm(
            data={
                "name": "Carne",
                "quantity_total": "-1",
                "unit": ItemUnit.KG,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantity_total", form.errors)

    def test_name_required(self):
        """Name is required."""
        form = AddItemForm(
            data={
                "name": "",
                "quantity_total": "",
                "unit": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_decimal_quantity_valid(self):
        """Decimal quantities are valid."""
        form = AddItemForm(
            data={
                "name": "Leche",
                "quantity_total": "2.5",
                "unit": ItemUnit.LITERS,
            }
        )
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["quantity_total"], Decimal("2.5")
        )


class EditItemFormTests(TestCase):
    """Tests for EditItemForm validation."""

    def test_valid_edit_no_assignments(self):
        """Without assignments, all fields editable."""
        form = EditItemForm(
            data={
                "name": "Pollo",
                "quantity_total": "3",
                "unit": ItemUnit.KG,
            },
            has_assignments=False,
        )
        self.assertTrue(form.is_valid())

    def test_valid_edit_with_assignments(self):
        """With assignments, only quantity_total matters."""
        owner = User.objects.create_user(
            email="owner@test.com", password="testpass123", display_name="Owner"
        )
        event = Event.objects.create(
            owner_user=owner,
            name="Test Event",
            event_date=timezone.now().date(),
            status=EventStatus.ACTIVE,
        )
        item = EventItem.objects.create(
            event=event,
            name="Carne",
            quantity_total=Decimal("5"),
            unit=ItemUnit.KG,
            created_by_user=owner,
        )
        form = EditItemForm(
            data={
                "name": "Carne",  # Disabled field — value comes from instance
                "quantity_total": "8",
                "unit": ItemUnit.KG,  # Disabled field — value comes from instance
            },
            instance=item,
            has_assignments=True,
        )
        self.assertTrue(form.is_valid())

    def test_has_assignments_locks_name_and_unit(self):
        """With assignments, name and unit fields are disabled."""
        form = EditItemForm(has_assignments=True)
        self.assertTrue(form.fields["name"].disabled)
        self.assertTrue(form.fields["unit"].disabled)

    def test_no_assignments_all_fields_editable(self):
        """Without assignments, no fields are disabled."""
        form = EditItemForm(has_assignments=False)
        self.assertFalse(form.fields["name"].disabled)
        self.assertFalse(form.fields["unit"].disabled)

    def test_invalid_quantity_zero_with_assignments(self):
        """Zero quantity is invalid even with assignments."""
        form = EditItemForm(
            data={
                "name": "Carne",
                "quantity_total": "0",
                "unit": ItemUnit.KG,
            },
            has_assignments=True,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("quantity_total", form.errors)

    def test_unit_choices_include_blank(self):
        """Unit dropdown includes a blank/placeholder option."""
        form = AddItemForm()
        choices = form.fields["unit"].choices
        self.assertEqual(choices[0], ("", "Seleccionar unidad"))
