"""URL configuration for the accounts app."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("verify-email/", views.verify_email_pending_view, name="verify_email_pending"),
    path(
        "verify-email/<str:token>/",
        views.verify_email_confirm_view,
        name="verify_email_confirm",
    ),
    path(
        "resend-verification/",
        views.resend_verification_view,
        name="resend_verification",
    ),
    path(
        "password-reset/",
        views.password_reset_request_view,
        name="password_reset_request",
    ),
    path(
        "password-reset/<str:token>/",
        views.password_reset_confirm_view,
        name="password_reset_confirm",
    ),
]
