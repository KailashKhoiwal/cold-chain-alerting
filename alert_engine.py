"""Temperature episode detection for the Cold-Chain Alerting demo."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any


DEFAULT_THRESHOLD_C = 8.0
DEFAULT_MIN_DURATION_MINUTES = 20.0
MAX_GAP_MINUTES = 10.0


def load_readings(path: str | Path) -> list[dict[str, Any]]:
    """Load and validate the top-level shape of the bundled readings file."""
    with Path(path).open(encoding="utf-8") as source:
        payload = json.load(source)
    readings = payload.get("readings") if isinstance(payload, dict) else None
    if not isinstance(readings, list):
        raise ValueError("Dataset must contain a 'readings' list.")
    return readings


def parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp; naive timestamps remain naive."""
    return datetime.fromisoformat(value)


def detect_episodes(
    readings: list[dict[str, Any]],
    threshold_c: float = DEFAULT_THRESHOLD_C,
    min_duration_minutes: float = DEFAULT_MIN_DURATION_MINUTES,
    max_gap_minutes: float = MAX_GAP_MINUTES,
) -> list[dict[str, Any]]:
    """Return qualifying over-temperature episodes, independently per truck.

    Readings at or below the threshold end an episode. Episodes are split when
    consecutive violating readings are separated by more than max_gap_minutes.
    Duration is elapsed timestamp time, not a count of readings.
    """
    by_truck: dict[str, list[tuple[datetime, dict[str, Any]]]] = {}
    for index, reading in enumerate(readings):
        try:
            truck_id = str(reading["truck_id"])
            timestamp = parse_timestamp(reading["timestamp"])
            temperature = float(reading["temperature_c"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid reading at index {index}: {exc}") from exc
        by_truck.setdefault(truck_id, []).append((timestamp, {**reading, "temperature_c": temperature}))

    alertable: list[dict[str, Any]] = []

    def finish(truck_id: str, episode: list[tuple[datetime, dict[str, Any]]]) -> None:
        if not episode:
            return
        start, end = episode[0][0], episode[-1][0]
        duration = (end - start).total_seconds() / 60
        if duration >= min_duration_minutes:
            alertable.append({
                "truck_id": truck_id,
                "start": start,
                "end": end,
                "duration_minutes": duration,
                "peak_temperature_c": max(item[1]["temperature_c"] for item in episode),
                "reading_count": len(episode),
            })

    for truck_id, truck_readings in by_truck.items():
        truck_readings.sort(key=lambda item: item[0])
        current: list[tuple[datetime, dict[str, Any]]] = []
        previous_time: datetime | None = None
        for timestamp, reading in truck_readings:
            is_violation = reading["temperature_c"] > threshold_c
            gap_minutes = (
                (timestamp - previous_time).total_seconds() / 60
                if previous_time is not None else 0
            )
            if current and gap_minutes > max_gap_minutes:
                finish(truck_id, current)
                current = []
            if is_violation:
                current.append((timestamp, reading))
            elif current:
                finish(truck_id, current)
                current = []
            previous_time = timestamp
        finish(truck_id, current)

    alertable.sort(key=lambda episode: (episode["start"], episode["truck_id"]))
    return alertable
