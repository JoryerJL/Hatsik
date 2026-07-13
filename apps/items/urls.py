"""URL patterns for item management."""

from django.urls import path

from apps.items.views import add_item_view, delete_item_view, edit_item_view

app_name = "items"

urlpatterns = [
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
]
