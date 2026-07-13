"""Forms for item management."""

from django import forms

from apps.items.models import EventItem, ItemUnit


class AddItemForm(forms.ModelForm):
    """Form for adding a new item to an event."""

    class Meta:
        model = EventItem
        fields = ["name", "quantity_total", "unit"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre del ítem",
                    "class": "w-full",
                    "autofocus": True,
                }
            ),
            "quantity_total": forms.NumberInput(
                attrs={
                    "placeholder": "Cantidad (opcional)",
                    "class": "w-full",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "w-full",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "quantity_total": "Cantidad",
            "unit": "Unidad",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make unit choices include a blank option
        self.fields["unit"].choices = [("", "Seleccionar unidad")] + list(
            ItemUnit.choices
        )
        self.fields["quantity_total"].required = False
        self.fields["unit"].required = False

    def clean(self):
        cleaned_data = super().clean()
        quantity_total = cleaned_data.get("quantity_total")
        unit = cleaned_data.get("unit")

        if quantity_total is not None and quantity_total <= 0:
            self.add_error("quantity_total", "La cantidad debe ser mayor a cero.")

        if quantity_total is not None and not unit:
            self.add_error(
                "unit", "La unidad es obligatoria cuando se especifica cantidad."
            )

        if unit and quantity_total is None:
            self.add_error(
                "quantity_total",
                "La cantidad es obligatoria cuando se especifica unidad.",
            )

        return cleaned_data


class EditItemForm(forms.ModelForm):
    """Form for editing an existing item.

    When the item has active assignments, only quantity_total is editable.
    Pass `has_assignments=True` in __init__ to lock name and unit fields.
    """

    class Meta:
        model = EventItem
        fields = ["name", "quantity_total", "unit"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre del ítem",
                    "class": "w-full",
                }
            ),
            "quantity_total": forms.NumberInput(
                attrs={
                    "placeholder": "Cantidad",
                    "class": "w-full",
                    "min": "0.01",
                    "step": "0.01",
                }
            ),
            "unit": forms.Select(
                attrs={
                    "class": "w-full",
                }
            ),
        }
        labels = {
            "name": "Nombre",
            "quantity_total": "Cantidad",
            "unit": "Unidad",
        }

    def __init__(self, *args, has_assignments=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_assignments = has_assignments

        # Make unit choices include a blank option
        self.fields["unit"].choices = [("", "Seleccionar unidad")] + list(
            ItemUnit.choices
        )
        self.fields["quantity_total"].required = False
        self.fields["unit"].required = False

        if has_assignments:
            # Lock name and unit — only quantity_total editable
            self.fields["name"].disabled = True
            self.fields["unit"].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        quantity_total = cleaned_data.get("quantity_total")
        unit = cleaned_data.get("unit")

        # For items with assignments, name/unit come from the instance (disabled)
        if self.has_assignments:
            # Only validate quantity_total
            if quantity_total is not None and quantity_total <= 0:
                self.add_error("quantity_total", "La cantidad debe ser mayor a cero.")
        else:
            # Full validation like AddItemForm
            if quantity_total is not None and quantity_total <= 0:
                self.add_error("quantity_total", "La cantidad debe ser mayor a cero.")

            if quantity_total is not None and not unit:
                self.add_error(
                    "unit",
                    "La unidad es obligatoria cuando se especifica cantidad.",
                )

            if unit and quantity_total is None:
                self.add_error(
                    "quantity_total",
                    "La cantidad es obligatoria cuando se especifica unidad.",
                )

        return cleaned_data
