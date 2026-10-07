# simulate_device.py
import requests
import random
import time

API_URL = "http://127.0.0.1:8000/api/ingest/"
API_KEY = "c03d13d900aac5f8f0b1ba823805bfa73cb5124e5fbfc361d6c21a4bd07e5904"

METRICS = {
    "temperature": (18.0, 32.0),
    "humidity": (30.0, 80.0),
}

INTERVAL_SECONDS = 5


def send_reading(metric, value):
    try:
        response = requests.post(
            API_URL,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY,
            },
            json={"metric": metric, "value": value},
            timeout=5,
        )
        print(f"{metric}={value:.1f} -> {response.status_code} {response.json()}")
    except requests.exceptions.ConnectionError:
        print(f"{metric}={value:.1f} -> FAILED (server unreachable, will retry next cycle)")
    except requests.exceptions.Timeout:
        print(f"{metric}={value:.1f} -> FAILED (request timed out)")


def main():
    print(f"Simulating device, sending every {INTERVAL_SECONDS}s. Ctrl+C to stop.")
    while True:
        for metric, (low, high) in METRICS.items():
            value = round(random.uniform(low, high), 1)
            send_reading(metric, value)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
