"""Tests for Phase 4 — Event Access (join requests, approval, leave)."""

import datetime

import pytest
from django.test import Client
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
from apps.events.services import (
    approve_request,
    correct_rejection,
    leave_event,
    reject_request,
    request_to_join,
)
from apps.items.models import EventItem, ItemAssignment

pytestmark = pytest.mark.django_db


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def user():
    """Owner user with verified email (can login)."""
    u = User.objects.create_user(
        email="owner@example.com",
        password="testpass1",
        display_name="Owner",
    )
    u.email_verified_at = timezone.now()
    u.save()
    return u


@pytest.fixture
def other_user():
    """Requester user with verified email."""
    u = User.objects.create_user(
        email="requester@example.com",
        password="testpass1",
        display_name="Requester",
    )
    u.email_verified_at = timezone.now()
    u.save()
    return u


@pytest.fixture
def third_user():
    """Third user with verified email."""
    u = User.objects.create_user(
        email="third@example.com",
        password="testpass1",
        display_name="Third User",
    )
    u.email_verified_at = timezone.now()
    u.save()
    return u


@pytest.fixture
def active_event(user):
    """Active event with owner participation row."""
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


@pytest.fixture
def closed_event(user):
    """Closed event."""
    event = Event.objects.create(
        owner_user=user,
        name="Closed Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.CLOSED,
        closed_at=timezone.now(),
    )
    EventParticipation.objects.create(
        event=event,
        user=user,
        role=EventRole.OWNER,
        access_status=AccessStatus.ACCEPTED,
    )
    return event


@pytest.fixture
def cancelled_event(user):
    """Cancelled event."""
    event = Event.objects.create(
        owner_user=user,
        name="Cancelled Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.CANCELLED,
        cancelled_at=timezone.now(),
    )
    EventParticipation.objects.create(
        event=event,
        user=user,
        role=EventRole.OWNER,
        access_status=AccessStatus.ACCEPTED,
    )
    return event


@pytest.fixture
def client():
    return Client()


# ─── Service Tests ───────────────────────────────────────────────────────────


class TestRequestToJoinService:
    """Tests for request_to_join service."""

    def test_happy_path_new_user(self, other_user, active_event):
        participation = request_to_join(other_user, active_event)

        assert participation.pk is not None
        assert participation.user == other_user
        assert participation.event == active_event
        assert participation.role == EventRole.PARTICIPANT
        assert participation.access_status == AccessStatus.PENDING
        assert participation.requested_at is not None

    def test_raises_on_closed_event(self, other_user, closed_event):
        with pytest.raises(ValueError, match="cerrado o cancelado"):
            request_to_join(other_user, closed_event)

    def test_raises_on_cancelled_event(self, other_user, cancelled_event):
        with pytest.raises(ValueError, match="cerrado o cancelado"):
            request_to_join(other_user, cancelled_event)

    def test_raises_if_already_pending(self, other_user, active_event):
        request_to_join(other_user, active_event)

        with pytest.raises(ValueError, match="solicitud activa"):
            request_to_join(other_user, active_event)

    def test_raises_if_already_accepted(self, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )

        with pytest.raises(ValueError, match="solicitud activa"):
            request_to_join(other_user, active_event)

    def test_raises_if_already_rejected(self, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )

        with pytest.raises(ValueError, match="solicitud activa"):
            request_to_join(other_user, active_event)

    def test_re_request_after_left(self, other_user, active_event):
        """A user who left can re-request → resets to pending."""
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.LEFT,
            left_at=timezone.now(),
        )

        participation = request_to_join(other_user, active_event)

        assert participation.access_status == AccessStatus.PENDING
        assert participation.role == EventRole.PARTICIPANT
        assert participation.requested_at is not None
        assert participation.left_at is None

    def test_re_request_after_removed(self, other_user, active_event):
        """A user who was removed can re-request → resets to pending."""
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.REMOVED,
            removed_at=timezone.now(),
        )

        participation = request_to_join(other_user, active_event)

        assert participation.access_status == AccessStatus.PENDING
        assert participation.role == EventRole.PARTICIPANT
        assert participation.removed_at is None


class TestApproveRejectService:
    """Tests for approve_request, reject_request, correct_rejection services."""

    @pytest.fixture
    def pending_participation(self, other_user, active_event):
        return EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )

    # approve_request

    def test_approve_happy_path(self, pending_participation):
        approve_request(pending_participation)
        pending_participation.refresh_from_db()

        assert pending_participation.access_status == AccessStatus.ACCEPTED
        assert pending_participation.responded_at is not None

    def test_approve_raises_if_not_pending(self, other_user, active_event):
        p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        with pytest.raises(ValueError, match="pendientes"):
            approve_request(p)

    # reject_request

    def test_reject_happy_path(self, pending_participation):
        reject_request(pending_participation)
        pending_participation.refresh_from_db()

        assert pending_participation.access_status == AccessStatus.REJECTED
        assert pending_participation.responded_at is not None

    def test_reject_raises_if_not_pending(self, other_user, active_event):
        p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.LEFT,
        )
        with pytest.raises(ValueError, match="pendientes"):
            reject_request(p)

    # correct_rejection

    def test_correct_rejection_happy_path(self, other_user, active_event):
        p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )

        correct_rejection(p)
        p.refresh_from_db()

        assert p.access_status == AccessStatus.ACCEPTED
        assert p.responded_at is not None

    def test_correct_rejection_raises_if_not_rejected(self, pending_participation):
        with pytest.raises(ValueError, match="rechazadas"):
            correct_rejection(pending_participation)


class TestLeaveEventService:
    """Tests for leave_event service."""

    @pytest.fixture
    def accepted_participation(self, other_user, active_event):
        return EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )

    def test_happy_path(self, accepted_participation):
        leave_event(accepted_participation)
        accepted_participation.refresh_from_db()

        assert accepted_participation.access_status == AccessStatus.LEFT
        assert accepted_participation.left_at is not None

    def test_raises_if_owner(self, user, active_event):
        owner_participation = EventParticipation.objects.get(
            event=active_event, user=user
        )
        with pytest.raises(ValueError, match="organizador"):
            leave_event(owner_participation)

    def test_raises_if_not_accepted(self, other_user, active_event):
        p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
        )
        with pytest.raises(ValueError, match="aceptados"):
            leave_event(p)

    def test_blocked_with_purchased_assignments(
        self, accepted_participation, active_event
    ):
        """Cannot leave if user has active (non-cancelled) purchases."""
        item = EventItem.objects.create(
            event=active_event,
            name="Carne",
            created_by_user=active_event.owner_user,
        )
        ItemAssignment.objects.create(
            item=item,
            user=accepted_participation.user,
            purchased_at=timezone.now(),
        )

        with pytest.raises(ValueError, match="compras registradas"):
            leave_event(accepted_participation)

        accepted_participation.refresh_from_db()
        assert accepted_participation.access_status == AccessStatus.ACCEPTED

    def test_allowed_with_cancelled_purchases(
        self, accepted_participation, active_event
    ):
        """Can leave if all purchases are cancelled."""
        item = EventItem.objects.create(
            event=active_event,
            name="Refrescos",
            created_by_user=active_event.owner_user,
        )
        ItemAssignment.objects.create(
            item=item,
            user=accepted_participation.user,
            purchased_at=timezone.now(),
            cancelled_at=timezone.now(),
        )

        leave_event(accepted_participation)
        accepted_participation.refresh_from_db()
        assert accepted_participation.access_status == AccessStatus.LEFT

    def test_co_admin_demoted_on_leave(self, other_user, active_event):
        """Co-admin role is demoted to participant before leaving."""
        p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )

        leave_event(p)
        p.refresh_from_db()

        assert p.access_status == AccessStatus.LEFT
        assert p.role == EventRole.PARTICIPANT
        assert p.left_at is not None


# ─── View Tests ──────────────────────────────────────────────────────────────


class TestPublicCardView:
    """Tests for public_card_view."""

    def test_anonymous_redirects_to_login(self, client, active_event):
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_shows_card_for_new_user(self, client, other_user, active_event):
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 200
        assert "event" in response.context
        assert response.context["can_join"] is True

    def test_redirects_accepted_to_detail(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 302
        assert f"/events/{active_event.pk}/" in response.url

    def test_redirects_pending_to_status(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 302
        assert "/status/" in response.url

    def test_redirects_rejected_to_status(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 302
        assert "/status/" in response.url

    def test_left_user_sees_card_again(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.LEFT,
            left_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["can_join"] is True

    def test_closed_event_shows_card_without_join(
        self, client, other_user, closed_event
    ):
        client.force_login(other_user)
        url = reverse(
            "events:public_card", kwargs={"token": closed_event.public_share_token}
        )
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["can_join"] is False


class TestRequestToJoinView:
    """Tests for request_to_join_view."""

    def test_anonymous_redirects_to_login(self, client, active_event):
        url = reverse(
            "events:request_to_join", kwargs={"token": active_event.public_share_token}
        )
        response = client.post(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_happy_path_creates_pending(self, client, other_user, active_event):
        client.force_login(other_user)
        url = reverse(
            "events:request_to_join", kwargs={"token": active_event.public_share_token}
        )
        response = client.post(url)

        assert response.status_code == 302
        assert "/status/" in response.url

        participation = EventParticipation.objects.get(
            event=active_event, user=other_user
        )
        assert participation.access_status == AccessStatus.PENDING

    def test_get_not_allowed(self, client, other_user, active_event):
        client.force_login(other_user)
        url = reverse(
            "events:request_to_join", kwargs={"token": active_event.public_share_token}
        )
        response = client.get(url)
        assert response.status_code == 405

    def test_error_redirects_to_public_card(self, client, other_user, active_event):
        """If request_to_join raises ValueError, redirect back to public card."""
        # Create existing pending participation to trigger error
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse(
            "events:request_to_join", kwargs={"token": active_event.public_share_token}
        )
        response = client.post(url)

        assert response.status_code == 302
        assert f"/join/{active_event.public_share_token}/" in response.url


class TestParticipationStatusView:
    """Tests for participation_status_view."""

    def test_anonymous_redirects_to_login(self, client, active_event):
        url = reverse("events:participation_status", kwargs={"pk": active_event.pk})
        response = client.get(url)
        assert response.status_code == 302
        assert "/login/" in response.url

    def test_pending_user_sees_status(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse("events:participation_status", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert "participation" in response.context
        assert response.context["participation"].access_status == AccessStatus.PENDING

    def test_rejected_user_sees_status(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse("events:participation_status", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert response.context["participation"].access_status == AccessStatus.REJECTED

    def test_accepted_user_redirects_to_detail(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(other_user)
        url = reverse("events:participation_status", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert f"/events/{active_event.pk}/" in response.url

    def test_left_user_redirects_to_public_card(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.LEFT,
            left_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse("events:participation_status", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 302
        assert f"/join/{active_event.public_share_token}/" in response.url


class TestManageRequestsView:
    """Tests for manage_requests_view (event_admin_required)."""

    def test_owner_can_access(self, client, user, active_event):
        client.force_login(user)
        url = reverse("events:manage_requests", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert "pending_requests" in response.context

    def test_co_admin_can_access(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(other_user)
        url = reverse("events:manage_requests", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 200

    def test_regular_participant_gets_403(self, client, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(other_user)
        url = reverse("events:manage_requests", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 403

    def test_non_participant_gets_403(self, client, other_user, active_event):
        client.force_login(other_user)
        url = reverse("events:manage_requests", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 403

    def test_lists_pending_requests(self, client, user, other_user, active_event):
        EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )
        client.force_login(user)
        url = reverse("events:manage_requests", kwargs={"pk": active_event.pk})
        response = client.get(url)

        assert response.status_code == 200
        assert len(response.context["pending_requests"]) == 1


class TestApproveRejectViews:
    """Tests for approve_request_view, reject_request_view, correct_rejection_view."""

    @pytest.fixture
    def pending_participation(self, other_user, active_event):
        return EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.PENDING,
            requested_at=timezone.now(),
        )

    # approve_request_view

    def test_approve_happy_path(
        self, client, user, active_event, pending_participation
    ):
        client.force_login(user)
        url = reverse(
            "events:approve_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url)

        assert response.status_code == 302
        pending_participation.refresh_from_db()
        assert pending_participation.access_status == AccessStatus.ACCEPTED

    def test_approve_htmx_returns_partial(
        self, client, user, active_event, pending_participation
    ):
        client.force_login(user)
        url = reverse(
            "events:approve_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        pending_participation.refresh_from_db()
        assert pending_participation.access_status == AccessStatus.ACCEPTED

    def test_approve_non_admin_gets_403(
        self, client, third_user, active_event, pending_participation
    ):
        client.force_login(third_user)
        url = reverse(
            "events:approve_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url)
        assert response.status_code == 403

    # reject_request_view

    def test_reject_happy_path(self, client, user, active_event, pending_participation):
        client.force_login(user)
        url = reverse(
            "events:reject_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url)

        assert response.status_code == 302
        pending_participation.refresh_from_db()
        assert pending_participation.access_status == AccessStatus.REJECTED

    def test_reject_htmx_returns_partial(
        self, client, user, active_event, pending_participation
    ):
        client.force_login(user)
        url = reverse(
            "events:reject_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        pending_participation.refresh_from_db()
        assert pending_participation.access_status == AccessStatus.REJECTED

    # correct_rejection_view

    def test_correct_rejection_happy_path(self, client, user, active_event, other_user):
        rejected = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )
        client.force_login(user)
        url = reverse(
            "events:correct_rejection",
            kwargs={"pk": active_event.pk, "participation_id": rejected.pk},
        )
        response = client.post(url)

        assert response.status_code == 302
        rejected.refresh_from_db()
        assert rejected.access_status == AccessStatus.ACCEPTED

    def test_correct_rejection_htmx(self, client, user, active_event, other_user):
        rejected = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.REJECTED,
            requested_at=timezone.now(),
            responded_at=timezone.now(),
        )
        client.force_login(user)
        url = reverse(
            "events:correct_rejection",
            kwargs={"pk": active_event.pk, "participation_id": rejected.pk},
        )
        response = client.post(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        rejected.refresh_from_db()
        assert rejected.access_status == AccessStatus.ACCEPTED

    def test_get_not_allowed_on_approve(
        self, client, user, active_event, pending_participation
    ):
        client.force_login(user)
        url = reverse(
            "events:approve_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.get(url)
        assert response.status_code == 405

    def test_co_admin_can_approve(
        self, client, third_user, active_event, pending_participation
    ):
        """Co-admin (not just owner) can approve requests."""
        EventParticipation.objects.create(
            event=active_event,
            user=third_user,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(third_user)
        url = reverse(
            "events:approve_request",
            kwargs={
                "pk": active_event.pk,
                "participation_id": pending_participation.pk,
            },
        )
        response = client.post(url)

        assert response.status_code == 302
        pending_participation.refresh_from_db()
        assert pending_participation.access_status == AccessStatus.ACCEPTED


class TestLeaveEventView:
    """Tests for leave_event_view."""

    @pytest.fixture
    def accepted_participation(self, other_user, active_event):
        return EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.PARTICIPANT,
            access_status=AccessStatus.ACCEPTED,
        )

    def test_happy_path_redirects_to_dashboard(
        self, client, other_user, active_event, accepted_participation
    ):
        client.force_login(other_user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.post(url)

        assert response.status_code == 302
        assert "/events/" in response.url
        accepted_participation.refresh_from_db()
        assert accepted_participation.access_status == AccessStatus.LEFT

    def test_owner_cannot_leave(self, client, user, active_event):
        client.force_login(user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.post(url)

        # participant_required passes (owner is accepted), but leave_event raises
        assert response.status_code == 302
        assert f"/events/{active_event.pk}/" in response.url

    def test_non_participant_gets_403(self, client, other_user, active_event):
        """User with no accepted participation gets 403 from participant_required."""
        client.force_login(other_user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.post(url)
        assert response.status_code == 403

    def test_get_not_allowed(
        self, client, other_user, active_event, accepted_participation
    ):
        client.force_login(other_user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.get(url)
        assert response.status_code == 405

    def test_leave_with_purchases_blocked(
        self, client, other_user, active_event, accepted_participation
    ):
        """Cannot leave if has active purchased assignments."""
        item = EventItem.objects.create(
            event=active_event,
            name="Carne",
            created_by_user=active_event.owner_user,
        )
        ItemAssignment.objects.create(
            item=item,
            user=other_user,
            purchased_at=timezone.now(),
        )
        client.force_login(other_user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.post(url)

        # Redirects back to detail with error message
        assert response.status_code == 302
        assert f"/events/{active_event.pk}/" in response.url
        accepted_participation.refresh_from_db()
        assert accepted_participation.access_status == AccessStatus.ACCEPTED

    def test_co_admin_leave_demotes(self, client, other_user, active_event):
        """Co-admin who leaves gets demoted to participant role."""
        co_admin_p = EventParticipation.objects.create(
            event=active_event,
            user=other_user,
            role=EventRole.CO_ADMIN,
            access_status=AccessStatus.ACCEPTED,
        )
        client.force_login(other_user)
        url = reverse("events:leave_event", kwargs={"pk": active_event.pk})
        response = client.post(url)

        assert response.status_code == 302
        co_admin_p.refresh_from_db()
        assert co_admin_p.access_status == AccessStatus.LEFT
        assert co_admin_p.role == EventRole.PARTICIPANT
