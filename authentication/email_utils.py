# authentication/email_utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_templated_email(
    subject, template_html, template_text, context, recipient_list
):
    """
    Send an email using HTML and text templates through the configured email backend.

    Args:
        subject (str): Email subject
        template_html (str): Path to HTML template
        template_text (str): Path to text template
        context (dict): Context variables for the templates
        recipient_list (list): List of recipient email addresses

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    html_content = render_to_string(template_html, context)
    text_content = render_to_string(template_text, context)

    # Fall back to stripping HTML tags if text template is not provided
    if not text_content:
        text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject, text_content, settings.DEFAULT_FROM_EMAIL, recipient_list
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        return msg.send() > 0
    except Exception as e:
        # Log the error but don't raise it
        print(f"Error sending email: {e}")
        return False


def send_welcome_email(user):
    """
    Send a welcome email to newly registered users.

    Args:
        user: User object to send the welcome email to

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = "Welcome to Uptime Monitor!"
    context = {
        "user": user,
        "site_name": "Uptime Monitor",
    }
    return send_templated_email(
        subject,
        "authentication/email/welcome_email.html",
        "authentication/email/welcome_email.txt",
        context,
        [user.email],
    )


def send_monitor_alert_email(user, monitor, error_message):
    """
    Send an alert email when a monitor goes down.

    Args:
        user: User object to send the alert to
        monitor: Monitor object that went down
        error_message: Error message explaining why the monitor is down

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"ALERT: {monitor.name} is DOWN"
    context = {
        "user": user,
        "monitor": monitor,
        "error_message": error_message,
        "site_name": "Uptime Monitor",
    }
    return send_templated_email(
        subject,
        "monitors/email/monitor_alert.html",
        "monitors/email/monitor_alert.txt",
        context,
        [user.email],
    )


def send_monitor_recovery_email(user, monitor, downtime_duration):
    """
    Send a recovery email when a monitor comes back up.

    Args:
        user: User object to send the recovery notice to
        monitor: Monitor object that came back up
        downtime_duration: How long the monitor was down for

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    subject = f"RECOVERED: {monitor.name} is back UP"
    context = {
        "user": user,
        "monitor": monitor,
        "downtime_duration": downtime_duration,
        "site_name": "Uptime Monitor",
    }
    return send_templated_email(
        subject,
        "monitors/email/monitor_recovery.html",
        "monitors/email/monitor_recovery.txt",
        context,
        [user.email],
    )
