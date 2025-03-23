from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("monitors.urls")),
    path("status/", include("status_page.urls")),
    path(
        "accounts/", include("authentication.urls")
    ),
]
