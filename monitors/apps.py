from django.apps import AppConfig


class MonitorsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monitors"

    def ready(self):
        import monitors.signals  # noqa: F401
