# devices/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Device, Reading
from .tasks import check_reading_against_rules


@csrf_exempt
@require_POST
def ingest_reading(request):
    # 1. Authenticate the device via its api_key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return JsonResponse({"error": "Missing X-API-Key header"}, status=401)

    try:
        device = Device.objects.get(api_key=api_key)
    except Device.DoesNotExist:
        return JsonResponse({"error": "Invalid API key"}, status=401)

    # 2. Parse the JSON body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    metric = data.get("metric")
    value = data.get("value")

    if metric is None or value is None:
        return JsonResponse({"error": "'metric' and 'value' are required"}, status=400)

    try:
        value = float(value)
    except (TypeError, ValueError):
        return JsonResponse({"error": "'value' must be a number"}, status=400)

    # 3. Save the reading
    reading = Reading.objects.create(device=device, metric=metric, value=value)
    check_reading_against_rules.delay(reading.id)

    # 4. Update device last_seen_at
    device.last_seen_at = timezone.now()
    device.save(update_fields=["last_seen_at"])

    return JsonResponse({"status": "ok"}, status=201)


def device_readings(request, device_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    # Only return data for devices the logged-in user actually owns
    device = get_object_or_404(Device, id=device_id, owner=request.user)

    metric = request.GET.get("metric")
    limit = int(request.GET.get("limit", 100))

    readings = device.readings.all()
    if metric:
        readings = readings.filter(metric=metric)
    readings = readings[:limit]

    data = [
        {
            "metric": r.metric,
            "value": r.value,
            "timestamp": r.timestamp.isoformat(),
        }
        for r in readings
    ]

    return JsonResponse({"device": device.name, "readings": data})
