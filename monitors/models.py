from django.db import models
from django.utils import timezone
import uuid


class Monitor(models.Model):
    MONITOR_TYPES = (
        ("http", "HTTP"),
        ("ping", "PING"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    url = models.CharField(
        max_length=255, help_text="URL for HTTP or IP address for PING"
    )
    monitor_type = models.CharField(max_length=10, choices=MONITOR_TYPES)
    interval_seconds = models.IntegerField(
        default=300, help_text="Check interval (30s to 24h)"
    )
    timeout_seconds = models.IntegerField(default=30, help_text="Timeout in seconds")
    expected_status_code = models.IntegerField(
        default=200, blank=True, null=True, help_text="For HTTP monitors only"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_monitor_type_display()})"

    def current_status(self):
        last_check = self.checks.order_by("-created_at").first()
        if not last_check:
            return "Unknown"
        return "Up" if last_check.is_up else "Down"

    def uptime_percentage(self, days=7):
        """Calculate uptime percentage for the last 'days' days"""
        start_date = timezone.now() - timezone.timedelta(days=days)
        checks = self.checks.filter(created_at__gte=start_date)
        if not checks:
            return None
        up_count = checks.filter(is_up=True).count()
        return (up_count / checks.count()) * 100

    def average_response_time(self, days=1):
        """Calculate average response time for the last 'days' days"""
        start_date = timezone.now() - timezone.timedelta(days=days)
        checks = self.checks.filter(created_at__gte=start_date, is_up=True)
        if not checks:
            return None
        total_time = sum(check.response_time for check in checks if check.response_time)
        return total_time / checks.count()


class Check(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    monitor = models.ForeignKey(
        Monitor, related_name="checks", on_delete=models.CASCADE
    )
    is_up = models.BooleanField()
    response_time = models.FloatField(
        null=True, blank=True, help_text="Response time in milliseconds"
    )
    status_code = models.IntegerField(
        null=True, blank=True, help_text="HTTP status code (HTTP monitors only)"
    )
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Up" if self.is_up else "Down"
        return f"{self.monitor.name} - {status} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
