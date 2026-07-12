from django.contrib import admin

from .models import Event, EventParticipation


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_user", "event_date", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ("event", "user", "role", "access_status", "created_at")
    list_filter = ("role", "access_status")
