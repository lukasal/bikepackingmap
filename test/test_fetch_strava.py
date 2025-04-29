import unittest
from unittest.mock import patch, MagicMock
import sys
from os.path import abspath, dirname, realpath
import pickle
import pandas as pd
from app.activity_manager.activity_manager import ActivityManager

PATH = realpath(abspath(__file__))
sys.path.insert(0, dirname(dirname(PATH)))
from app import create_app


class FetchStravaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["PROPAGATE_EXCEPTIONS"] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    @patch("app.routes.strava.get_data")
    @patch(
        "app.activity_manager.activity_manager.store_in_cache",
        side_effect=lambda: lambda x: x,
    )
    def test_fetch_strava(self, mock_activity_manager, mock_get_data):

        # Mock request args
        with self.client as c:
            with c.session_transaction() as sess:
                sess["access_token"] = "test_access_token"

            with open("test/data/get_data.pkl", "rb") as f:
                get_data = pickle.load(f)

            mock_get_data.return_value = get_data
            mock_activity_manager_instance = ActivityManager("123")
            mock_activity_manager.load_from_cache.return_value = (
                mock_activity_manager_instance
            )

            response = c.post(
                "/fetch_strava",
                data={
                    "start_date": "2024-06-05",
                    "end_date": "2024-06-08",
                    "per_page": 10,
                },
            )

            self.assertEqual(response.status_code, 200)
            response_data = response.json["data"]
            self.assertEqual(len(response_data), 3)
            for item in response_data:
                self.assertIn("start_date", item)
                self.assertIn("name", item)
                self.assertIn("id", item)
                self.assertIn("type", item)
                self.assertIsInstance(item["start_date"], str)
                self.assertIsInstance(item["name"], str)
                self.assertIsInstance(item["id"], str)
                self.assertIsInstance(item["type"], str)


if __name__ == "__main__":
    unittest.main()
