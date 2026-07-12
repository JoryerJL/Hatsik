import uuid

from django.conf import settings
from django.db import models

from apps.items.models import ItemUnit


class SuggestionStatus(models.TextChoices):
    PENDING_APPROVAL = "pending_approval", "Pending Approval"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"


class ItemSuggestion(models.Model):
    """A suggested item from a participant, pending owner/co-admin approval."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="suggestions",
    )
    suggested_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_suggestions",
    )
    name = models.CharField(max_length=255)
    quantity_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="NULL means binary suggestion.",
    )
    unit = models.CharField(
        max_length=20,
        choices=ItemUnit.choices,
        null=True,
        blank=True,
        help_text="Required only if quantity_total is set.",
    )
    status = models.CharField(
        max_length=20,
        choices=SuggestionStatus.choices,
        default=SuggestionStatus.PENDING_APPROVAL,
    )
    reviewed_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_suggestions",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_note = models.TextField(blank=True, null=True)
    converted_event_item = models.OneToOneField(
        "items.EventItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_suggestion_ref",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_suggestions"
        indexes = [
            models.Index(
                fields=["event", "status"],
                name="item_sugg_event_status_idx",
            ),
            models.Index(
                fields=["suggested_by_user"],
                name="item_sugg_by_user_idx",
            ),
        ]

    def __str__(self):
        return f"Suggestion: {self.name} ({self.status})"
