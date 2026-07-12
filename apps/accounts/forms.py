"""Authentication forms for Hatsik."""

from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    """User registration form."""

    display_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"placeholder": "Your name", "autocomplete": "name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "email@example.com", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Min. 8 characters", "autocomplete": "new-password"}
        ),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Repeat password", "autocomplete": "new-password"}
        ),
        label="Confirm password",
    )

    def clean_email(self):
        """Normalize email to lowercase."""
        return self.cleaned_data["email"].lower().strip()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Las contraseñas no coinciden.")

        if password:
            try:
                password_validation.validate_password(password)
            except ValidationError as e:
                self.add_error("password", e)

        return cleaned_data


class LoginForm(forms.Form):
    """User login form."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "email@example.com", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "current-password"}
        ),
    )

    def clean_email(self):
        """Normalize email to lowercase."""
        return self.cleaned_data["email"].lower().strip()


class PasswordResetRequestForm(forms.Form):
    """Password reset request form — asks for email only."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"placeholder": "email@example.com", "autocomplete": "email"}
        ),
    )

    def clean_email(self):
        """Normalize email to lowercase."""
        return self.cleaned_data["email"].lower().strip()


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form — new password entry."""

    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "New password", "autocomplete": "new-password"}
        ),
        label="New password",
    )
    new_password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Repeat new password", "autocomplete": "new-password"}
        ),
        label="Confirm new password",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if (
            new_password
            and new_password_confirm
            and new_password != new_password_confirm
        ):
            self.add_error("new_password_confirm", "Las contraseñas no coinciden.")

        if new_password:
            try:
                password_validation.validate_password(new_password)
            except ValidationError as e:
                self.add_error("new_password", e)

        return cleaned_data
