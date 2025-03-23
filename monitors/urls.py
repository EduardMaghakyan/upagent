from django.urls import path
from . import views

urlpatterns = [
    path("", views.monitor_list, name="monitor_list"),
    path("monitor/new/", views.monitor_create, name="monitor_create"),
    path("monitor/<uuid:pk>/edit/", views.monitor_edit, name="monitor_edit"),
    path("monitor/<uuid:pk>/delete/", views.monitor_delete, name="monitor_delete"),
    path("monitor/<uuid:pk>/check/", views.monitor_check_now, name="monitor_check_now"),
    path("monitor/<uuid:pk>/", views.monitor_detail, name="monitor_detail"),
]
