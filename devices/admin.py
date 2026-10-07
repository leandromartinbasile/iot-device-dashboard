# devices/admin.py
from django.contrib import admin
from .models import Device, Reading, AlertRule, Alert


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "device_type", "last_seen_at")
    readonly_fields = ("api_key", "created_at", "last_seen_at")


admin.site.register(AlertRule)
admin.site.register(Alert)


@admin.register(Reading)
class ReadingAdmin(admin.ModelAdmin):
    list_display = ("device", "metric", "value", "timestamp")
    list_filter = ("device", "metric")
    ordering = ("-timestamp",)
