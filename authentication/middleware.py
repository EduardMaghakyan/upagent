# authentication/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

from .two_factor_utils import is_two_factor_enabled, verify_two_factor_session
from .views import TWO_FACTOR_AUTH_SESSION_KEY, TWO_FACTOR_VERIFIED_SESSION_KEY


class TwoFactorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs that are always accessible, even when 2FA verification is required
        exempt_urls = [
            reverse("two_factor_verify"),
            reverse("two_factor_resend"),
            reverse("logout"),
        ]

        # Skip middleware for non-authenticated users or exempt URLs
        if not request.user.is_authenticated or request.path in exempt_urls:
            return self.get_response(request)

        # Check if user is in 2FA verification flow (has passed first auth step)
        if TWO_FACTOR_AUTH_SESSION_KEY in request.session:
            # Only allow access to 2FA verification pages or logout
            if request.path not in exempt_urls:
                messages.info(
                    request, "Please complete the two-factor authentication process."
                )
                return redirect("two_factor_verify")

        # Check if user has 2FA enabled but hasn't verified this session
        if is_two_factor_enabled(request.user):
            # Check if this session has been verified with 2FA
            session_verified = request.session.get(
                TWO_FACTOR_VERIFIED_SESSION_KEY, False
            )
            session_key = request.session.session_key

            # If not verified through session flag or the database, redirect to login
            if not session_verified and not verify_two_factor_session(
                request.user, session_key
            ):
                # Store user ID for 2FA flow and redirect to verification
                request.session[TWO_FACTOR_AUTH_SESSION_KEY] = request.user.id
                messages.info(request, "Please verify your identity to continue.")
                return redirect("two_factor_verify")

        return self.get_response(request)
