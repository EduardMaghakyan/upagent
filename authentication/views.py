from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages

from django_ratelimit.decorators import ratelimit
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from .email_utils import send_welcome_email

from .forms import RegisterForm, LoginForm


def ratelimit_view(request, exception):
    """Custom view to handle rate limited requests"""
    return render(
        request,
        "authentication/ratelimit.html",
        {"retry_after": getattr(request, "retry_after", None)},
        status=429,
    )


@ratelimit(key="ip", rate="5/m", method=["POST"], block=True)
@ratelimit(key="post:username", rate="5/m", method=["POST"], block=True)
def login_view(request):
    """Login view with rate limiting by IP and username"""
    if request.user.is_authenticated:
        return redirect("monitor_list")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
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
