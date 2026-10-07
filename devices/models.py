# devices/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets


class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=50, blank=True)  # e.g. "ESP32", "Arduino Uno"
    api_key = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.owner.username})"


class Reading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="readings")
    metric = models.CharField(max_length=50)   # e.g. "temperature", "humidity"
    value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["device", "metric", "-timestamp"]),
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.device.name} · {self.metric}={self.value} @ {self.timestamp}"


class AlertRule(models.Model):
    CONDITION_CHOICES = [
        ("gt", "Greater than"),
        ("lt", "Less than"),
    ]

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="alert_rules")
    metric = models.CharField(max_length=50)
    condition = models.CharField(max_length=2, choices=CONDITION_CHOICES)
    threshold = models.FloatField()
    enabled = models.BooleanField(default=True)

    def is_breached(self, value: float) -> bool:
        if self.condition == "gt":
            return value > self.threshold
        return value < self.threshold

    def __str__(self):
        return f"{self.device.name}: {self.metric} {self.condition} {self.threshold}"


class Alert(models.Model):
    rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name="alerts")
    value_at_trigger = models.FloatField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_active(self):
        return self.resolved_at is None

    def __str__(self):
        return f"Alert: {self.rule} — triggered {self.triggered_at}"
