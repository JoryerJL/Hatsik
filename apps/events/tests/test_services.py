"""Tests for event services."""

import datetime

import pytest
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
    cancel_event,
    close_event,
    close_expired_events,
    create_event,
    demote_co_admin,
    promote_to_co_admin,
    remove_participant,
    reopen_event,
)
from apps.items.models import EventItem, ItemAssignment

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(
        email="owner@example.com",
        password="testpass1",
        display_name="Owner",
    )


@pytest.fixture
def other_user():
    return User.objects.create_user(
        email="other@example.com",
        password="testpass1",
        display_name="Other User",
    )


@pytest.fixture
def active_event(user):
    return Event.objects.create(
        owner_user=user,
        name="Test Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.ACTIVE,
    )


@pytest.fixture
def closed_event(user):
    return Event.objects.create(
        owner_user=user,
        name="Closed Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.CLOSED,
        closed_at=timezone.now(),
    )


@pytest.fixture
def cancelled_event(user):
    return Event.objects.create(
        owner_user=user,
        name="Cancelled Event",
        event_date=datetime.date(2026, 12, 25),
        status=EventStatus.CANCELLED,
        cancelled_at=timezone.now(),
    )


@pytest.fixture
def participation(active_event, other_user):
    return EventParticipation.objects.create(
        event=active_event,
        user=other_user,
        role=EventRole.PARTICIPANT,
        access_status=AccessStatus.ACCEPTED,
    )


class TestCreateEvent:
    """Tests for create_event service."""

    def test_happy_path(self, user):
        event = create_event(
            user,
            name="Parrillada",
            event_date=datetime.date(2026, 8, 15),
            description="Carne asada con los amigos",
        )

        assert event.pk is not None
        assert event.name == "Parrillada"
        assert event.owner_user == user
        assert event.event_date == datetime.date(2026, 8, 15)
        assert event.description == "Carne asada con los amigos"
        assert event.status == EventStatus.ACTIVE

        # Owner participation should be auto-created
        participation = EventParticipation.objects.get(event=event, user=user)
        assert participation.role == EventRole.OWNER
        assert participation.access_status == AccessStatus.ACCEPTED

    def test_creates_with_assignment_deadline(self, user):
        deadline = timezone.now() + datetime.timedelta(days=5)
        event = create_event(
            user,
            name="Evento",
            event_date=datetime.date(2026, 9, 1),
            assignment_deadline_at=deadline,
        )
        assert event.assignment_deadline_at == deadline


class TestCloseEvent:
    """Tests for close_event service."""

    def test_happy_path(self, active_event):
        close_event(active_event)
        active_event.refresh_from_db()

        assert active_event.status == EventStatus.CLOSED
        assert active_event.closed_at is not None

    def test_raises_on_cancelled(self, cancelled_event):
        with pytest.raises(ValueError, match="Cannot close a cancelled event"):
            close_event(cancelled_event)


class TestReopenEvent:
    """Tests for reopen_event service."""

    def test_happy_path(self, closed_event):
        reopen_event(closed_event)
        closed_event.refresh_from_db()

        assert closed_event.status == EventStatus.ACTIVE
        assert closed_event.closed_at is None

    def test_raises_on_cancelled(self, cancelled_event):
        with pytest.raises(ValueError, match="Cannot reopen a cancelled event"):
            reopen_event(cancelled_event)


class TestCancelEvent:
    """Tests for cancel_event service."""

    def test_happy_path(self, active_event):
        cancel_event(active_event)
        active_event.refresh_from_db()

        assert active_event.status == EventStatus.CANCELLED
        assert active_event.cancelled_at is not None

    def test_raises_on_already_cancelled(self, cancelled_event):
        with pytest.raises(ValueError, match="Event is already cancelled"):
            cancel_event(cancelled_event)


class TestPromoteToCoadmin:
    """Tests for promote_to_co_admin service."""

    def test_happy_path(self, participation):
        assert participation.role == EventRole.PARTICIPANT

        promote_to_co_admin(participation)
        participation.refresh_from_db()

        assert participation.role == EventRole.CO_ADMIN


class TestDemoteCoadmin:
    """Tests for demote_co_admin service."""

    def test_happy_path(self, participation):
        participation.role = EventRole.CO_ADMIN
        participation.save()

        demote_co_admin(participation)
        participation.refresh_from_db()

        assert participation.role == EventRole.PARTICIPANT


class TestRemoveParticipant:
    """Tests for remove_participant service."""

    def test_happy_path(self, participation):
        remove_participant(participation)
        participation.refresh_from_db()

        assert participation.access_status == AccessStatus.REMOVED
        assert participation.removed_at is not None

    def test_blocked_with_purchased_assignments(self, active_event, participation):
        """Cannot remove a participant who has purchased items."""
        item = EventItem.objects.create(
            event=active_event,
            name="Carne",
            created_by_user=active_event.owner_user,
        )
        ItemAssignment.objects.create(
            item=item,
            user=participation.user,
            purchased_at=timezone.now(),
        )

        with pytest.raises(ValueError, match="purchased assignments"):
            remove_participant(participation)

        # Status unchanged
        participation.refresh_from_db()
        assert participation.access_status == AccessStatus.ACCEPTED

    def test_allowed_with_cancelled_assignment(self, active_event, participation):
        """Can remove if all purchased assignments are cancelled."""
        item = EventItem.objects.create(
            event=active_event,
            name="Refrescos",
            created_by_user=active_event.owner_user,
        )
        ItemAssignment.objects.create(
            item=item,
            user=participation.user,
            purchased_at=timezone.now(),
            cancelled_at=timezone.now(),
        )

        # Should not raise — cancelled assignments don't block removal
        remove_participant(participation)
        participation.refresh_from_db()
        assert participation.access_status == AccessStatus.REMOVED


class TestCloseExpiredEvents:
    """Tests for close_expired_events service."""

    def test_closes_expired_events(self, user):
        past_deadline = timezone.now() - datetime.timedelta(hours=1)
        event = Event.objects.create(
            owner_user=user,
            name="Expired Event",
            event_date=datetime.date(2026, 12, 25),
            status=EventStatus.ACTIVE,
            assignment_deadline_at=past_deadline,
        )

        count = close_expired_events()

        assert count == 1
        event.refresh_from_db()
        assert event.status == EventStatus.CLOSED
        assert event.closed_at is not None

    def test_ignores_events_without_deadline(self, active_event):
        """Events without assignment_deadline_at should not be closed."""
        assert active_event.assignment_deadline_at is None

        count = close_expired_events()

        assert count == 0
        active_event.refresh_from_db()
        assert active_event.status == EventStatus.ACTIVE

    def test_ignores_future_deadline(self, user):
        future_deadline = timezone.now() + datetime.timedelta(hours=24)
        Event.objects.create(
            owner_user=user,
            name="Future Event",
            event_date=datetime.date(2026, 12, 25),
            status=EventStatus.ACTIVE,
            assignment_deadline_at=future_deadline,
        )

        count = close_expired_events()
        assert count == 0

    def test_ignores_already_closed_events(self, user):
        past_deadline = timezone.now() - datetime.timedelta(hours=1)
        Event.objects.create(
            owner_user=user,
            name="Already Closed",
            event_date=datetime.date(2026, 12, 25),
            status=EventStatus.CLOSED,
            closed_at=timezone.now(),
            assignment_deadline_at=past_deadline,
        )

        count = close_expired_events()
        assert count == 0

    def test_ignores_cancelled_events(self, user):
        past_deadline = timezone.now() - datetime.timedelta(hours=1)
        Event.objects.create(
            owner_user=user,
            name="Cancelled",
            event_date=datetime.date(2026, 12, 25),
            status=EventStatus.CANCELLED,
            cancelled_at=timezone.now(),
            assignment_deadline_at=past_deadline,
        )

        count = close_expired_events()
        assert count == 0
