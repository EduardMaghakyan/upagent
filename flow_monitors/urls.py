# flow_monitors/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.flow_monitor_list, name="flow_monitor_list"),
    path("flow/new/", views.flow_monitor_create, name="flow_monitor_create"),
    path("flow/step/add/", views.flow_step_add, name="flow_step_add"),
    path("flow/<uuid:pk>/", views.flow_monitor_detail, name="flow_monitor_detail"),
    path("flow/<uuid:pk>/check/", views.flow_monitor_check_now, name="flow_monitor_check_now"),
    path("flow/<uuid:pk>/delete/", views.flow_monitor_delete, name="flow_monitor_delete"),
]
