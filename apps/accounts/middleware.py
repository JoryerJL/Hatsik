"""Custom middleware for Hatsik authentication."""

from django.shortcuts import redirect
from django.urls import reverse


class EmailVerificationMiddleware:
    """
    Redirect authenticated-but-unverified users to the verification pending page.

    Must be placed AFTER AuthenticationMiddleware in the middleware stack.
    """

    # Paths that unverified users are allowed to access
    ALLOWED_PATHS = [
        "/login/",
        "/register/",
        "/logout/",
        "/verify-email/",
        "/resend-verification/",
        "/password-reset/",
        "/static/",
        "/admin/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_redirect(request):
            return redirect(reverse("accounts:verify_email_pending"))
        return self.get_response(request)

    def _should_redirect(self, request):
        """Check if request should be redirected to verification."""
        # Only applies to authenticated users
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return False

        # Only unverified users
        if request.user.email_verified_at is not None:
            return False

        # Allow staff to bypass (admin access)
        if request.user.is_staff:
            return False

        # Check if the path is in the allowlist
        path = request.path
        for allowed in self.ALLOWED_PATHS:
            if path.startswith(allowed):
                return False

        return True
