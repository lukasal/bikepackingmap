import unittest
from unittest.mock import patch, MagicMock
import sys
from os.path import abspath, dirname, realpath
import pickle

PATH = realpath(abspath(__file__))
sys.path.insert(0, dirname(dirname(PATH)))
from app.endpoints import create_app


class FetchStravaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    @patch("app.endpoints.get_data")
    @patch("app.endpoints.ActivityManager")
    def test_fetch_strava(self, mock_activity_manager, mock_get_data):

        # Mock request args
        with self.client as c:
            with c.session_transaction() as sess:
                sess["access_token"] = "test_access_token"

            with open("test/data/get_data.pkl", "rb") as f:
                get_data = pickle.load(f)

            mock_get_data.return_value = get_data
            mock_activity_manager_instance = MagicMock()
            mock_activity_manager.load_from_redis.return_value = (
                mock_activity_manager_instance
            )

            response = c.get(
                "/fetch_strava",
                query_string={
                    "start_date": "2024-06-05",
                    "end_date": "2024-06-08",
                    "per_page": 10,
                },
            )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.json,
                {
                    "data": [
                        {k: d[k] for k in ["start_date", "name", "id"]}
                        for d in get_data
                    ]
                },
            )


if __name__ == "__main__":
    unittest.main()
