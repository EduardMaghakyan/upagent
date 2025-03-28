from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("monitors.urls")),
    path("status/", include("status_page.urls")),
    path("accounts/", include("authentication.urls")),
    path("django-rq/", include("django_rq.urls")),
    path("support/", include("support.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
