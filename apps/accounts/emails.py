"""
Transactional email utilities using Resend SDK.

Wraps Resend API calls so the email provider is swappable in the future.
"""

import resend
from django.conf import settings


def _get_resend_client():
    """Initialize Resend with the API key from settings."""
    resend.api_key = settings.RESEND_API_KEY


def send_verification_email(user, token: str, verification_url: str) -> dict:
    """
    Send email verification link to a newly registered user.

    Args:
        user: User instance with email and display_name.
        token: Raw verification token (NOT the hash).
        verification_url: Full URL the user clicks to verify.

    Returns:
        Resend API response dict.
    """
    _get_resend_client()

    html_body = f"""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h1 style="font-family: 'Nunito', sans-serif; color: #E8432D; font-size: 24px; margin-bottom: 16px;">
            Welcome to Hatsik!
        </h1>
        <p style="color: #404040; font-size: 14px; line-height: 1.6;">
            Hi {user.display_name},<br><br>
            Please verify your email address by clicking the button below:
        </p>
        <a href="{verification_url}"
           style="display: inline-block; margin: 24px 0; padding: 12px 24px;
                  background-color: #E8432D; color: white; text-decoration: none;
                  border-radius: 12px; font-weight: 600; font-size: 14px;">
            Verify Email
        </a>
        <p style="color: #737373; font-size: 12px;">
            This link expires in 24 hours. If you didn't create an account, ignore this email.
        </p>
    </div>
    """

    text_body = (
        f"Hi {user.display_name},\n\n"
        f"Please verify your email by visiting: {verification_url}\n\n"
        f"This link expires in 24 hours.\n"
        f"If you didn't create an account, ignore this email."
    )

    return resend.Emails.send(
        {
            "from": "Hatsik <noreply@hatsik.com>",
            "to": [user.email],
            "subject": "Verify your Hatsik account",
            "html": html_body,
            "text": text_body,
        }
    )


def send_password_reset_email(user, token: str, reset_url: str) -> dict:
    """
    Send password reset link to a user.

    Args:
        user: User instance with email and display_name.
        token: Raw reset token (NOT the hash).
        reset_url: Full URL the user clicks to reset password.

    Returns:
        Resend API response dict.
    """
    _get_resend_client()

    html_body = f"""
    <div style="font-family: 'Plus Jakarta Sans', sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
        <h1 style="font-family: 'Nunito', sans-serif; color: #E8432D; font-size: 24px; margin-bottom: 16px;">
            Reset your password
        </h1>
        <p style="color: #404040; font-size: 14px; line-height: 1.6;">
            Hi {user.display_name},<br><br>
            Someone requested a password reset for your Hatsik account. Click below to set a new password:
        </p>
        <a href="{reset_url}"
           style="display: inline-block; margin: 24px 0; padding: 12px 24px;
                  background-color: #E8432D; color: white; text-decoration: none;
                  border-radius: 12px; font-weight: 600; font-size: 14px;">
            Reset Password
        </a>
        <p style="color: #737373; font-size: 12px;">
            This link expires in 1 hour. If you didn't request this, ignore this email.
        </p>
    </div>
    """

    text_body = (
        f"Hi {user.display_name},\n\n"
        f"Reset your password by visiting: {reset_url}\n\n"
        f"This link expires in 1 hour.\n"
        f"If you didn't request this, ignore this email."
    )

    return resend.Emails.send(
        {
            "from": "Hatsik <noreply@hatsik.com>",
            "to": [user.email],
            "subject": "Reset your Hatsik password",
            "html": html_body,
            "text": text_body,
        }
    )
