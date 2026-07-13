"""Forms for event creation and editing."""

from django import forms

from apps.events.models import Event


class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "event_date", "description", "assignment_deadline_at"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Nombre del evento"}
            ),
            "event_date": forms.DateInput(
                attrs={"type": "date", "placeholder": "Fecha del evento"}
            ),
            "description": forms.Textarea(
                attrs={"placeholder": "Descripción (opcional)", "rows": 3}
            ),
            "assignment_deadline_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "Fecha límite de asignación (opcional)",
                }
            ),
        }
        labels = {
            "name": "Nombre del evento",
            "event_date": "Fecha del evento",
            "description": "Descripción",
            "assignment_deadline_at": "Fecha límite de asignación",
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError(
                "El nombre del evento es obligatorio.", code="required"
            )
        return name


class EditEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["name", "event_date", "description", "assignment_deadline_at"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Nombre del evento"}
            ),
            "event_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(
                attrs={"placeholder": "Descripción (opcional)", "rows": 3}
            ),
            "assignment_deadline_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}
            ),
        }
        labels = {
            "name": "Nombre del evento",
            "event_date": "Fecha del evento",
            "description": "Descripción",
            "assignment_deadline_at": "Fecha límite de asignación",
        }
