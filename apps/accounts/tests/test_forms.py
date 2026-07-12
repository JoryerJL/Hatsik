"""Tests for authentication forms."""

from apps.accounts.forms import (
    LoginForm,
    PasswordResetConfirmForm,
    PasswordResetRequestForm,
    RegisterForm,
)


class TestRegisterForm:
    """Tests for the registration form."""

    def test_valid_data(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "test@example.com",
                "password": "secure1pass",
                "password_confirm": "secure1pass",
            }
        )
        assert form.is_valid(), form.errors

    def test_email_normalized_to_lowercase(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "TEST@EXAMPLE.COM",
                "password": "secure1pass",
                "password_confirm": "secure1pass",
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["email"] == "test@example.com"

    def test_passwords_must_match(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "test@example.com",
                "password": "secure1pass",
                "password_confirm": "different1pass",
            }
        )
        assert not form.is_valid()
        assert "password_confirm" in form.errors

    def test_password_too_short(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "test@example.com",
                "password": "ab1",
                "password_confirm": "ab1",
            }
        )
        assert not form.is_valid()
        assert "password" in form.errors

    def test_password_missing_number(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "test@example.com",
                "password": "abcdefgh",
                "password_confirm": "abcdefgh",
            }
        )
        assert not form.is_valid()
        assert "password" in form.errors

    def test_password_missing_letter(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "test@example.com",
                "password": "12345678",
                "password_confirm": "12345678",
            }
        )
        assert not form.is_valid()
        assert "password" in form.errors

    def test_required_fields(self):
        form = RegisterForm(data={})
        assert not form.is_valid()
        assert "display_name" in form.errors
        assert "email" in form.errors
        assert "password" in form.errors
        assert "password_confirm" in form.errors

    def test_invalid_email_format(self):
        form = RegisterForm(
            data={
                "display_name": "Test User",
                "email": "not-an-email",
                "password": "secure1pass",
                "password_confirm": "secure1pass",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors


class TestLoginForm:
    """Tests for the login form."""

    def test_valid_data(self):
        form = LoginForm(data={"email": "test@example.com", "password": "anything"})
        assert form.is_valid(), form.errors

    def test_email_normalized(self):
        form = LoginForm(data={"email": "TEST@EXAMPLE.COM", "password": "anything"})
        assert form.is_valid()
        assert form.cleaned_data["email"] == "test@example.com"

    def test_required_fields(self):
        form = LoginForm(data={})
        assert not form.is_valid()
        assert "email" in form.errors
        assert "password" in form.errors

    def test_invalid_email_format(self):
        form = LoginForm(data={"email": "not-valid", "password": "test"})
        assert not form.is_valid()
        assert "email" in form.errors


class TestPasswordResetRequestForm:
    """Tests for the password reset request form."""

    def test_valid_email(self):
        form = PasswordResetRequestForm(data={"email": "user@example.com"})
        assert form.is_valid(), form.errors

    def test_email_normalized(self):
        form = PasswordResetRequestForm(data={"email": "USER@Example.Com"})
        assert form.is_valid()
        assert form.cleaned_data["email"] == "user@example.com"

    def test_required_email(self):
        form = PasswordResetRequestForm(data={})
        assert not form.is_valid()
        assert "email" in form.errors

    def test_invalid_email(self):
        form = PasswordResetRequestForm(data={"email": "bad"})
        assert not form.is_valid()
        assert "email" in form.errors


class TestPasswordResetConfirmForm:
    """Tests for the password reset confirm form."""

    def test_valid_data(self):
        form = PasswordResetConfirmForm(
            data={
                "new_password": "newsecure1",
                "new_password_confirm": "newsecure1",
            }
        )
        assert form.is_valid(), form.errors

    def test_passwords_must_match(self):
        form = PasswordResetConfirmForm(
            data={
                "new_password": "newsecure1",
                "new_password_confirm": "different1",
            }
        )
        assert not form.is_valid()
        assert "new_password_confirm" in form.errors

    def test_password_validation_runs(self):
        form = PasswordResetConfirmForm(
            data={
                "new_password": "short",
                "new_password_confirm": "short",
            }
        )
        assert not form.is_valid()
        assert "new_password" in form.errors

    def test_required_fields(self):
        form = PasswordResetConfirmForm(data={})
        assert not form.is_valid()
        assert "new_password" in form.errors
        assert "new_password_confirm" in form.errors
