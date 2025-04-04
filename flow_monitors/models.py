from django.db import models
from django.contrib.auth.models import User
import uuid


class FlowMonitor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    starting_url = models.URLField(help_text="Starting URL for the flow")
    interval_seconds = models.IntegerField(
        default=3600, help_text="Check interval (hourly, daily, etc.)"
    )
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="flow_monitors"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FlowStep(models.Model):
    ACTION_TYPES = (
        ("navigate", "Navigate to URL"),
        ("click", "Click Element"),
        ("fill", "Fill Form Field"),
        ("wait", "Wait for Element"),
        ("verify", "Verify Element Exists"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow = models.ForeignKey(
        FlowMonitor, on_delete=models.CASCADE, related_name="steps"
    )
    sequence = models.IntegerField(help_text="Order of execution")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.CharField(
        max_length=255, help_text="Human readable description"
    )

    # Navigation specific fields
    url = models.URLField(blank=True, null=True, help_text="URL to navigate to")

    # Element interaction fields
    element_description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Text description of element to interact with",
    )
    input_value = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Value to input into form field",
    )

    # Timing fields
    timeout_seconds = models.IntegerField(default=30)
    wait_time_seconds = models.IntegerField(
        default=0, help_text="Time to wait after action"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.sequence}. {self.description}"


class FlowCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flow_monitor = models.ForeignKey(
        FlowMonitor, on_delete=models.CASCADE, related_name="checks"
    )
    is_successful = models.BooleanField()
    total_time = models.FloatField(help_text="Total flow execution time in seconds")
    error_message = models.TextField(blank=True, null=True)
    error_step = models.ForeignKey(
        FlowStep, on_delete=models.SET_NULL, null=True, related_name="failures"
    )
    screenshot = models.ImageField(upload_to="flow_screenshots/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Successful" if self.is_successful else "Failed"
        return f"{self.flow_monitor.name} - {status} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
