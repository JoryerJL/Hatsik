"""Event views for Hatsik."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.events.decorators import (
    event_admin_required,
    event_owner_required,
    participant_required,
)
from apps.events.forms import CreateEventForm, EditEventForm
from apps.events.models import AccessStatus, EventParticipation
from apps.events.services import (
    approve_request,
    cancel_event,
    close_event,
    correct_rejection,
    create_event,
    demote_co_admin,
    leave_event,
    promote_to_co_admin,
    reject_request,
    remove_participant,
    reopen_event,
    request_to_join,
)


@login_required
@require_GET
def dashboard_view(request):
    """Display user's events dashboard."""
    participations = (
        EventParticipation.objects.filter(
            user=request.user,
            access_status=AccessStatus.ACCEPTED,
        )
        .select_related("event")
        .order_by("-event__created_at")
    )
    events_data = []
    for p in participations:
        pending_count = 0
        if p.role in ("owner", "co_admin"):
            pending_count = EventParticipation.objects.filter(
                event=p.event, access_status=AccessStatus.PENDING
            ).count()
        events_data.append(
            {
                "event": p.event,
                "role": p.role,
                "participation": p,
                "pending_count": pending_count,
            }
        )
    return render(
        request,
        "events/dashboard.html",
        {
            "events_data": events_data,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def create_event_view(request):
    """Create a new event."""
    if request.method == "POST":
        form = CreateEventForm(request.POST)
        if form.is_valid():
            event = create_event(
                user=request.user,
                name=form.cleaned_data["name"],
                event_date=form.cleaned_data["event_date"],
                description=form.cleaned_data.get("description"),
                assignment_deadline_at=form.cleaned_data.get("assignment_deadline_at"),
            )
            messages.success(request, "¡Evento creado exitosamente!")
            return redirect("events:detail", pk=event.pk)
    else:
        form = CreateEventForm()

    return render(request, "events/create-event.html", {"form": form})


@login_required
@participant_required
@require_GET
def event_detail_view(request, event, participation):
    """Display full event detail for accepted participants."""
    participants = (
        EventParticipation.objects.filter(
            event=event,
            access_status=AccessStatus.ACCEPTED,
        )
        .select_related("user")
        .order_by("created_at")
    )
    is_owner = request.user == event.owner_user
    is_admin = is_owner or participation.role == "co_admin"
    pending_count = 0
    pending_requests = []
    if is_admin:
        pending_qs = (
            EventParticipation.objects.filter(
                event=event, access_status=AccessStatus.PENDING
            )
            .select_related("user")
            .order_by("requested_at")
        )
        pending_requests = list(pending_qs)
        pending_count = len(pending_requests)
    return render(
        request,
        "events/event-detail.html",
        {
            "event": event,
            "participation": participation,
            "participants": participants,
            "is_owner": is_owner,
            "is_admin": is_admin,
            "pending_count": pending_count,
            "pending_requests": pending_requests,
        },
    )


@login_required
@event_owner_required
@require_http_methods(["GET", "POST"])
def edit_event_view(request, event):
    """Edit event details — Owner only."""
    if request.method == "POST":
        form = EditEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento actualizado.")
            return redirect("events:detail", pk=event.pk)
    else:
        form = EditEventForm(instance=event)

    return render(
        request,
        "events/edit-event.html",
        {
            "form": form,
            "event": event,
        },
    )


@login_required
@event_owner_required
@require_POST
def close_event_view(request, event):
    """Close an active event."""
    try:
        close_event(event)
        messages.success(request, "Evento cerrado.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@event_owner_required
@require_POST
def reopen_event_view(request, event):
    """Reopen a closed event."""
    try:
        reopen_event(event)
        messages.success(request, "Evento reabierto.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@event_owner_required
@require_POST
def cancel_event_view(request, event):
    """Cancel an event."""
    try:
        cancel_event(event)
        messages.success(request, "Evento cancelado.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@participant_required
@require_GET
def share_event_view(request, event, participation):
    """Display the share/invite page with link and QR."""
    share_url = request.build_absolute_uri(f"/events/join/{event.public_share_token}/")
    return render(
        request,
        "events/share-event.html",
        {
            "event": event,
            "share_url": share_url,
        },
    )


@login_required
@participant_required
@require_GET
def share_qr_view(request, event, participation):
    """Return QR code as downloadable PNG."""
    import io

    import qrcode

    share_url = request.build_absolute_uri(f"/events/join/{event.public_share_token}/")
    img = qrcode.make(share_url)
    buffer = io.BytesIO()
    img.save(buffer)
    buffer.seek(0)

    from django.http import HttpResponse

    return HttpResponse(
        buffer.getvalue(),
        content_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="hatsik-event-{event.pk}.png"'
        },
    )


@login_required
@event_owner_required
@require_POST
def remove_participant_view(request, event, participation_id):
    """Remove a participant from the event."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    if participation.user == request.user:
        messages.error(request, "No podés eliminarte a vos mismo.")
        return redirect("events:detail", pk=event.pk)
    try:
        remove_participant(participation)
        messages.success(request, "Participante eliminado.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@event_owner_required
@require_POST
def promote_participant_view(request, event, participation_id):
    """Promote a participant to co-admin."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    if participation.user == request.user:
        messages.error(request, "No podés promoverte a vos mismo.")
        return redirect("events:detail", pk=event.pk)
    try:
        promote_to_co_admin(participation)
        messages.success(request, "Participante promovido a co-admin.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@event_owner_required
@require_POST
def demote_participant_view(request, event, participation_id):
    """Demote a co-admin to participant."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    if participation.user == request.user:
        messages.error(request, "No podés degradarte a vos mismo.")
        return redirect("events:detail", pk=event.pk)
    try:
        demote_co_admin(participation)
        messages.success(request, "Co-admin degradado a participante.")
    except ValueError as e:
        messages.error(request, str(e))
    return redirect("events:detail", pk=event.pk)


@login_required
@require_GET
def public_card_view(request, token):
    """Public-facing event card accessed via share link.

    Handles multiple participation states:
    - No participation / left / removed → show join button
    - Pending / rejected → redirect to status page
    - Accepted → redirect to event detail
    - Closed/cancelled event → show card without join button
    """
    from apps.events.models import Event, EventStatus

    event = get_object_or_404(Event, public_share_token=token)

    existing = EventParticipation.objects.filter(
        event=event,
        user=request.user,
    ).first()

    if existing:
        if existing.access_status == AccessStatus.ACCEPTED:
            return redirect("events:detail", pk=event.pk)
        if existing.access_status in (AccessStatus.PENDING, AccessStatus.REJECTED):
            return redirect("events:participation_status", pk=event.pk)
        # LEFT or REMOVED — allow re-request (fall through to show card)

    # Determine if user can request to join
    can_join = event.status == EventStatus.ACTIVE

    return render(
        request,
        "events/event-card-public.html",
        {
            "event": event,
            "can_join": can_join,
        },
    )


@login_required
@require_POST
def request_to_join_view(request, token):
    """Handle join request submission."""
    from apps.events.models import Event

    event = get_object_or_404(Event, public_share_token=token)

    try:
        request_to_join(request.user, event)
        messages.success(
            request, "¡Solicitud enviada! El organizador revisará tu pedido."
        )
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("events:public_card", token=token)

    return redirect("events:participation_status", pk=event.pk)


@login_required
@require_GET
def participation_status_view(request, pk):
    """Show pending or rejected participation status."""
    from apps.events.models import Event

    event = get_object_or_404(Event, pk=pk)
    participation = EventParticipation.objects.filter(
        event=event,
        user=request.user,
    ).first()

    if not participation or participation.access_status == AccessStatus.ACCEPTED:
        return redirect("events:detail", pk=event.pk)

    if participation.access_status in (AccessStatus.LEFT, AccessStatus.REMOVED):
        return redirect("events:public_card", token=event.public_share_token)

    return render(
        request,
        "events/participation-status.html",
        {
            "event": event,
            "participation": participation,
        },
    )


@login_required
@event_admin_required
@require_GET
def manage_requests_view(request, event):
    """List pending (and rejected) requests for Owner/Co-admin."""
    pending = (
        EventParticipation.objects.filter(
            event=event,
            access_status=AccessStatus.PENDING,
        )
        .select_related("user")
        .order_by("requested_at")
    )
    rejected = (
        EventParticipation.objects.filter(
            event=event,
            access_status=AccessStatus.REJECTED,
        )
        .select_related("user")
        .order_by("-responded_at")[:10]
    )
    return render(
        request,
        "events/manage-requests.html",
        {
            "event": event,
            "pending_requests": pending,
            "rejected_requests": rejected,
        },
    )


@login_required
@event_admin_required
@require_POST
def approve_request_view(request, event, participation_id):
    """Approve a pending join request."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    try:
        approve_request(participation)
        messages.success(request, f"{participation.user.display_name} fue aceptado.")
    except ValueError as e:
        messages.error(request, str(e))

    # HTMX support: return partial if HTMX request
    if request.headers.get("HX-Request"):
        pending_count = EventParticipation.objects.filter(
            event=event, access_status=AccessStatus.PENDING
        ).count()
        return render(
            request,
            "events/partials/_request_row_empty.html",
            {"pending_count": pending_count},
        )
    return redirect("events:manage_requests", pk=event.pk)


@login_required
@event_admin_required
@require_POST
def reject_request_view(request, event, participation_id):
    """Reject a pending join request."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    try:
        reject_request(participation)
        messages.success(request, f"{participation.user.display_name} fue rechazado.")
    except ValueError as e:
        messages.error(request, str(e))

    # HTMX support
    if request.headers.get("HX-Request"):
        pending_count = EventParticipation.objects.filter(
            event=event, access_status=AccessStatus.PENDING
        ).count()
        return render(
            request,
            "events/partials/_request_row_empty.html",
            {"pending_count": pending_count},
        )
    return redirect("events:manage_requests", pk=event.pk)


@login_required
@event_admin_required
@require_POST
def correct_rejection_view(request, event, participation_id):
    """Correct a rejected request to accepted."""
    participation = get_object_or_404(
        EventParticipation, pk=participation_id, event=event
    )
    try:
        correct_rejection(participation)
        messages.success(
            request, f"{participation.user.display_name} fue aceptado (corrección)."
        )
    except ValueError as e:
        messages.error(request, str(e))

    if request.headers.get("HX-Request"):
        return render(request, "events/partials/_request_row_empty.html", {})
    return redirect("events:manage_requests", pk=event.pk)


@login_required
@participant_required
@require_POST
def leave_event_view(request, event, participation):
    """Leave an event voluntarily."""
    try:
        leave_event(participation)
        messages.success(request, "Abandonaste el evento.")
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("events:detail", pk=event.pk)
    return redirect("events:dashboard")
