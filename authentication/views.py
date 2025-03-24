from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from django_ratelimit.decorators import ratelimit
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from authentication.two_factor_utils import (
    create_two_factor_session,
    generate_otp_code,
    get_or_create_two_factor,
    is_two_factor_enabled,
    send_otp_email,
    verify_otp_code,
)
from .email_utils import send_welcome_email

from .forms import OTPVerificationForm, RegisterForm, LoginForm, TwoFactorSettingsForm


# Key for storing User ID in session during 2FA flow
TWO_FACTOR_AUTH_SESSION_KEY = "two_factor_auth_user_id"
# Key for storing 2FA verified status in session
TWO_FACTOR_VERIFIED_SESSION_KEY = "two_factor_verified"


def ratelimit_view(request, exception):
    """Custom view to handle rate limited requests"""
    return render(
        request,
        "authentication/ratelimit.html",
        {"retry_after": getattr(request, "retry_after", None)},
        status=429,
    )


@ratelimit(key="ip", rate="10/m", method=["POST"], block=True)
def two_factor_verify_view(request):
    """View for verifying OTP during login."""
    # Get the user ID from session
    user_id = request.session.get(TWO_FACTOR_AUTH_SESSION_KEY)

    # If no user ID in session, redirect to login
    if not user_id:
        return redirect("login")

    # Get the user
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # Invalid user ID, clear session and redirect to login
        request.session.pop(TWO_FACTOR_AUTH_SESSION_KEY, None)
        return redirect("login")

    if request.method == "POST":
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data.get("otp_code")

            # Verify OTP
            if verify_otp_code(user, otp_code):
                # OTP is valid, log the user in
                login(request, user)

                # Create two-factor session record for future verification
                create_two_factor_session(user, request.session.session_key)

                # Mark this session as 2FA verified
                request.session[TWO_FACTOR_VERIFIED_SESSION_KEY] = True

                # Clear the temporary session key
                request.session.pop(TWO_FACTOR_AUTH_SESSION_KEY, None)

                messages.success(request, f"Welcome back, {user.username}!")
                return redirect("monitor_list")
            else:
                messages.error(request, "Invalid or expired verification code.")
        else:
            messages.error(request, "Please enter a valid verification code.")
    else:
        form = OTPVerificationForm()

    return render(
        request,
        "authentication/two_factor_verify.html",
        {
            "form": form,
            "user": user,
        },
    )


@ratelimit(key="ip", rate="5/m", method=["POST"], block=True)
def two_factor_resend_otp_view(request):
    """View for resending OTP."""
    # Get the user ID from session
    user_id = request.session.get(TWO_FACTOR_AUTH_SESSION_KEY)

    # If no user ID in session, redirect to login
    if not user_id:
        return redirect("login")

    # Get the user
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # Invalid user ID, clear session and redirect to login
        request.session.pop(TWO_FACTOR_AUTH_SESSION_KEY, None)
        return redirect("login")

    # Generate and send new OTP
    otp_code = generate_otp_code(user)
    send_otp_email(user, otp_code, request)

    messages.info(request, "A new verification code has been sent to your email.")
    return redirect("two_factor_verify")


@login_required
def two_factor_settings_view(request):
    """View for managing two-factor authentication settings."""
    # Get or create the user's two-factor settings
    two_factor = get_or_create_two_factor(request.user)

    if request.method == "POST":
        form = TwoFactorSettingsForm(request.POST)
        if form.is_valid():
            enable_two_factor = form.cleaned_data.get("enable_two_factor")

            # Update two-factor settings
            two_factor.is_enabled = enable_two_factor
            two_factor.save()

            if enable_two_factor:
                messages.success(
                    request,
                    "Two-factor authentication has been enabled for your account.",
                )
            else:
                messages.success(
                    request,
                    "Two-factor authentication has been disabled for your account.",
                )

            return redirect("two_factor_settings")
    else:
        form = TwoFactorSettingsForm(
            initial={"enable_two_factor": two_factor.is_enabled}
        )

    return render(
        request,
        "authentication/two_factor_settings.html",
        {
            "form": form,
            "two_factor": two_factor,
        },
    )


@ratelimit(key="ip", rate="5/m", method=["POST"], block=True)
@ratelimit(key="post:username", rate="5/m", method=["POST"], block=True)
def login_view(request):
    """Login view with rate limiting by IP and username"""
    if request.user.is_authenticated:
        return redirect("monitor_list")

    # Check if user has already passed first authentication step
    user_id = request.session.get(TWO_FACTOR_AUTH_SESSION_KEY)
    if user_id:
        return redirect("two_factor_verify")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                # Check if user has 2FA enabled
                if is_two_factor_enabled(user):
                    # Store user ID in session for the 2FA verification step
                    request.session[TWO_FACTOR_AUTH_SESSION_KEY] = user.id
                    # Generate and send OTP code
                    otp_code = generate_otp_code(user)
                    send_otp_email(user, otp_code, request)
                    messages.info(
                        request, "A verification code has been sent to your email."
                    )
                    return redirect("two_factor_verify")
                else:
                    # No 2FA, proceed with normal login
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect("monitor_list")
        else:
            messages.error(request, "Invalid username or password")
    else:
        form = LoginForm()

    return render(request, "authentication/login.html", {"form": form})


@ratelimit(key="ip", rate="5/h", method=["POST"], block=True)
def register_view(request):
    """Register view with rate limiting by IP"""
    if request.user.is_authenticated:
        return redirect("monitor_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            send_welcome_email(user)

            messages.success(request, f"Account created for {user.username}")
            return redirect("monitor_list")
    else:
        form = RegisterForm()

    return render(request, "authentication/register.html", {"form": form})


def logout_view(request):
    """Logout view - no rate limiting needed"""
    # Clear 2FA keys from session
    request.session.pop(TWO_FACTOR_AUTH_SESSION_KEY, None)
    request.session.pop(TWO_FACTOR_VERIFIED_SESSION_KEY, None)

    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


class RateLimitedPasswordResetView(PasswordResetView):
    """Password reset view with rate limiting"""

    template_name = "authentication/password_reset.html"
    success_url = reverse_lazy("password_reset_done")
    email_template_name = (
        "authentication/password_reset_email.txt"  # Plain text version
    )
    html_email_template_name = (
        "authentication/password_reset_email.html"  # HTML version
    )

    @ratelimit(key="ip", rate="3/h", method=["POST"], block=True)
    @ratelimit(key="post:email", rate="3/d", method=["POST"], block=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RateLimitedPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirmation view with rate limiting"""

    template_name = "authentication/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

    @ratelimit(key="ip", rate="10/h", method=["POST"], block=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
