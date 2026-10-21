"""Flask dashboard for the cold-chain alerting take-home."""

from math import isfinite
from pathlib import Path

from flask import Flask, render_template, request

from alert_engine import (
    DEFAULT_MIN_DURATION_MINUTES,
    DEFAULT_THRESHOLD_C,
    MAX_GAP_MINUTES,
    detect_episodes,
    load_readings,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "sensor_readings.json"
app = Flask(__name__)
READINGS = load_readings(DATA_PATH)


def parse_control(name: str, default: float, low: float, high: float) -> tuple[float, str | None]:
    label = {"threshold_c": "Temperature threshold", "min_duration": "Minimum duration"}[name]
    raw_value = request.args.get(name)
    if raw_value is None:
        return default, None
    try:
        value = float(raw_value)
    except (TypeError, ValueError):
        return default, f"{label} must be a number."
    if not isfinite(value) or not low <= value <= high:
        return default, f"{label} must be between {low:g} and {high:g}."
    return value, None


@app.get("/")
def dashboard():
    threshold, threshold_error = parse_control("threshold_c", DEFAULT_THRESHOLD_C, -50, 50)
    duration, duration_error = parse_control("min_duration", DEFAULT_MIN_DURATION_MINUTES, 0, 1440)
    errors = [error for error in (threshold_error, duration_error) if error]
    episodes = detect_episodes(READINGS, threshold, duration)
    truck_ids = sorted({str(reading["truck_id"]) for reading in READINGS})
    return render_template(
        "index.html",
        episodes=episodes,
        threshold=threshold,
        duration=duration,
        truck_count=len(truck_ids),
        reading_count=len(READINGS),
        errors=errors,
        max_gap=MAX_GAP_MINUTES,
    )


if __name__ == "__main__":
    app.run(debug=False)
