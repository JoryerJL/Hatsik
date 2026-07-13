"""URL patterns for item management."""

from django.urls import path

from apps.items.views import (
    add_item_view,
    cancel_assignment_view,
    claim_item_view,
    delete_item_view,
    edit_assignment_view,
    edit_item_view,
    progress_bar_view,
    purchase_assignment_view,
)

app_name = "items"

urlpatterns = [
    # Item management (owner)
    path(
        "<uuid:pk>/items/add/",
        add_item_view,
        name="add",
    ),
    path(
        "<uuid:pk>/items/<uuid:item_pk>/edit/",
        edit_item_view,
        name="edit",
    ),
    path(
        "<uuid:pk>/items/<uuid:item_pk>/delete/",
        delete_item_view,
        name="delete",
    ),
    # Assignment actions (participants)
    path(
        "<uuid:pk>/items/<uuid:item_pk>/claim/",
        claim_item_view,
        name="claim",
    ),
    path(
        "<uuid:pk>/assignments/<uuid:assignment_pk>/edit/",
        edit_assignment_view,
        name="edit_assignment",
    ),
    path(
        "<uuid:pk>/assignments/<uuid:assignment_pk>/cancel/",
        cancel_assignment_view,
        name="cancel_assignment",
    ),
    path(
        "<uuid:pk>/assignments/<uuid:assignment_pk>/purchase/",
        purchase_assignment_view,
        name="purchase_assignment",
    ),
    # Progress bar partial
    path(
        "<uuid:pk>/progress/",
        progress_bar_view,
        name="progress",
    ),
]
