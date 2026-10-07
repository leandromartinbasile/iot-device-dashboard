# devices/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("ingest/", views.ingest_reading, name="ingest_reading"),
    path("devices/<int:device_id>/readings/", views.device_readings, name="device_readings"),
]
