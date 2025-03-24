from django.db import models
from django.contrib.auth.models import User
import uuid
import random
import string
from django.utils import timezone
from datetime import timedelta


class TwoFactorAuth(models.Model):
    """Model to store Two-Factor Authentication information."""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="two_factor"
    )
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"2FA for {self.user.username} - {'Enabled' if self.is_enabled else 'Disabled'}"


class OTPCode(models.Model):
    """Model to store one-time password codes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_codes")
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.code:
            # Generate a 6-digit numeric code
            self.code = "".join(random.choices(string.digits, k=6))

        if not self.expires_at:
            # Set expiration to 10 minutes from now
            self.expires_at = timezone.now() + timedelta(minutes=10)

        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        self.is_used = True
        self.save()

    def __str__(self):
        status = "Valid" if self.is_valid() else "Invalid"
        return f"OTP {self.code} for {self.user.username} - {status}"


class TwoFactorSession(models.Model):
    """Model to track active 2FA sessions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="two_factor_sessions"
    )
    session_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 30 days from now (adjust as needed)
            self.expires_at = timezone.now() + timedelta(days=30)

        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() < self.expires_at

    def __str__(self):
        status = "Valid" if self.is_valid() else "Expired"
        return f"2FA Session for {self.user.username} - {status}"
