"""Views for item management."""

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.events.decorators import event_owner_required
from apps.items.forms import AddItemForm, EditItemForm
from apps.items.models import EventItem, ItemAssignment
from apps.items.services import ItemError, add_item, delete_item, edit_item


@login_required
@event_owner_required
def add_item_view(request, event):
    """Add a new item to an event's shopping list.

    GET: Render the add item form.
    POST: Validate and create the item.
    """
    if request.method == "POST":
        form = AddItemForm(request.POST)
        if form.is_valid():
            try:
                add_item(
                    event,
                    request.user,
                    name=form.cleaned_data["name"],
                    quantity_total=form.cleaned_data.get("quantity_total"),
                    unit=form.cleaned_data.get("unit") or None,
                )
                return redirect("events:detail", pk=event.pk)
            except ItemError as e:
                form.add_error(None, str(e))
    else:
        form = AddItemForm()

    return render(
        request,
        "items/add-item.html",
        {"form": form, "event": event},
    )


@login_required
@event_owner_required
def edit_item_view(request, event, item_pk):
    """Edit an existing item.

    GET: Render the edit form (pre-filled).
    POST: Validate and update the item.
    """
    item = get_object_or_404(EventItem, pk=item_pk, event=event)
    has_assignments = ItemAssignment.objects.filter(
        item=item, cancelled_at__isnull=True
    ).exists()

    if request.method == "POST":
        form = EditItemForm(
            request.POST, instance=item, has_assignments=has_assignments
        )
        if form.is_valid():
            try:
                edit_item(
                    item,
                    request.user,
                    name=form.cleaned_data.get("name"),
                    quantity_total=form.cleaned_data.get("quantity_total"),
                    unit=form.cleaned_data.get("unit") or None,
                )
                return redirect("events:detail", pk=event.pk)
            except ItemError as e:
                form.add_error(None, str(e))
    else:
        form = EditItemForm(instance=item, has_assignments=has_assignments)

    return render(
        request,
        "items/edit-item.html",
        {
            "form": form,
            "event": event,
            "item": item,
            "has_assignments": has_assignments,
        },
    )


@login_required
@event_owner_required
def delete_item_view(request, event, item_pk):
    """Delete an item (POST only).

    Returns an empty HTMX response on success for inline removal,
    or redirects for non-HTMX requests.
    """
    if request.method != "POST":
        return redirect("events:detail", pk=event.pk)

    item = get_object_or_404(EventItem, pk=item_pk, event=event)

    try:
        delete_item(item, request.user)
    except ItemError as e:
        # For HTMX: return error message
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="text-error text-sm p-2">{e}</div>',
                status=422,
            )
        return redirect("events:detail", pk=event.pk)

    if request.headers.get("HX-Request"):
        return HttpResponse("")

    return redirect("events:detail", pk=event.pk)
