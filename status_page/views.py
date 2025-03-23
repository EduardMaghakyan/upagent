from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from monitors.models import Monitor


def status_page(request):
    monitors = Monitor.objects.all().order_by("name")

    # Calculate overall system status
    overall_status = "Operational"
    down_monitors = []

    for monitor in monitors:
        last_check = monitor.checks.order_by("-created_at").first()
        if last_check and not last_check.is_up:
            overall_status = "Partial Outage"
            down_monitors.append(monitor.name)

    if len(down_monitors) == len(monitors) and len(monitors) > 0:
        overall_status = "Major Outage"

    # Prepare data for each monitor
    monitor_data = []

    for monitor in monitors:
        # Get latest status
        last_check = monitor.checks.order_by("-created_at").first()
        status = "Unknown"
        last_checked = None

        if last_check:
            status = "Operational" if last_check.is_up else "Down"
            last_checked = last_check.created_at

        # Get uptime percentages
        uptime_24h = monitor.uptime_percentage(days=1)
        uptime_7d = monitor.uptime_percentage(days=7)
        uptime_30d = monitor.uptime_percentage(days=30)

        # Get average response time
        avg_response_24h = monitor.average_response_time(days=1)

        # Get last 24 hours of checks for timeline
        one_day_ago = timezone.now() - timedelta(days=1)
        recent_checks = list(
            monitor.checks.filter(created_at__gte=one_day_ago)
            .order_by("created_at")
            .values("created_at", "is_up", "response_time")
        )

        # Group checks by hour for the timeline
        hourly_checks = {}
        for check in recent_checks:
            hour = check["created_at"].replace(minute=0, second=0, microsecond=0)
            if hour not in hourly_checks:
                hourly_checks[hour] = []
            hourly_checks[hour].append(check["is_up"])

        # Calculate hourly status (up if all checks are up, down if any check is down)
        timeline = []
        for hour, checks in sorted(hourly_checks.items()):
            timeline.append(
                {
                    "hour": hour.strftime("%H:%M"),
                    "status": "up" if all(checks) else "down",
                }
            )

        monitor_data.append(
            {
                "name": monitor.name,
                "type": monitor.get_monitor_type_display(),
                "status": status,
                "last_checked": last_checked,
                "uptime_24h": uptime_24h,
                "uptime_7d": uptime_7d,
                "uptime_30d": uptime_30d,
                "avg_response_24h": avg_response_24h,
                "timeline": timeline,
            }
        )

    # Get recent incidents (monitors that have gone down in the last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    incidents = []

    for monitor in monitors:
        # Find checks where status changed from up to down
        checks = list(
            monitor.checks.filter(created_at__gte=seven_days_ago).order_by("created_at")
        )

        for i in range(1, len(checks)):
            if checks[i - 1].is_up and not checks[i].is_up:
                # Found a transition from up to down
                start_time = checks[i].created_at

                # Find when it came back up (if it did)
                resolved_time = None
                for j in range(i + 1, len(checks)):
                    if checks[j].is_up:
                        resolved_time = checks[j].created_at
                        break

                duration = None
                if resolved_time:
                    duration = resolved_time - start_time

                incidents.append(
                    {
                        "monitor": monitor.name,
                        "start_time": start_time,
                        "resolved_time": resolved_time,
                        "duration": duration,
                        "error": checks[i].error_message,
                    }
                )

    # Sort incidents by start time (most recent first)
    incidents.sort(key=lambda x: x["start_time"], reverse=True)

    return render(
        request,
        "status_page/status.html",
        {
            "overall_status": overall_status,
            "monitors": monitor_data,
            "incidents": incidents,
            "last_updated": timezone.now(),
        },
    )
