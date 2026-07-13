"""Tests for event views."""

import datetime

import pytest
from django.test import Client

from apps.accounts.models import User
from apps.events.models import (
    AccessStatus,
    Event,
    EventParticipation,
    EventRole,
    EventStatus,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    from django.utils import timezone

    u = User.objects.create_user(
        email="dashboard@example.com",
        password="testpass1",
        display_name="Dashboard User",
    )
    u.email_verified_at = timezone.now()
    u.save()
    return u


@pytest.fixture
def other_user():
    return User.objects.create_user(
        email="other@example.com",
        password="testpass1",
        display_name="Other User",
    )


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def auth_client(client, user):
    client.login(email="dashboard@example.com", password="testpass1")
    return client


@pytest.fixture
def active_event(user):
    event = Event.objects.create(
        owner_user=user,
        name="Active Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.ACTIVE,
    )
    EventParticipation.objects.create(
        event=event,
        user=user,
        role=EventRole.OWNER,
        access_status=AccessStatus.ACCEPTED,
    )
    return event


class TestDashboardRequiresLogin:
    def test_anonymous_user_redirected(self, client):
        response = client.get("/events/")
        assert response.status_code == 302
        assert "/login/" in response.url


class TestDashboardEmptyState:
    def test_new_user_sees_empty_state(self, auth_client):
        response = auth_client.get("/events/")
        assert response.status_code == 200
        assert "¿Nuevo plan en mente?" in response.content.decode()


class TestDashboardShowsUserEvents:
    def test_user_with_events_sees_them(self, auth_client, active_event):
        response = auth_client.get("/events/")
        assert response.status_code == 200
        content = response.content.decode()
        assert active_event.name in content


class TestDashboardExcludesNonAccepted:
    def test_pending_not_shown(self, auth_client, user):
        event = Event.objects.create(
            owner_user=user,
            name="Pending Event",
            event_date=datetime.date(2026, 11, 15),
            status=EventStatus.ACTIVE,
        )
        EventParticipation.objects.create(
            event=event,
            user=user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
        )
        response = auth_client.get("/events/")
        content = response.content.decode()
        assert "Pending Event" not in content

    def test_removed_not_shown(self, auth_client, user):
        event = Event.objects.create(
            owner_user=user,
            name="Removed Event",
            event_date=datetime.date(2026, 11, 15),
            status=EventStatus.ACTIVE,
        )
        EventParticipation.objects.create(
            event=event,
            user=user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REMOVED,
        )
        response = auth_client.get("/events/")
        content = response.content.decode()
        assert "Removed Event" not in content

    def test_left_not_shown(self, auth_client, user):
        event = Event.objects.create(
            owner_user=user,
            name="Left Event",
            event_date=datetime.date(2026, 11, 15),
            status=EventStatus.ACTIVE,
        )
        EventParticipation.objects.create(
            event=event,
            user=user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.LEFT,
        )
        response = auth_client.get("/events/")
        content = response.content.decode()
        assert "Left Event" not in content


class TestDashboardShowsCorrectRole:
    def test_owner_events_show_owner_badge(self, auth_client, active_event):
        response = auth_client.get("/events/")
        content = response.content.decode()
        assert "Owner" in content

    def test_participant_events_show_participant_badge(self, auth_client, user):
        other = User.objects.create_user(
            email="creator@example.com",
            password="testpass1",
            display_name="Creator",
        )
        event = Event.objects.create(
            owner_user=other,
            name="Participant Event",
            event_date=datetime.date(2026, 10, 10),
            status=EventStatus.ACTIVE,
        )
        EventParticipation.objects.create(
            event=event,
            user=user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        response = auth_client.get("/events/")
        content = response.content.decode()
        assert "Participante" in content


class TestCreateEventView:
    def test_create_event_requires_login(self, client):
        response = client.get("/events/create/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_create_event_get_renders_form(self, auth_client):
        response = auth_client.get("/events/create/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Nuevo Evento" in content
        assert 'name="name"' in content
        assert 'name="event_date"' in content

    def test_create_event_post_valid(self, auth_client, user):
        response = auth_client.post("/events/create/", {
            "name": "Mi Asado",
            "event_date": "2026-12-25",
        })
        assert response.status_code == 302
        event = Event.objects.get(name="Mi Asado")
        assert event.owner_user == user
        assert event.event_date == datetime.date(2026, 12, 25)
        # Owner participation created
        participation = EventParticipation.objects.get(
            event=event, user=user
        )
        assert participation.role == EventRole.OWNER
        assert participation.access_status == AccessStatus.ACCEPTED

    def test_create_event_post_missing_name(self, auth_client):
        response = auth_client.post("/events/create/", {
            "name": "",
            "event_date": "2026-12-25",
        })
        assert response.status_code == 200
        assert Event.objects.count() == 0

    def test_create_event_post_missing_date(self, auth_client):
        response = auth_client.post("/events/create/", {
            "name": "Mi Asado",
            "event_date": "",
        })
        assert response.status_code == 200
        assert Event.objects.count() == 0

    def test_create_event_with_optional_fields(self, auth_client):
        response = auth_client.post("/events/create/", {
            "name": "Evento Completo",
            "event_date": "2026-12-31",
            "description": "Una gran fiesta",
            "assignment_deadline_at": "2026-12-30T18:00",
        })
        assert response.status_code == 302
        event = Event.objects.get(name="Evento Completo")
        assert event.description == "Una gran fiesta"
        assert event.assignment_deadline_at is not None


class TestEventDetailView:
    def test_detail_requires_login(self, client, active_event):
        response = client.get(f"/events/{active_event.pk}/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_detail_requires_accepted_participation(self, auth_client, user):
        from django.utils import timezone

        other = User.objects.create_user(
            email="owner2@x.com", password="p1", display_name="O",
        )
        other.email_verified_at = timezone.now()
        other.save()
        event = Event.objects.create(
            owner_user=other, name="Private", event_date=datetime.date(2026, 1, 1),
        )
        EventParticipation.objects.create(
            event=event, user=other, role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
        # user is NOT a participant
        response = auth_client.get(f"/events/{event.pk}/")
        assert response.status_code == 403

    def test_detail_shows_event_info(self, auth_client, active_event):
        response = auth_client.get(f"/events/{active_event.pk}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert active_event.name in content

    def test_detail_shows_participants(self, auth_client, active_event, user):
        response = auth_client.get(f"/events/{active_event.pk}/")
        content = response.content.decode()
        assert user.display_name in content


class TestEditEventView:
    def test_edit_requires_owner(self, auth_client, user):
        from django.utils import timezone

        other = User.objects.create_user(
            email="owner3@x.com", password="p1", display_name="O",
        )
        other.email_verified_at = timezone.now()
        other.save()
        event = Event.objects.create(
            owner_user=other, name="NotMine", event_date=datetime.date(2026, 1, 1),
        )
        EventParticipation.objects.create(
            event=event, user=other, role=EventRole.OWNER,
            access_status=AccessStatus.ACCEPTED,
        )
        response = auth_client.get(f"/events/{event.pk}/edit/")
        assert response.status_code == 403

    def test_edit_get_shows_form(self, auth_client, active_event):
        response = auth_client.get(f"/events/{active_event.pk}/edit/")
        assert response.status_code == 200
        assert 'name="name"' in response.content.decode()

    def test_edit_post_updates_event(self, auth_client, active_event):
        response = auth_client.post(f"/events/{active_event.pk}/edit/", {
            "name": "Updated Name",
            "event_date": "2026-12-31",
        })
        assert response.status_code == 302
        active_event.refresh_from_db()
        assert active_event.name == "Updated Name"


class TestLifecycleViews:
    def test_close_event_as_owner(self, auth_client, active_event):
        response = auth_client.post(f"/events/{active_event.pk}/close/")
        assert response.status_code == 302
        active_event.refresh_from_db()
        assert active_event.status == EventStatus.CLOSED

    def test_close_event_non_owner_forbidden(self, client, active_event):
        from django.utils import timezone

        other = User.objects.create_user(
            email="nonowner@x.com", password="p1", display_name="X"
        )
        other.email_verified_at = timezone.now()
        other.save()
        client.login(email="nonowner@x.com", password="p1")
        response = client.post(f"/events/{active_event.pk}/close/")
        assert response.status_code == 403

    def test_reopen_closed_event(self, auth_client, active_event):
        from apps.events.services import close_event

        close_event(active_event)
        response = auth_client.post(f"/events/{active_event.pk}/reopen/")
        assert response.status_code == 302
        active_event.refresh_from_db()
        assert active_event.status == EventStatus.ACTIVE

    def test_cancel_event(self, auth_client, active_event):
        response = auth_client.post(f"/events/{active_event.pk}/cancel/")
        assert response.status_code == 302
        active_event.refresh_from_db()
        assert active_event.status == EventStatus.CANCELLED

    def test_cannot_reopen_cancelled_event(self, auth_client, active_event):
        from apps.events.services import cancel_event

        cancel_event(active_event)
        response = auth_client.post(f"/events/{active_event.pk}/reopen/")
        assert response.status_code == 302  # redirect with error message
        active_event.refresh_from_db()
        assert active_event.status == EventStatus.CANCELLED


class TestParticipantManagementViews:
    def test_promote_participant(self, auth_client, active_event, user):
        other = User.objects.create_user(
            email="part@x.com", password="p1", display_name="Part"
        )
        participation = EventParticipation.objects.create(
            event=active_event,
            user=other,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        response = auth_client.post(
            f"/events/{active_event.pk}/participants/{participation.pk}/promote/"
        )
        assert response.status_code == 302
        participation.refresh_from_db()
        assert participation.role == EventRole.CO_ADMIN

    def test_demote_co_admin(self, auth_client, active_event, user):
        other = User.objects.create_user(
            email="coadm@x.com", password="p1", display_name="CoAdm"
        )
        participation = EventParticipation.objects.create(
            event=active_event,
            user=other,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        response = auth_client.post(
            f"/events/{active_event.pk}/participants/{participation.pk}/demote/"
        )
        assert response.status_code == 302
        participation.refresh_from_db()
        assert participation.role == EventRole.PARTICIPANT

    def test_remove_participant(self, auth_client, active_event, user):
        other = User.objects.create_user(
            email="rem@x.com", password="p1", display_name="Rem"
        )
        participation = EventParticipation.objects.create(
            event=active_event,
            user=other,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        response = auth_client.post(
            f"/events/{active_event.pk}/participants/{participation.pk}/remove/"
        )
        assert response.status_code == 302
        participation.refresh_from_db()
        assert participation.access_status == AccessStatus.REMOVED

    def test_cannot_remove_self(self, auth_client, active_event, user):
        owner_participation = EventParticipation.objects.get(
            event=active_event, user=user
        )
        response = auth_client.post(
            f"/events/{active_event.pk}/participants/{owner_participation.pk}/remove/"
        )
        assert response.status_code == 302
        owner_participation.refresh_from_db()
        assert owner_participation.access_status == AccessStatus.ACCEPTED  # unchanged


class TestShareEventView:
    def test_share_requires_login(self, client, active_event):
        response = client.get(f"/events/{active_event.pk}/share/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_share_requires_participation(self, auth_client, user):
        from django.utils import timezone

        other = User.objects.create_user(
            email="shareowner@x.com", password="p1", display_name="Share Owner"
        )
        other.email_verified_at = timezone.now()
        other.save()
        event = Event.objects.create(
            owner_user=other, name="Not Mine", event_date=datetime.date(2026, 6, 1)
        )
        EventParticipation.objects.create(
            event=event, user=other, role=EventRole.OWNER, access_status=AccessStatus.ACCEPTED
        )
        response = auth_client.get(f"/events/{event.pk}/share/")
        assert response.status_code == 403

    def test_share_shows_link_and_qr(self, auth_client, active_event):
        response = auth_client.get(f"/events/{active_event.pk}/share/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Invitar amigos" in content
        assert str(active_event.public_share_token) in content
        assert "Descargar QR" in content

    def test_share_qr_returns_png(self, auth_client, active_event):
        response = auth_client.get(f"/events/{active_event.pk}/share/qr/")
        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert "attachment" in response["Content-Disposition"]


class TestPublicCardView:
    def test_public_card_requires_login(self, client, active_event):
        response = client.get(f"/events/join/{active_event.public_share_token}/")
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_public_card_shows_event_info(self, auth_client, user):
        from django.utils import timezone

        other = User.objects.create_user(
            email="pubowner@x.com", password="p1", display_name="Pub Owner"
        )
        other.email_verified_at = timezone.now()
        other.save()
        event = Event.objects.create(
            owner_user=other,
            name="Public Event",
            description="A great event",
            event_date=datetime.date(2026, 8, 15),
        )
        EventParticipation.objects.create(
            event=event, user=other, role=EventRole.OWNER, access_status=AccessStatus.ACCEPTED
        )
        response = auth_client.get(f"/events/join/{event.public_share_token}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Public Event" in content

    def test_public_card_redirects_if_already_participant(self, auth_client, active_event):
        response = auth_client.get(f"/events/join/{active_event.public_share_token}/")
        assert response.status_code == 302
        assert f"/events/{active_event.pk}/" in response.url


class TestAutoCloseIntegration:
    """Integration tests for the internal close-expired-events endpoint."""

    def test_close_endpoint_requires_token(self, client):
        response = client.post("/internal/close-expired-events/")
        assert response.status_code == 401

    def test_close_endpoint_rejects_wrong_token(self, client):
        response = client.post(
            "/internal/close-expired-events/",
            HTTP_X_INTERNAL_TOKEN="wrong-token",
        )
        assert response.status_code == 401

    def test_close_endpoint_closes_expired_events(self, client, user):
        from django.utils import timezone

        # Create event with past deadline
        past = timezone.now() - datetime.timedelta(hours=1)
        event = Event.objects.create(
            owner_user=user,
            name="Expired Event",
            event_date=datetime.date(2026, 1, 1),
            assignment_deadline_at=past,
            status=EventStatus.ACTIVE,
        )
        # Create event without deadline (should NOT be closed)
        Event.objects.create(
            owner_user=user,
            name="No Deadline",
            event_date=datetime.date(2026, 6, 1),
            status=EventStatus.ACTIVE,
        )

        from django.conf import settings

        response = client.post(
            "/internal/close-expired-events/",
            HTTP_X_INTERNAL_TOKEN=settings.INTERNAL_CRON_TOKEN,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["closed_count"] == 1

        event.refresh_from_db()
        assert event.status == EventStatus.CLOSED
