"""Views for item suggestion moderation."""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.events.decorators import event_admin_required, participant_required
from apps.moderation.forms import (
    ApproveSuggestionForm,
    EditSuggestionForm,
    RejectSuggestionForm,
    SuggestItemForm,
)
from apps.moderation.models import ItemSuggestion, SuggestionStatus
from apps.moderation.services import (
    ModerationError,
    approve_suggestion,
    delete_suggestion,
    edit_suggestion,
    reject_suggestion,
    suggest_item,
)


@login_required
@participant_required
def suggest_item_view(request, event, participation):
    """Suggest a new item for an event.

    GET: Render the suggestion modal fragment.
    POST: Validate and create the suggestion.
    """
    if request.method == "POST":
        form = SuggestItemForm(request.POST)
        if form.is_valid():
            try:
                suggest_item(
                    event,
                    request.user,
                    name=form.cleaned_data["name"],
                    quantity_total=form.cleaned_data.get("quantity_total"),
                    unit=form.cleaned_data.get("unit") or None,
                )
                if request.headers.get("HX-Request"):
                    response = HttpResponse("")
                    response["HX-Redirect"] = reverse(
                        "events:detail", kwargs={"pk": event.pk}
                    )
                    return response
                return redirect("events:detail", pk=event.pk)
            except ModerationError as e:
                form.add_error(None, str(e))
    else:
        form = SuggestItemForm()

    return render(
        request,
        "moderation/suggest-item.html",
        {"form": form, "event": event},
    )


@login_required
@participant_required
def edit_suggestion_view(request, event, participation, suggestion_pk):
    """Edit an own pending suggestion.

    GET: Render the edit suggestion modal fragment (pre-filled).
    POST: Validate and update the suggestion.
    """
    suggestion = get_object_or_404(
        ItemSuggestion,
        pk=suggestion_pk,
        event=event,
        suggested_by_user=request.user,
        status=SuggestionStatus.PENDING_APPROVAL,
    )

    if request.method == "POST":
        form = EditSuggestionForm(request.POST, instance=suggestion)
        if form.is_valid():
            try:
                edit_suggestion(
                    suggestion,
                    request.user,
                    name=form.cleaned_data["name"],
                    quantity_total=form.cleaned_data.get("quantity_total"),
                    unit=form.cleaned_data.get("unit") or None,
                )
                if request.headers.get("HX-Request"):
                    response = HttpResponse("")
                    response["HX-Redirect"] = reverse(
                        "events:detail", kwargs={"pk": event.pk}
                    )
                    return response
                return redirect("events:detail", pk=event.pk)
            except ModerationError as e:
                form.add_error(None, str(e))
    else:
        form = EditSuggestionForm(instance=suggestion)

    return render(
        request,
        "moderation/edit-suggestion.html",
        {"form": form, "event": event, "suggestion": suggestion},
    )


@login_required
@participant_required
def delete_suggestion_view(request, event, participation, suggestion_pk):
    """Delete an own pending suggestion (POST only).

    Returns an empty HTMX response on success for inline removal,
    or redirects for non-HTMX requests.
    """
    if request.method != "POST":
        return redirect("events:detail", pk=event.pk)

    suggestion = get_object_or_404(
        ItemSuggestion,
        pk=suggestion_pk,
        event=event,
        suggested_by_user=request.user,
        status=SuggestionStatus.PENDING_APPROVAL,
    )

    try:
        delete_suggestion(suggestion, request.user)
    except ModerationError as e:
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="text-error text-sm p-2">{e}</div>',
                status=422,
            )
        return redirect("events:detail", pk=event.pk)

    if request.headers.get("HX-Request"):
        return HttpResponse("")

    return redirect("events:detail", pk=event.pk)


@login_required
@event_admin_required
def approve_suggestion_view(request, event, suggestion_pk):
    """Approve a pending suggestion (admin only).

    GET: Render the approve modal fragment pre-filled from suggestion.
    POST: Validate and approve, creating an official item.
    """
    suggestion = get_object_or_404(
        ItemSuggestion,
        pk=suggestion_pk,
        event=event,
        status=SuggestionStatus.PENDING_APPROVAL,
    )

    if request.method == "POST":
        form = ApproveSuggestionForm(request.POST, instance=suggestion)
        if form.is_valid():
            try:
                approve_suggestion(
                    suggestion,
                    request.user,
                    name=form.cleaned_data["name"],
                    quantity_total=form.cleaned_data.get("quantity_total"),
                    unit=form.cleaned_data.get("unit") or None,
                )
                if request.headers.get("HX-Request"):
                    response = HttpResponse("")
                    response["HX-Redirect"] = reverse(
                        "events:detail", kwargs={"pk": event.pk}
                    )
                    return response
                return redirect("events:detail", pk=event.pk)
            except ModerationError as e:
                form.add_error(None, str(e))
    else:
        form = ApproveSuggestionForm(instance=suggestion)

    return render(
        request,
        "moderation/approve-suggestion.html",
        {"form": form, "event": event, "suggestion": suggestion},
    )


@login_required
@event_admin_required
def reject_suggestion_view(request, event, suggestion_pk):
    """Reject a pending suggestion (admin only, POST only).

    Returns an empty HTMX response on success or redirects.
    """
    if request.method != "POST":
        return redirect("events:detail", pk=event.pk)

    suggestion = get_object_or_404(
        ItemSuggestion,
        pk=suggestion_pk,
        event=event,
        status=SuggestionStatus.PENDING_APPROVAL,
    )

    rejection_note = request.POST.get("rejection_note", "")

    try:
        reject_suggestion(
            suggestion,
            request.user,
            rejection_note=rejection_note or None,
        )
    except ModerationError as e:
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="text-error text-sm p-2">{e}</div>',
                status=422,
            )
        return redirect("events:detail", pk=event.pk)

    if request.headers.get("HX-Request"):
        return HttpResponse("")

    return redirect("events:detail", pk=event.pk)
