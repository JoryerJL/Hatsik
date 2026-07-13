"""URL patterns for item suggestion moderation."""

from django.urls import path

from apps.moderation.views import (
    approve_suggestion_view,
    delete_suggestion_view,
    edit_suggestion_view,
    reject_suggestion_view,
    suggest_item_view,
)

app_name = "moderation"

urlpatterns = [
    path(
        "<uuid:pk>/suggestions/add/",
        suggest_item_view,
        name="suggest",
    ),
    path(
        "<uuid:pk>/suggestions/<uuid:suggestion_pk>/edit/",
        edit_suggestion_view,
        name="edit",
    ),
    path(
        "<uuid:pk>/suggestions/<uuid:suggestion_pk>/delete/",
        delete_suggestion_view,
        name="delete",
    ),
    path(
        "<uuid:pk>/suggestions/<uuid:suggestion_pk>/approve/",
        approve_suggestion_view,
        name="approve",
    ),
    path(
        "<uuid:pk>/suggestions/<uuid:suggestion_pk>/reject/",
        reject_suggestion_view,
        name="reject",
    ),
]
