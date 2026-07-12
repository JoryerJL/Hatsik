"""
Development-only views for testing UI components and HTMX.

These views are only available when DEBUG=True.
"""

from django.http import HttpResponse
from django.shortcuts import render


def component_gallery_view(request):
    """Render the component gallery page."""
    return render(request, "dev/components.html")


def htmx_test_view(request):
    """Return a simple HTML fragment to test HTMX is working."""
    return HttpResponse(
        '<span class="text-green-600 font-semibold">✓ HTMX is working!</span>'
    )
