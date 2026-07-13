from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    # Dashboard
    path("", views.dashboard_view, name="dashboard"),
    path("create/", views.create_event_view, name="create"),
    path("<uuid:pk>/", views.event_detail_view, name="detail"),
    path("<uuid:pk>/edit/", views.edit_event_view, name="edit"),
    # Lifecycle
    path("<uuid:pk>/close/", views.close_event_view, name="close"),
    path("<uuid:pk>/reopen/", views.reopen_event_view, name="reopen"),
    path("<uuid:pk>/cancel/", views.cancel_event_view, name="cancel"),
    # Share
    path("<uuid:pk>/share/", views.share_event_view, name="share"),
    path("<uuid:pk>/share/qr/", views.share_qr_view, name="share_qr"),
    # Participants
    path(
        "<uuid:pk>/participants/<uuid:participation_id>/remove/",
        views.remove_participant_view,
        name="remove_participant",
    ),
    path(
        "<uuid:pk>/participants/<uuid:participation_id>/promote/",
        views.promote_participant_view,
        name="promote_participant",
    ),
    path(
        "<uuid:pk>/participants/<uuid:participation_id>/demote/",
        views.demote_participant_view,
        name="demote_participant",
    ),
    # Public
    path("join/<uuid:token>/", views.public_card_view, name="public_card"),
    path(
        "join/<uuid:token>/request/", views.request_to_join_view, name="request_to_join"
    ),
    # Participation status (pending/rejected)
    path(
        "<uuid:pk>/status/",
        views.participation_status_view,
        name="participation_status",
    ),
    # Request management (Owner/Co-admin)
    path("<uuid:pk>/requests/", views.manage_requests_view, name="manage_requests"),
    path(
        "<uuid:pk>/requests/<uuid:participation_id>/approve/",
        views.approve_request_view,
        name="approve_request",
    ),
    path(
        "<uuid:pk>/requests/<uuid:participation_id>/reject/",
        views.reject_request_view,
        name="reject_request",
    ),
    path(
        "<uuid:pk>/requests/<uuid:participation_id>/correct/",
        views.correct_rejection_view,
        name="correct_rejection",
    ),
    # Leave event
    path("<uuid:pk>/leave/", views.leave_event_view, name="leave_event"),
]
