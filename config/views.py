"""Project-level views (not tied to any specific app module)."""

from django.shortcuts import redirect, render


def landing_view(request):
    """Public landing page. Redirects authenticated users to the dashboard."""
    if request.user.is_authenticated:
        return redirect("events:dashboard")
    return render(request, "landing.html")
