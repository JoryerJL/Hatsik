from django.urls import path

from . import views

app_name = "internal"

urlpatterns = [
    path(
        "close-expired-events/", views.close_expired_events, name="close_expired_events"
    ),
]
