"""Access control decorators for event views."""

import functools

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from apps.events.models import AccessStatus, Event, EventParticipation


def event_owner_required(view_func):
    """Require that request.user is the event owner.

    Fetches Event by `pk` kwarg, returns 403 if user is not the owner.
    Injects `event` into kwargs for the wrapped view.
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.pop("pk")
        event = get_object_or_404(Event, pk=pk)
        if request.user != event.owner_user:
            return HttpResponseForbidden()
        kwargs["event"] = event
        return view_func(request, *args, **kwargs)

    return wrapper


def event_admin_required(view_func):
    """Require that request.user is the event owner or an accepted co-admin.

    Fetches Event by `pk` kwarg, verifies user is owner or has an
    EventParticipation with role='co_admin' and access_status='accepted'.
    Returns 403 if neither condition is met.
    Injects `event` into kwargs for the wrapped view.
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.pop("pk")
        event = get_object_or_404(Event, pk=pk)
        if request.user == event.owner_user:
            kwargs["event"] = event
            return view_func(request, *args, **kwargs)
        # Check if co-admin
        is_co_admin = EventParticipation.objects.filter(
            event=event,
            user=request.user,
            role="co_admin",
            access_status=AccessStatus.ACCEPTED,
        ).exists()
        if is_co_admin:
            kwargs["event"] = event
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return wrapper


def participant_required(view_func):
    """Require that request.user is an accepted participant of the event.

    Fetches Event by `pk` kwarg, verifies user has an EventParticipation
    with access_status='accepted'. Returns 403 if not.
    Injects `event` and `participation` into kwargs for the wrapped view.
    """

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        pk = kwargs.pop("pk")
        event = get_object_or_404(Event, pk=pk)
        participation = (
            EventParticipation.objects.filter(
                event=event,
                user=request.user,
                access_status=AccessStatus.ACCEPTED,
            )
            .select_related("event")
            .first()
        )
        if participation is None:
            return HttpResponseForbidden()
        kwargs["event"] = event
        kwargs["participation"] = participation
        return view_func(request, *args, **kwargs)

    return wrapper
