from django.contrib import admin

from .models import ItemSuggestion


@admin.register(ItemSuggestion)
class ItemSuggestionAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "suggested_by_user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("name",)
