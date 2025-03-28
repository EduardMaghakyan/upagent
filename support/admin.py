from django.contrib import admin
from .models import SupportRequest


@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "priority", "status", "created_at")
    list_filter = ("priority", "status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Contact Information", {"fields": ("name", "email")}),
        ("Request Details", {"fields": ("subject", "message", "priority")}),
        ("Status", {"fields": ("status",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
