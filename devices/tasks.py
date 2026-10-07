# devices/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Reading, AlertRule, Alert
from django.utils import timezone


@shared_task
def check_reading_against_rules(reading_id):
    try:
        reading = Reading.objects.get(id=reading_id)
    except Reading.DoesNotExist:
        return

    rules = AlertRule.objects.filter(
        device=reading.device,
        metric=reading.metric,
        enabled=True,
    )

    for rule in rules:
        active_alert = Alert.objects.filter(rule=rule, resolved_at__isnull=True).first()

        if rule.is_breached(reading.value):
            if active_alert:
                continue  # already alerted, still breaching — stay quiet
            Alert.objects.create(rule=rule, value_at_trigger=reading.value)
            send_mail(
                subject=f"Alert: {reading.device.name} — {rule.metric} {rule.condition} {rule.threshold}",
                message=(
                    f"Device: {reading.device.name}\n"
                    f"Metric: {rule.metric}\n"
                    f"Value: {reading.value}\n"
                    f"Rule: {rule.condition} {rule.threshold}\n"
                    f"Time: {reading.timestamp}"
                ),
                from_email=None,
                recipient_list=[reading.device.owner.email],
                fail_silently=True,
            )
        else:
            if active_alert:
                active_alert.resolved_at = timezone.now()
                active_alert.save(update_fields=["resolved_at"])
