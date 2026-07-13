"""Views for item management and assignments."""

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.events.decorators import event_owner_required, participant_required
from apps.items.forms import (
    AddItemForm,
    ClaimItemForm,
    EditAssignmentForm,
    EditItemForm,
)
from apps.items.models import EventItem, ItemAssignment
from apps.items.services import (
    ItemError,
    add_item,
    cancel_assignment,
    claim_item,
    compute_event_progress,
    delete_item,
    edit_item,
    get_available_quantity,
    get_items_with_status,
    mark_as_purchased,
    modify_assignment,
)

# --- Item Management Views (Owner) ---


@login_required
@event_owner_required
def add_item_view(request, event):
    """Add a new item to an event's shopping list.

    GET: Render the add item modal fragment.
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
                if request.headers.get("HX-Request"):
                    response = HttpResponse("")
                    response["HX-Redirect"] = reverse(
                        "events:detail", kwargs={"pk": event.pk}
                    )
                    return response
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

    GET: Render the edit item modal fragment (pre-filled).
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
                if request.headers.get("HX-Request"):
                    response = HttpResponse("")
                    response["HX-Redirect"] = reverse(
                        "events:detail", kwargs={"pk": event.pk}
                    )
                    return response
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


# --- Assignment Views (Participants) ---


def _render_item_row_response(request, event, item):
    """Render the updated item row partial with HX-Trigger for progress update."""
    # Re-fetch item with annotations
    items_qs = get_items_with_status(event).filter(pk=item.pk)
    annotated_item = items_qs.first()

    # Get assignments for this item
    assignments = ItemAssignment.objects.filter(
        item=item, cancelled_at__isnull=True
    ).select_related("user")

    is_owner = event.owner_user == request.user
    is_admin = is_owner or event.participations.filter(
        user=request.user, role="co_admin", access_status="accepted"
    ).exists()

    available = get_available_quantity(item)

    response = render(
        request,
        "items/partials/_item_row.html",
        {
            "item": annotated_item,
            "event": event,
            "is_owner": is_owner,
            "is_admin": is_admin,
            "assignments": assignments,
            "available_quantity": available,
        },
    )
    response["HX-Trigger"] = "progress-updated"
    return response


@login_required
@participant_required
def claim_item_view(request, event, participation, item_pk):
    """Claim an item (or portion).

    GET: Return claim form fragment.
    POST: Create the assignment.
    """
    item = get_object_or_404(EventItem, pk=item_pk, event=event)
    is_quantified = item.quantity_total is not None

    if request.method == "POST":
        form = ClaimItemForm(request.POST, is_quantified=is_quantified)
        if form.is_valid():
            try:
                quantity = form.cleaned_data.get("quantity_assigned")
                claim_item(item, request.user, quantity_assigned=quantity)

                if request.headers.get("HX-Request"):
                    return _render_item_row_response(request, event, item)
                return redirect("events:detail", pk=event.pk)
            except ItemError as e:
                form.add_error(None, str(e))
    else:
        form = ClaimItemForm(is_quantified=is_quantified)

    available = get_available_quantity(item)
    return render(
        request,
        "items/claim-item.html",
        {
            "form": form,
            "event": event,
            "item": item,
            "is_quantified": is_quantified,
            "available_quantity": available,
        },
    )


@login_required
@participant_required
def edit_assignment_view(request, event, participation, assignment_pk):
    """Edit own assignment quantity.

    GET: Return edit form fragment.
    POST: Modify the assignment.
    """
    assignment = get_object_or_404(
        ItemAssignment, pk=assignment_pk, item__event=event
    )
    item = assignment.item

    if request.method == "POST":
        form = EditAssignmentForm(request.POST)
        if form.is_valid():
            try:
                modify_assignment(
                    assignment,
                    request.user,
                    quantity_assigned=form.cleaned_data["quantity_assigned"],
                )
                if request.headers.get("HX-Request"):
                    return _render_item_row_response(request, event, item)
                return redirect("events:detail", pk=event.pk)
            except ItemError as e:
                form.add_error(None, str(e))
    else:
        form = EditAssignmentForm(
            initial={"quantity_assigned": assignment.quantity_assigned}
        )

    # Available = max they could set (excluding their current amount)
    others_sum = (
        ItemAssignment.objects.filter(item=item, cancelled_at__isnull=True)
        .exclude(pk=assignment.pk)
        .aggregate(total=Sum("quantity_assigned"))["total"]
        or Decimal("0")
    )
    available = item.quantity_total - others_sum if item.quantity_total else None

    return render(
        request,
        "items/edit-assignment.html",
        {
            "form": form,
            "event": event,
            "item": item,
            "assignment": assignment,
            "available_quantity": available,
        },
    )


@login_required
@participant_required
def cancel_assignment_view(request, event, participation, assignment_pk):
    """Cancel an assignment (POST only)."""
    if request.method != "POST":
        return redirect("events:detail", pk=event.pk)

    assignment = get_object_or_404(
        ItemAssignment, pk=assignment_pk, item__event=event
    )
    item = assignment.item

    try:
        cancel_assignment(assignment, request.user)
    except ItemError as e:
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="text-error text-sm p-2">{e}</div>',
                status=422,
            )
        return redirect("events:detail", pk=event.pk)

    if request.headers.get("HX-Request"):
        return _render_item_row_response(request, event, item)
    return redirect("events:detail", pk=event.pk)


@login_required
@participant_required
def purchase_assignment_view(request, event, participation, assignment_pk):
    """Mark an assignment as purchased (POST only)."""
    if request.method != "POST":
        return redirect("events:detail", pk=event.pk)

    assignment = get_object_or_404(
        ItemAssignment, pk=assignment_pk, item__event=event
    )
    item = assignment.item

    try:
        mark_as_purchased(assignment, request.user)
    except ItemError as e:
        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="text-error text-sm p-2">{e}</div>',
                status=422,
            )
        return redirect("events:detail", pk=event.pk)

    if request.headers.get("HX-Request"):
        return _render_item_row_response(request, event, item)
    return redirect("events:detail", pk=event.pk)


@login_required
@participant_required
def progress_bar_view(request, event, participation):
    """Return the progress bar partial (for HTMX refresh)."""
    progress = compute_event_progress(event)
    return render(
        request,
        "items/partials/_progress_bar.html",
        {"event": event, "progress": progress},
    )
