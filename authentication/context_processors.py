# authentication/context_processors.py
from django.conf import settings


def email_context(request=None):
    """
    Context processor for email templates to include common variables.

    This can be used both in request context and directly in email templates.
    """
    return {
        "site_name": getattr(settings, "SITE_NAME", "Uptime Monitor"),
        "support_email": getattr(settings, "SUPPORT_EMAIL", "support@yourdomain.com"),
        "company_address": getattr(settings, "COMPANY_ADDRESS", ""),
        "company_name": getattr(settings, "COMPANY_NAME", "Your Company"),
        "unsubscribe_url": getattr(settings, "UNSUBSCRIBE_URL", "#"),
    }
