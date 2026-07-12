import uuid

from django.conf import settings
from django.db import models


class EventStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CLOSED = "closed", "Closed"
    CANCELLED = "cancelled", "Cancelled"


class EventRole(models.TextChoices):
    OWNER = "owner", "Owner"
    CO_ADMIN = "co_admin", "Co-admin"
    PARTICIPANT = "participant", "Participant"


class AccessStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    REJECTED = "rejected", "Rejected"
    LEFT = "left", "Left"
    REMOVED = "removed", "Removed"


class Event(models.Model):
    """An event (convivio) owned by a user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_events",
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField()
    assignment_deadline_at = models.DateTimeField(blank=True, null=True)
    public_share_token = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.ACTIVE,
    )
    closed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "events"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class EventParticipation(models.Model):
    """Tracks a user's participation status in an event."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participations",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_participations",
    )
    role = models.CharField(max_length=20, choices=EventRole.choices)
    access_status = models.CharField(max_length=20, choices=AccessStatus.choices)
    requested_at = models.DateTimeField(blank=True, null=True)
    responded_at = models.DateTimeField(blank=True, null=True)
    left_at = models.DateTimeField(blank=True, null=True)
    removed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_participations"
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="event_participations_event_user_key",
            ),
        ]
        indexes = [
            models.Index(
                fields=["event", "access_status"],
                name="evt_part_event_status_idx",
            ),
            models.Index(
                fields=["user"],
                name="evt_part_user_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.event} ({self.access_status})"
