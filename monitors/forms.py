from django import forms
from .models import Monitor


class MonitorForm(forms.ModelForm):
    # Add choices for time intervals
    INTERVAL_CHOICES = [
        # (30, "30 seconds"),
        (60, "1 minute"),
        (300, "5 minutes"),
        (600, "10 minutes"),
        (900, "15 minutes"),
        (1800, "30 minutes"),
        (3600, "1 hour"),
        (7200, "2 hours"),
        (14400, "4 hours"),
        (21600, "6 hours"),
        (43200, "12 hours"),
        (86400, "24 hours"),
    ]

    # Replace the interval_seconds field with a choice field
    interval_seconds = forms.ChoiceField(
        choices=INTERVAL_CHOICES,
        label="Check Interval",
        help_text="How often to check this monitor",
        widget=forms.Select(
            attrs={
                "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500"
            }
        ),
    )

    class Meta:
        model = Monitor
        fields = [
            "name",
            "url",
            "monitor_type",
            "request_method",
            "interval_seconds",
            "timeout_seconds",
            "expected_status_code",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500"
                }
            ),
            "url": forms.URLInput(
                attrs={
                    "rows": 4,
                    "class": "block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-gray-500 focus:border-gray-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500",
                }
            ),
            "monitor_type": forms.Select(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500"
                }
            ),
            "request_method": forms.Select(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500"
                }
            ),
            "timeout_seconds": forms.NumberInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500",
                    "min": "5",
                    "max": "120",
                }
            ),
            "expected_status_code": forms.NumberInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-gray-500 focus:border-gray-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-gray-500 dark:focus:border-gray-500"
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        monitor_type = cleaned_data.get("monitor_type")
        expected_status_code = cleaned_data.get("expected_status_code")

        # Only HTTP monitors need expected_status_code and request_method
        if monitor_type == "ping":
            if expected_status_code is not None:
                cleaned_data["expected_status_code"] = None
            # Reset request_method to GET for PING monitors (it won't be used)
            cleaned_data["request_method"] = "GET"

        # Convert interval_seconds from string to integer
        interval = cleaned_data.get("interval_seconds")
        if interval:
            cleaned_data["interval_seconds"] = int(interval)

        # Validate timeout_seconds (should be less than 120 seconds)
        timeout = cleaned_data.get("timeout_seconds")
        if timeout:
            if timeout > 120:
                self.add_error(
                    "timeout_seconds", "Timeout must be less than 120 seconds"
                )

        return cleaned_data
