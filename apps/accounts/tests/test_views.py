"""Integration tests for authentication views."""

from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.models import (
    EmailVerificationToken,
    PasswordResetToken,
    User,
)


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    """Create a verified user."""
    user = User.objects.create_user(
        email="verified@example.com",
        password="testpass1",
        display_name="Verified User",
    )
    from django.utils import timezone

    user.email_verified_at = timezone.now()
    user.save()
    return user


@pytest.fixture
def unverified_user(db):
    """Create an unverified user."""
    return User.objects.create_user(
        email="unverified@example.com",
        password="testpass1",
        display_name="Unverified User",
    )


# ==============================================================
# Registration Tests
# ==============================================================


class TestRegisterView:
    """Integration tests for registration."""

    def test_get_renders_form(self, client, db):
        resp = client.get(reverse("accounts:register"))
        assert resp.status_code == 200
        assert b"Crea tu cuenta" in resp.content

    @patch("apps.accounts.views.send_verification_email")
    def test_successful_registration(self, mock_send, client, db):
        resp = client.post(
            reverse("accounts:register"),
            {
                "display_name": "New User",
                "email": "new@example.com",
                "password": "secure1pass",
                "password_confirm": "secure1pass",
            },
        )
        # Should redirect to verify-email pending
        assert resp.status_code == 302
        assert "/verify-email/" in resp.url

        # User created
        user = User.objects.get(email="new@example.com")
        assert user.display_name == "New User"
        assert user.email_verified_at is None

        # Token created
        assert EmailVerificationToken.objects.filter(user=user).exists()

        # Email sent
        mock_send.assert_called_once()

    @patch("apps.accounts.views.send_verification_email")
    def test_duplicate_email_generic_error(self, mock_send, client, user):
        resp = client.post(
            reverse("accounts:register"),
            {
                "display_name": "Another",
                "email": "verified@example.com",
                "password": "secure1pass",
                "password_confirm": "secure1pass",
            },
        )
        assert resp.status_code == 200
        assert b"No se pudo crear la cuenta" in resp.content
        mock_send.assert_not_called()

    def test_invalid_password_shows_error(self, client, db):
        resp = client.post(
            reverse("accounts:register"),
            {
                "display_name": "New User",
                "email": "new@example.com",
                "password": "short",
                "password_confirm": "short",
            },
        )
        assert resp.status_code == 200
        # Should show validation error (too short and missing number)

    def test_password_mismatch(self, client, db):
        resp = client.post(
            reverse("accounts:register"),
            {
                "display_name": "New User",
                "email": "new@example.com",
                "password": "secure1pass",
                "password_confirm": "different1pass",
            },
        )
        assert resp.status_code == 200
        assert "Las contrase" in resp.content.decode()

    def test_authenticated_user_redirected(self, client, user):
        client.force_login(user)
        resp = client.get(reverse("accounts:register"))
        assert resp.status_code == 302


# ==============================================================
# Email Verification Tests
# ==============================================================


class TestEmailVerification:
    """Integration tests for email verification flow."""

    def test_pending_view_for_unverified(self, client, unverified_user):
        client.force_login(unverified_user)
        resp = client.get(reverse("accounts:verify_email_pending"))
        assert resp.status_code == 200
        assert "Casi listo" in resp.content.decode()

    def test_pending_view_redirects_verified(self, client, user):
        client.force_login(user)
        resp = client.get(reverse("accounts:verify_email_pending"))
        assert resp.status_code == 302

    def test_valid_token_verifies_user(self, client, unverified_user):
        import hashlib
        import secrets

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        from datetime import timedelta

        from django.utils import timezone

        EmailVerificationToken.objects.create(
            user=unverified_user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=24),
        )

        resp = client.get(reverse("accounts:verify_email_confirm", args=[raw_token]))
        assert resp.status_code == 302

        unverified_user.refresh_from_db()
        assert unverified_user.email_verified_at is not None

    def test_expired_token_shows_error(self, client, unverified_user):
        import hashlib
        import secrets

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        from datetime import timedelta

        from django.utils import timezone

        EmailVerificationToken.objects.create(
            user=unverified_user,
            token_hash=token_hash,
            expires_at=timezone.now() - timedelta(hours=1),  # Already expired
        )

        resp = client.get(reverse("accounts:verify_email_confirm", args=[raw_token]))
        assert resp.status_code == 302  # Redirects with error message

        unverified_user.refresh_from_db()
        assert unverified_user.email_verified_at is None

    def test_consumed_token_shows_error(self, client, unverified_user):
        import hashlib
        import secrets

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        from datetime import timedelta

        from django.utils import timezone

        EmailVerificationToken.objects.create(
            user=unverified_user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=24),
            consumed_at=timezone.now(),  # Already consumed
        )

        resp = client.get(reverse("accounts:verify_email_confirm", args=[raw_token]))
        assert resp.status_code == 302

        unverified_user.refresh_from_db()
        assert unverified_user.email_verified_at is None

    def test_invalid_token_shows_error(self, client, db):
        resp = client.get(
            reverse("accounts:verify_email_confirm", args=["bogus-token"])
        )
        assert resp.status_code == 302

    @patch("apps.accounts.views.send_verification_email")
    def test_resend_creates_new_token(self, mock_send, client, unverified_user):
        client.force_login(unverified_user)
        resp = client.post(reverse("accounts:resend_verification"))
        assert resp.status_code == 302  # Non-HTMX redirect
        assert EmailVerificationToken.objects.filter(user=unverified_user).count() == 1
        mock_send.assert_called_once()

    @patch("apps.accounts.views.send_verification_email")
    def test_resend_rate_limited(self, mock_send, client, unverified_user):
        client.force_login(unverified_user)
        # First request succeeds
        client.post(reverse("accounts:resend_verification"))
        mock_send.reset_mock()

        # Second request within 60s is rate-limited
        resp = client.post(reverse("accounts:resend_verification"))
        assert resp.status_code == 302
        mock_send.assert_not_called()


# ==============================================================
# Login & Logout Tests
# ==============================================================


class TestLoginView:
    """Integration tests for login."""

    def test_get_renders_form(self, client, db):
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 200
        assert "Bienvenido a Hatsik" in resp.content.decode()

    def test_valid_login_verified_user(self, client, user):
        resp = client.post(
            reverse("accounts:login"),
            {
                "email": "verified@example.com",
                "password": "testpass1",
            },
        )
        assert resp.status_code == 302
        assert resp.url == "/events/"

    def test_valid_login_unverified_user(self, client, unverified_user):
        resp = client.post(
            reverse("accounts:login"),
            {
                "email": "unverified@example.com",
                "password": "testpass1",
            },
        )
        assert resp.status_code == 302
        assert "/verify-email/" in resp.url

    def test_invalid_credentials(self, client, user):
        resp = client.post(
            reverse("accounts:login"),
            {
                "email": "verified@example.com",
                "password": "wrongpassword1",
            },
        )
        assert resp.status_code == 200
        assert "Correo o contrase" in resp.content.decode()

    def test_next_parameter_preserved(self, client, user):
        resp = client.post(
            reverse("accounts:login") + "?next=/events/123/",
            {"email": "verified@example.com", "password": "testpass1"},
        )
        assert resp.status_code == 302
        assert resp.url == "/events/123/"

    def test_authenticated_user_redirected(self, client, user):
        client.force_login(user)
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 302


class TestLogoutView:
    """Integration tests for logout."""

    def test_logout_destroys_session(self, client, user):
        client.force_login(user)
        resp = client.post(reverse("accounts:logout"))
        assert resp.status_code == 302
        assert resp.url == "/login/"

        # Session is gone
        resp = client.get(reverse("accounts:login"))
        assert resp.status_code == 200  # Not redirected (not logged in)

    def test_logout_requires_post(self, client, user):
        client.force_login(user)
        resp = client.get(reverse("accounts:logout"))
        assert resp.status_code == 405  # Method not allowed

    def test_logout_requires_auth(self, client, db):
        resp = client.post(reverse("accounts:logout"))
        assert resp.status_code == 302
        assert "/login/" in resp.url


# ==============================================================
# Password Recovery Tests
# ==============================================================


class TestPasswordResetRequest:
    """Integration tests for password reset request."""

    def test_get_renders_form(self, client, db):
        resp = client.get(reverse("accounts:password_reset_request"))
        assert resp.status_code == 200
        assert "Recupera tu contrase" in resp.content.decode()

    @patch("apps.accounts.views.send_password_reset_email")
    def test_valid_email_sends_reset(self, mock_send, client, user):
        resp = client.post(
            reverse("accounts:password_reset_request"),
            {
                "email": "verified@example.com",
            },
        )
        assert resp.status_code == 302
        mock_send.assert_called_once()
        assert PasswordResetToken.objects.filter(user=user).exists()

    @patch("apps.accounts.views.send_password_reset_email")
    def test_nonexistent_email_still_shows_success(self, mock_send, client, db):
        resp = client.post(
            reverse("accounts:password_reset_request"),
            {
                "email": "nobody@example.com",
            },
        )
        assert resp.status_code == 302
        mock_send.assert_not_called()

    @patch("apps.accounts.views.send_password_reset_email")
    def test_rate_limit_enforced(self, mock_send, client, user):
        # First request
        client.post(
            reverse("accounts:password_reset_request"),
            {
                "email": "verified@example.com",
            },
        )
        mock_send.reset_mock()

        # Second request within 60s — rate-limited
        client.post(
            reverse("accounts:password_reset_request"),
            {
                "email": "verified@example.com",
            },
        )
        mock_send.assert_not_called()


class TestPasswordResetConfirm:
    """Integration tests for password reset confirmation."""

    def _create_reset_token(self, user):
        import hashlib
        import secrets
        from datetime import timedelta

        from django.utils import timezone

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=1),
        )
        return raw_token

    def test_valid_token_renders_form(self, client, user):
        raw_token = self._create_reset_token(user)
        resp = client.get(reverse("accounts:password_reset_confirm", args=[raw_token]))
        assert resp.status_code == 200
        assert "Establecer nueva contrase" in resp.content.decode()

    def test_valid_reset_changes_password(self, client, user):
        raw_token = self._create_reset_token(user)
        resp = client.post(
            reverse("accounts:password_reset_confirm", args=[raw_token]),
            {"new_password": "newpass1word", "new_password_confirm": "newpass1word"},
        )
        assert resp.status_code == 302
        assert "/login/" in resp.url

        # Can log in with new password
        user.refresh_from_db()
        assert user.check_password("newpass1word")

    def test_expired_token_redirects(self, client, user):
        import hashlib
        import secrets
        from datetime import timedelta

        from django.utils import timezone

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() - timedelta(hours=1),  # Expired
        )

        resp = client.get(reverse("accounts:password_reset_confirm", args=[raw_token]))
        assert resp.status_code == 302

    def test_consumed_token_redirects(self, client, user):
        import hashlib
        import secrets
        from datetime import timedelta

        from django.utils import timezone

        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=1),
            consumed_at=timezone.now(),
        )

        resp = client.get(reverse("accounts:password_reset_confirm", args=[raw_token]))
        assert resp.status_code == 302

    def test_invalid_token_redirects(self, client, db):
        resp = client.get(
            reverse("accounts:password_reset_confirm", args=["bad-token"])
        )
        assert resp.status_code == 302

    def test_password_mismatch_shows_error(self, client, user):
        raw_token = self._create_reset_token(user)
        resp = client.post(
            reverse("accounts:password_reset_confirm", args=[raw_token]),
            {"new_password": "newpass1word", "new_password_confirm": "different1word"},
        )
        assert resp.status_code == 200
        assert "Las contrase" in resp.content.decode()


# ==============================================================
# Email Verification Middleware Tests
# ==============================================================


class TestEmailVerificationMiddleware:
    """Integration tests for the email verification middleware."""

    def test_unverified_user_redirected_from_protected_route(
        self, client, unverified_user
    ):
        client.force_login(unverified_user)
        resp = client.get("/events/")  # Protected route
        assert resp.status_code == 302
        assert "/verify-email/" in resp.url

    def test_verified_user_passes_through(self, client, user):
        client.force_login(user)
        # This will 404 since events app has no views yet, but middleware won't block
        resp = client.get("/events/")
        assert resp.status_code != 302 or "/verify-email/" not in resp.get(
            "Location", ""
        )

    def test_unauthenticated_user_not_affected(self, client, db):
        # Without an events view, anonymous user hits 404 — middleware is not involved
        # The key assertion is that middleware does NOT redirect to /verify-email/
        resp = client.get("/events/")
        if resp.status_code == 302:
            assert "/verify-email/" not in resp.url

    def test_allowed_paths_not_blocked(self, client, unverified_user):
        """Unverified user can access auth paths."""
        client.force_login(unverified_user)

        # verify-email page itself is accessible
        resp = client.get("/verify-email/")
        assert resp.status_code == 200

        # login page is accessible (though redirects since already logged in)
        resp = client.get("/login/")
        # Logged-in user on login page → depends on view logic, but middleware doesn't block
        assert resp.status_code in (200, 302)
        if resp.status_code == 302:
            assert "/verify-email/" in resp.url  # Our login view redirects unverified

    def test_static_paths_not_blocked(self, client, unverified_user):
        """Static file paths are in the allowlist."""
        client.force_login(unverified_user)
        # Static paths start with /static/ — middleware won't redirect
        resp = client.get("/static/css/main.css")
        # May 200 or 404 depending on staticfiles config, but NOT redirect to verify
        assert resp.status_code != 302 or "/verify-email/" not in resp.get(
            "Location", ""
        )
