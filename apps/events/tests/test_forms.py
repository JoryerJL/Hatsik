"""Tests for event forms."""

import pytest

from apps.events.forms import CreateEventForm, EditEventForm

pytestmark = pytest.mark.django_db


class TestCreateEventForm:
    """Tests for CreateEventForm."""

    def test_valid_data(self):
        form = CreateEventForm(
            data={
                "name": "Cena de Navidad",
                "event_date": "2026-12-25",
                "description": "Celebración navideña",
                "assignment_deadline_at": "2026-12-20T18:00",
            }
        )
        assert form.is_valid(), form.errors

    def test_valid_without_optional_fields(self):
        form = CreateEventForm(
            data={
                "name": "Parrillada",
                "event_date": "2026-08-15",
            }
        )
        assert form.is_valid(), form.errors

    def test_missing_name(self):
        form = CreateEventForm(
            data={
                "name": "",
                "event_date": "2026-12-25",
            }
        )
        assert not form.is_valid()
        assert "name" in form.errors

    def test_whitespace_only_name(self):
        form = CreateEventForm(
            data={
                "name": "   ",
                "event_date": "2026-12-25",
            }
        )
        assert not form.is_valid()
        assert "name" in form.errors

    def test_missing_event_date(self):
        form = CreateEventForm(
            data={
                "name": "Cena",
                "event_date": "",
            }
        )
        assert not form.is_valid()
        assert "event_date" in form.errors

    def test_name_stripped(self):
        form = CreateEventForm(
            data={
                "name": "  Fiesta  ",
                "event_date": "2026-12-25",
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["name"] == "Fiesta"


class TestEditEventForm:
    """Tests for EditEventForm."""

    def test_valid_data(self):
        form = EditEventForm(
            data={
                "name": "Cena Actualizada",
                "event_date": "2026-12-26",
                "description": "Descripción nueva",
                "assignment_deadline_at": "2026-12-22T10:00",
            }
        )
        assert form.is_valid(), form.errors

    def test_allows_partial_update_description_blank(self):
        form = EditEventForm(
            data={
                "name": "Evento",
                "event_date": "2026-12-25",
                "description": "",
                "assignment_deadline_at": "",
            }
        )
        assert form.is_valid(), form.errors
        assert form.cleaned_data["description"] == ""
        assert form.cleaned_data["assignment_deadline_at"] is None
