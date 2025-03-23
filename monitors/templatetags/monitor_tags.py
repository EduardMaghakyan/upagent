from django import template

register = template.Library()


@register.filter
def format_interval(seconds):
    """
    Convert seconds to a human-readable interval string
    """
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"


@register.filter
def format_uptime(uptime):
    """
    Format uptime percentage with proper coloring
    """
    if uptime is None:
        return None

    # Return the formatted uptime percentage
    return f"{uptime:.2f}%"
