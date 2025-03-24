from django.utils import timezone
from django.contrib.sites.models import Site

from .models import OTPCode, TwoFactorAuth, TwoFactorSession
from .email_utils import send_templated_email


def get_or_create_two_factor(user):
    """Get or create a TwoFactorAuth instance for the user."""
    two_factor, created = TwoFactorAuth.objects.get_or_create(user=user)
    return two_factor


def generate_otp_code(user):
    """Generate a new OTP code for the user."""
    # First, invalidate any existing unused codes
    OTPCode.objects.filter(
        user=user, is_used=False, expires_at__gt=timezone.now()
    ).update(is_used=True)

    # Generate a new code
    otp = OTPCode(user=user)
    otp.save()

    return otp


def send_otp_email(user, otp_code, request=None):
    """Send OTP code to the user's email."""
    domain = Site.objects.get_current().domain
    protocol = "https" if request and request.is_secure() else "http"

    subject = "Your One-Time Password for Login"
    context = {
        "user": user,
        "otp_code": otp_code,
        "domain": domain,
        "protocol": protocol,
        "expiry_minutes": 10,
    }

    return send_templated_email(
        subject,
        "authentication/email/two_factor_otp.html",
        "authentication/email/two_factor_otp.txt",
        context,
        [user.email],
    )


def verify_otp_code(user, code):
    """Verify if the provided OTP code is valid for the user."""
    try:
        otp = OTPCode.objects.get(
            user=user, code=code, is_used=False, expires_at__gt=timezone.now()
        )
        otp.mark_as_used()
        return True
    except OTPCode.DoesNotExist:
        return False


def create_two_factor_session(user, session_key):
    """Create a new two-factor session for the user."""
    session = TwoFactorSession(user=user, session_key=session_key)
    session.save()
    return session


def verify_two_factor_session(user, session_key):
    """Verify if the user has a valid two-factor session."""
    try:
        session = TwoFactorSession.objects.get(
            user=user, session_key=session_key, expires_at__gt=timezone.now()
        )
        return True
    except TwoFactorSession.DoesNotExist:
        return False


def is_two_factor_enabled(user):
    """Check if two-factor authentication is enabled for the user."""
    try:
        return user.two_factor.is_enabled
    except (TwoFactorAuth.DoesNotExist, AttributeError):
        return False
