import logging

from monitors.models import Monitor, Check
from monitors.services.checks import check_monitor

from authentication.email_utils import (
    send_monitor_alert_email,
    send_monitor_recovery_email,
)

logger = logging.getLogger(__name__)


def perform_check(monitor_id):
    """
    Perform a check for a specific monitor

    Args:
        monitor_id: UUID of the monitor to check
    """
    try:
        # Get the monitor
        monitor = Monitor.objects.get(id=monitor_id)
        logger.info(f"Checking monitor: {monitor.name} ({monitor.id})")

        # Get the last check to compare status for recovery
        last_check = monitor.checks.order_by("-created_at").first()
        was_up = last_check and last_check.is_up

        # Run the check
        result = check_monitor(monitor)

        # Create check record in database
        check = Check.objects.create(
            monitor=monitor,
            is_up=result["is_up"],
            response_time=result["response_time"],
            status_code=result["status_code"],
            error_message=result["error_message"],
        )

        # Service just went down
        if was_up and not result["is_up"]:
            logger.warning(f"Monitor {monitor.name} went DOWN")
            _send_down_notification(monitor, result["error_message"])

        # Service just recovered
        elif not was_up and result["is_up"] and last_check:
            logger.info(f"Monitor {monitor.name} RECOVERED")
            downtime_duration = check.created_at - last_check.created_at
            _send_recovery_notification(monitor, downtime_duration)

        # Log the result
        status = "UP" if result["is_up"] else "DOWN"
        response_time = (
            f"{result['response_time']:.1f}ms" if result["response_time"] else "N/A"
        )

        if result["is_up"]:
            logger.info(f"{monitor.name}: {status} - Response time: {response_time}")
        else:
            logger.error(f"{monitor.name}: {status} - Error: {result['error_message']}")

        return {
            "monitor_id": str(monitor.id),
            "status": status,
            "response_time": response_time,
        }

    except Monitor.DoesNotExist:
        logger.error(f"Monitor with ID {monitor_id} not found")
    except Exception as e:
        logger.exception(f"Error checking monitor {monitor_id}: {str(e)}")


def _send_down_notification(monitor, error_message):
    """Send notification when a monitor goes down"""
    from django.contrib.auth.models import User

    # In a production app, you'd have monitor owners or subscribers
    # For simplicity, we'll notify all admin users
    admin_users = User.objects.filter(is_staff=True)

    for user in admin_users:
        try:
            send_monitor_alert_email(user, monitor, error_message)
        except Exception as e:
            logger.exception(
                f"Error sending down notification to {user.email}: {str(e)}"
            )


def _send_recovery_notification(monitor, downtime_duration):
    """Send notification when a monitor recovers"""
    from django.contrib.auth.models import User

    # Format duration for readability
    hours, remainder = divmod(downtime_duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_duration = ""
    if hours:
        formatted_duration += f"{int(hours)} hours "
    if minutes or hours:
        formatted_duration += f"{int(minutes)} minutes "
    formatted_duration += f"{int(seconds)} seconds"

    # In a production app, you'd have monitor owners or subscribers
    # For simplicity, we'll notify all admin users
    admin_users = User.objects.filter(is_staff=True)

    for user in admin_users:
        try:
            send_monitor_recovery_email(user, monitor, formatted_duration)
        except Exception as e:
            logger.exception(
                f"Error sending recovery notification to {user.email}: {str(e)}"
            )
