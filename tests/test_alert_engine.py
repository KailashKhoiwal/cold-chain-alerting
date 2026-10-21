import unittest
from datetime import datetime

from alert_engine import detect_episodes


def reading(truck, minute, temperature):
    return {
        "truck_id": truck,
        "timestamp": f"2026-07-20T08:{minute:02d}:00",
        "temperature_c": temperature,
        "humidity_pct": 50,
    }


class DetectEpisodesTests(unittest.TestCase):
    def test_seed_dataset_is_sorted_and_groups_expected_trucks(self):
        from pathlib import Path
        from alert_engine import load_readings

        data = load_readings(Path(__file__).parents[1] / "data" / "sensor_readings.json")
        alerts = detect_episodes(data)
        self.assertEqual({item["truck_id"] for item in alerts}, {"T-01", "T-04", "T-05"})
        by_truck = {item["truck_id"]: item for item in alerts}
        self.assertEqual(by_truck["T-05"]["duration_minutes"], 30)
        self.assertEqual(by_truck["T-04"]["duration_minutes"], 20)

    def test_spike_and_exact_threshold_do_not_alert(self):
        data = [reading("T-1", 0, 8.1), reading("T-1", 5, 9), reading("T-1", 10, 8), reading("T-1", 15, 8)]
        self.assertEqual(detect_episodes(data), [])

    def test_exact_minimum_duration_qualifies(self):
        data = [reading("T-1", 0, 8.1), reading("T-1", 5, 8.2), reading("T-1", 10, 8.5), reading("T-1", 20, 8.3)]
        self.assertEqual(detect_episodes(data)[0]["duration_minutes"], 20)

    def test_gap_over_ten_minutes_splits_episode(self):
        data = [reading("T-1", 0, 9), reading("T-1", 5, 9), reading("T-1", 20, 9), reading("T-1", 25, 9)]
        self.assertEqual(detect_episodes(data), [])

    def test_independent_trucks_and_out_of_order_inputs(self):
        data = [
            reading("B", 20, 9), reading("A", 0, 9), reading("B", 10, 9),
            reading("A", 15, 9), reading("B", 0, 9), reading("A", 10, 9),
            reading("B", 15, 9), reading("A", 5, 9), reading("B", 5, 9),
            reading("A", 20, 9),
        ]
        alerts = detect_episodes(data)
        self.assertEqual([item["truck_id"] for item in alerts], ["A", "B"])
        self.assertTrue(all(item["start"] == datetime(2026, 7, 20, 8, 0) for item in alerts))


if __name__ == "__main__":
    unittest.main()
