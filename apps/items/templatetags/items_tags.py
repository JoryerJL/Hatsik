"""Template tags for item status rendering."""

from django import template

from apps.items.services import (
    STATUS_BOUGHT,
    STATUS_COLORS,
    STATUS_COVERED,
    STATUS_LABELS,
    STATUS_PARTIALLY_BOUGHT,
    STATUS_PARTIALLY_COVERED,
    STATUS_UNASSIGNED,
    get_computed_status_from_annotations,
)

register = template.Library()


@register.simple_tag
def item_status(item):
    """Return status string from annotated item."""
    return get_computed_status_from_annotations(item)


@register.simple_tag
def item_status_color(item):
    """Return status color hex from annotated item."""
    status = get_computed_status_from_annotations(item)
    return STATUS_COLORS.get(status, "#E5E7EB")


@register.simple_tag
def item_status_label(item):
    """Return human-readable status label."""
    status = get_computed_status_from_annotations(item)
    return STATUS_LABELS.get(status, "Desconocido")


@register.simple_tag
def item_status_css_class(item):
    """Return Tailwind CSS class for status background."""
    status = get_computed_status_from_annotations(item)
    mapping = {
        STATUS_UNASSIGNED: "state-unassigned",
        STATUS_PARTIALLY_COVERED: "state-partial",
        STATUS_COVERED: "state-covered",
        STATUS_PARTIALLY_BOUGHT: "state-partial-bought",
        STATUS_BOUGHT: "state-bought",
    }
    return mapping.get(status, "surface-container")
