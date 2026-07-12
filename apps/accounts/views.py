"""Authentication views for Hatsik."""

import hashlib
import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .emails import send_password_reset_email, send_verification_email
from .forms import (
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    RegisterForm,
)
from .models import EmailVerificationToken, PasswordResetToken, User

# ==============================================================
# Helpers
# ==============================================================

VERIFICATION_TOKEN_TTL = timedelta(hours=24)
PASSWORD_RESET_TOKEN_TTL = timedelta(hours=1)
RATE_LIMIT_SECONDS = 60


def _generate_token():
    """Generate a raw token and its SHA-256 hash."""
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token, token_hash


def _hash_token(raw_token):
    """Hash a raw token for lookup."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


def _is_rate_limited(key):
    """Check if an action is rate-limited."""
    return cache.get(key) is not None


def _set_rate_limit(key):
    """Set a rate limit marker."""
    cache.set(key, True, RATE_LIMIT_SECONDS)


# ==============================================================
# Registration
# ==============================================================


@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            # Check if email already exists — generic error to prevent enumeration
            if User.objects.filter(email=email).exists():
                form.add_error(None, "No se pudo crear la cuenta. Intentá de nuevo.")
                return render(request, "accounts/register.html", {"form": form})

            # Create user
            user = User.objects.create_user(
                email=email,
                password=form.cleaned_data["password"],
                display_name=form.cleaned_data["display_name"],
            )

            # Generate verification token
            raw_token, token_hash = _generate_token()
            EmailVerificationToken.objects.create(
                user=user,
                token_hash=token_hash,
                expires_at=timezone.now() + VERIFICATION_TOKEN_TTL,
            )

            # Send verification email
            verification_url = request.build_absolute_uri(f"/verify-email/{raw_token}/")
            send_verification_email(user, raw_token, verification_url)

            # Log in the user (unverified — middleware will contain them)
            login(request, user)
            return redirect("accounts:verify_email_pending")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


# ==============================================================
# Email Verification
# ==============================================================


@login_required
@require_GET
def verify_email_pending_view(request):
    """Show the 'check your email' pending verification screen."""
    if request.user.email_verified_at:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, "accounts/verify-email.html")


@require_GET
def verify_email_confirm_view(request, token):
    """Confirm email verification via token link."""
    token_hash = _hash_token(token)

    try:
        token_obj = EmailVerificationToken.objects.get(token_hash=token_hash)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "Enlace de verificación inválido.")
        return redirect("accounts:login")

    # Already consumed
    if token_obj.consumed_at:
        messages.info(request, "Este enlace ya fue utilizado. Iniciá sesión.")
        return redirect("accounts:login")

    # Expired
    if timezone.now() > token_obj.expires_at:
        messages.error(
            request,
            "Este enlace de verificación expiró. Solicitá uno nuevo.",
        )
        if request.user.is_authenticated:
            return redirect("accounts:verify_email_pending")
        return redirect("accounts:login")

    # Verify the user
    user = token_obj.user
    user.email_verified_at = timezone.now()
    user.save(update_fields=["email_verified_at"])

    # Consume the token
    token_obj.consumed_at = timezone.now()
    token_obj.save(update_fields=["consumed_at"])

    messages.success(request, "¡Email verificado! Bienvenido a Hatsik.")

    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect("accounts:login")


@login_required
@require_POST
def resend_verification_view(request):
    """Resend verification email (rate-limited, HTMX-compatible)."""
    user = request.user

    if user.email_verified_at:
        return redirect(settings.LOGIN_REDIRECT_URL)

    rate_key = f"ratelimit:resend_verification:{user.id}"

    if _is_rate_limited(rate_key):
        if request.htmx:
            return render(
                request,
                "accounts/partials/_resend_button.html",
                {"rate_limited": True},
            )
        messages.warning(request, "Esperá un momento antes de solicitar otro email.")
        return redirect("accounts:verify_email_pending")

    # Invalidate old tokens (don't delete — just let them expire)
    # Generate new token
    raw_token, token_hash = _generate_token()
    EmailVerificationToken.objects.create(
        user=user,
        token_hash=token_hash,
        expires_at=timezone.now() + VERIFICATION_TOKEN_TTL,
    )

    # Send email
    verification_url = request.build_absolute_uri(f"/verify-email/{raw_token}/")
    send_verification_email(user, raw_token, verification_url)

    # Set rate limit
    _set_rate_limit(rate_key)

    if request.htmx:
        return render(
            request,
            "accounts/partials/_resend_button.html",
            {"rate_limited": True, "sent": True},
        )

    messages.success(request, "¡Email de verificación enviado!")
    return redirect("accounts:verify_email_pending")


# ==============================================================
# Login & Logout
# ==============================================================


@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        if request.user.email_verified_at:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return redirect("accounts:verify_email_pending")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                # Respect ?next= parameter
                next_url = request.GET.get("next") or request.POST.get("next")
                if user.email_verified_at:
                    return redirect(next_url or settings.LOGIN_REDIRECT_URL)
                return redirect("accounts:verify_email_pending")
            else:
                form.add_error(None, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": request.GET.get("next", ""),
        },
    )


@login_required
@require_POST
def logout_view(request):
    """User logout."""
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


# ==============================================================
# Password Recovery
# ==============================================================


@require_http_methods(["GET", "POST"])
def password_reset_request_view(request):
    """Password reset request — always shows generic success."""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            rate_key = f"ratelimit:password_reset:{hashlib.sha256(email.encode()).hexdigest()[:16]}"

            if not _is_rate_limited(rate_key):
                try:
                    user = User.objects.get(email=email)
                    raw_token, token_hash = _generate_token()
                    PasswordResetToken.objects.create(
                        user=user,
                        token_hash=token_hash,
                        expires_at=timezone.now() + PASSWORD_RESET_TOKEN_TTL,
                    )
                    reset_url = request.build_absolute_uri(
                        f"/password-reset/{raw_token}/"
                    )
                    send_password_reset_email(user, raw_token, reset_url)
                except User.DoesNotExist:
                    pass  # Don't reveal email existence

                _set_rate_limit(rate_key)

            # Always show success — even if rate-limited or email doesn't exist
            messages.success(
                request,
                "Si este correo existe en nuestro sistema, enviamos un enlace para restablecer tu contraseña.",
            )
            return redirect("accounts:password_reset_request")
    else:
        form = PasswordResetRequestForm()

    return render(request, "accounts/password-reset.html", {"form": form})


@require_http_methods(["GET", "POST"])
def password_reset_confirm_view(request, token):
    """Password reset confirmation — set new password."""
    token_hash = _hash_token(token)

    try:
        token_obj = PasswordResetToken.objects.get(token_hash=token_hash)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "Enlace de recuperación inválido o expirado.")
        return redirect("accounts:password_reset_request")

    # Already consumed
    if token_obj.consumed_at:
        messages.error(request, "Este enlace de recuperación ya fue utilizado.")
        return redirect("accounts:password_reset_request")

    # Expired
    if timezone.now() > token_obj.expires_at:
        messages.error(
            request,
            "Este enlace expiró. Solicitá uno nuevo.",
        )
        return redirect("accounts:password_reset_request")

    if request.method == "POST":
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user = token_obj.user
            user.set_password(form.cleaned_data["new_password"])
            user.save(update_fields=["password"])

            # Consume token
            token_obj.consumed_at = timezone.now()
            token_obj.save(update_fields=["consumed_at"])

            messages.success(
                request,
                "Contraseña restablecida correctamente. Iniciá sesión con tu nueva contraseña.",
            )
            return redirect("accounts:login")
    else:
        form = PasswordResetConfirmForm()

    return render(
        request,
        "accounts/password-reset-confirm.html",
        {
            "form": form,
            "token": token,
        },
    )
