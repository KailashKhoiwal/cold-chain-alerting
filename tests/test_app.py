import unittest

from app import app


class DashboardTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_dashboard_shows_seed_alerts_and_rule_controls(self):
        response = self.client.get("/")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("T-01", page)
        self.assertIn("T-04", page)
        self.assertIn("T-05", page)
        self.assertIn('name="threshold_c"', page)

    def test_empty_state_when_no_episode_meets_rule(self):
        response = self.client.get("/?threshold_c=50&min_duration=20")
        self.assertIn("No sustained issues found", response.get_data(as_text=True))

    def test_invalid_values_show_feedback_and_use_defaults(self):
        response = self.client.get("/?threshold_c=hot&min_duration=99999")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Temperature threshold must be a number", page)
        self.assertIn("Minimum duration must be between 0 and 1440", page)
        self.assertIn('value="8.0"', page)
        self.assertIn('value="20"', page)


if __name__ == "__main__":
    unittest.main()
