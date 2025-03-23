from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
import json
from datetime import timedelta

from .models import Monitor, Check
from .forms import MonitorForm
from .services.checks import check_monitor
from django.contrib.auth.decorators import login_required


@login_required
def monitor_list(request):
    monitors = Monitor.objects.all().order_by("name")

    # Get basic status for each monitor
    monitor_data = []
    for monitor in monitors:
        last_check = monitor.checks.order_by("-created_at").first()
        status = "Unknown"
        response_time = None
        last_checked = None

        if last_check:
            status = "Up" if last_check.is_up else "Down"
            response_time = last_check.response_time
            last_checked = last_check.created_at

        monitor_data.append(
            {
                "id": monitor.id,
                "name": monitor.name,
                "type": monitor.get_monitor_type_display(),
                "url": monitor.url,
                "status": status,
                "response_time": response_time,
                "last_checked": last_checked,
                "uptime": monitor.uptime_percentage(),
            }
        )

    return render(
        request,
        "monitors/monitor_list.html",
        {
            "monitors": monitor_data,
        },
    )


@login_required
def monitor_create(request):
    if request.method == "POST":
        form = MonitorForm(request.POST)
        if form.is_valid():
            monitor = form.save()
            messages.success(request, f'Monitor "{monitor.name}" created successfully')
            return redirect("monitor_list")
    else:
        form = MonitorForm()

    return render(
        request, "monitors/monitor_form.html", {"form": form, "title": "Create Monitor"}
    )


@login_required
def monitor_edit(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk)

    if request.method == "POST":
        form = MonitorForm(request.POST, instance=monitor)
        if form.is_valid():
            monitor = form.save()
            messages.success(request, f'Monitor "{monitor.name}" updated successfully')
            return redirect("monitor_list")
    else:
        form = MonitorForm(instance=monitor)

    return render(
        request,
        "monitors/monitor_form.html",
        {"form": form, "title": f"Edit Monitor: {monitor.name}", "monitor": monitor},
    )


@login_required
def monitor_delete(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk)

    if request.method == "POST":
        name = monitor.name
        monitor.delete()
        messages.success(request, f'Monitor "{name}" deleted successfully')
        return redirect("monitor_list")

    return render(request, "monitors/monitor_confirm_delete.html", {"monitor": monitor})


@login_required
def monitor_check_now(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk)

    try:
        # Run the check manually
        result = check_monitor(monitor)

        # Create check record in database
        Check.objects.create(
            monitor=monitor,
            is_up=result["is_up"],
            response_time=result["response_time"],
            status_code=result["status_code"],
            error_message=result["error_message"],
        )

        status = "Up" if result["is_up"] else "Down"
        message = f"Check complete: {monitor.name} is {status}"
        if result["response_time"]:
            message += f' ({result["response_time"]:.1f} ms)'
        if not result["is_up"] and result["error_message"]:
            message += f' - Error: {result["error_message"]}'

        messages.info(request, message)
    except Exception as e:
        messages.error(request, f"Error checking monitor: {str(e)}")

    return redirect("monitor_list")


@login_required
def monitor_detail(request, pk):
    monitor = get_object_or_404(Monitor, pk=pk)

    # Get the last 100 checks
    checks = monitor.checks.order_by("-created_at")[:100]

    # Get uptime percentages for different time periods
    uptime_24h = monitor.uptime_percentage(days=1)
    uptime_7d = monitor.uptime_percentage(days=7)
    uptime_30d = monitor.uptime_percentage(days=30)

    # Get average response times
    avg_response_24h = monitor.average_response_time(days=1)
    avg_response_7d = monitor.average_response_time(days=7)

    # Prepare data for the response time chart (last 24 hours)
    one_day_ago = timezone.now() - timedelta(days=1)
    response_time_data = list(
        monitor.checks.filter(
            created_at__gte=one_day_ago, is_up=True, response_time__isnull=False
        )
        .order_by("created_at")
        .values("created_at", "response_time")
    )

    chart_data = [
        {
            "timestamp": check["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
            "response_time": check["response_time"],
        }
        for check in response_time_data
    ]

    return render(
        request,
        "monitors/monitor_detail.html",
        {
            "monitor": monitor,
            "checks": checks,
            "uptime_24h": uptime_24h,
            "uptime_7d": uptime_7d,
            "uptime_30d": uptime_30d,
            "avg_response_24h": avg_response_24h,
            "avg_response_7d": avg_response_7d,
            "chart_data": json.dumps(chart_data),
        },
    )
