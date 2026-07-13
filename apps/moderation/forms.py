"""Forms for item suggestion moderation."""

from django import forms

from apps.items.models import ItemUnit
from apps.moderation.models import ItemSuggestion


class SuggestItemForm(forms.ModelForm):
    """Form for participants to suggest a new item."""

    class Meta:
        model = ItemSuggestion
        fields = ["name", "quantity_total", "unit"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre del ítem sugerido",
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


class EditSuggestionForm(SuggestItemForm):
    """Form for editing an own pending suggestion.

    Inherits all validation from SuggestItemForm.
    """

    pass


class ApproveSuggestionForm(forms.ModelForm):
    """Form for approving a suggestion with optional edits.

    Pre-filled from the suggestion data. All fields editable by the admin.
    """

    class Meta:
        model = ItemSuggestion
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


class RejectSuggestionForm(forms.Form):
    """Form for rejecting a suggestion with an optional note."""

    rejection_note = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "placeholder": "Motivo del rechazo (opcional)",
                "class": "w-full",
                "rows": 3,
            }
        ),
        label="Motivo del rechazo",
    )
