from django.contrib import admin

from .models import EventItem, ItemAssignment


@admin.register(EventItem)
class EventItemAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "quantity_total", "unit", "created_at")
    list_filter = ("unit",)
    search_fields = ("name",)


@admin.register(ItemAssignment)
class ItemAssignmentAdmin(admin.ModelAdmin):
    list_display = ("item", "user", "quantity_assigned", "purchased_at", "cancelled_at")
    list_filter = ("purchased_at", "cancelled_at")
