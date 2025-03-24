# Update authentication/urls.py to include new 2FA paths

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Two-factor authentication paths
    path("two-factor/verify/", views.two_factor_verify_view, name="two_factor_verify"),
    path(
        "two-factor/resend/", views.two_factor_resend_otp_view, name="two_factor_resend"
    ),
    path(
        "two-factor/settings/",
        views.two_factor_settings_view,
        name="two_factor_settings",
    ),
    # Password reset paths with rate limiting
    path(
        "password-reset/",
        views.RateLimitedPasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="authentication/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.RateLimitedPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="authentication/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
