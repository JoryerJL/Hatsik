import uuid

from django.conf import settings
from django.db import models


class ItemUnit(models.TextChoices):
    KG = "kg", "Kilogramos"
    G = "g", "Gramos"
    LITERS = "liters", "Litros"
    ML = "ml", "Mililitros"
    PIECES = "pieces", "Piezas"
    PACKAGES = "packages", "Paquetes"
    BAGS = "bags", "Bolsas"
    BOXES = "boxes", "Cajas"
    CANS = "cans", "Latas"
    BOTTLES = "bottles", "Botellas"
    JUGS = "jugs", "Garrafones"
    TRAYS = "trays", "Charolas"
    DOZENS = "dozens", "Docenas"


class EventItem(models.Model):
    """An item on an event's shopping list."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="items",
    )
    source_suggestion = models.OneToOneField(
        "moderation.ItemSuggestion",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="converted_item",
    )
    name = models.CharField(max_length=255)
    quantity_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="NULL means binary item (no quantity).",
    )
    unit = models.CharField(
        max_length=20,
        choices=ItemUnit.choices,
        null=True,
        blank=True,
        help_text="Required only if quantity_total is set.",
    )
    created_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "event_items"
        indexes = [
            models.Index(
                fields=["event"],
                name="event_items_event_idx",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.event.name})"


class ItemAssignment(models.Model):
    """Assignment of an item (or portion) to a user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey(
        EventItem,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="item_assignments",
    )
    quantity_assigned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Required only for quantified items. Must be > 0.",
    )
    purchased_at = models.DateTimeField(null=True, blank=True)
    purchased_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="marked_purchases",
    )
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_assignments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "item_assignments"
        constraints = [
            # Partial unique: one active assignment per user per item
            models.UniqueConstraint(
                fields=["item", "user"],
                condition=models.Q(cancelled_at__isnull=True),
                name="item_assignments_item_user_key",
            ),
        ]
        indexes = [
            models.Index(
                fields=["item"],
                name="item_assignments_item_idx",
            ),
            models.Index(
                fields=["user"],
                name="item_assignments_user_idx",
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.item.name}"
