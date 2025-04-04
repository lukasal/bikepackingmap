import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
from app.strava.preprocess import preprocess
import matplotlib.pyplot as plt


class TestPreprocess(unittest.TestCase):

    def setUp(self):
        # Create a sample dataframe
        data = {
            "name": ["Location A - Location B", "Location C - Location D"],
            "id": [123, 456],
            "map.summary_polyline": ["encoded_polyline_1", "encoded_polyline_2"],
            "start_date_local": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
            "elapsed_time": [3600, 7200],
            "type": ["Run", "Ride"],
            "distance": [10000, 20000],
            "average_speed": [2.78, 5.56],
            "max_speed": [5.56, 11.12],
        }
        self.activities = pd.DataFrame(data)

    @patch("app.strava.preprocess.get_elevation")
    @patch("app.strava.preprocess.create_binary_elevation_profile")
    @patch("app.strava.preprocess.polyline.decode", lambda x: x)
    def test_preprocess(self, mock_create_binary_elevation_profile, mock_get_elevation):
        # Mock the return values
        mock_get_elevation.return_value = ([0, 1000, 2000], [10, 20, 30])
        mock_plot = plt.plot(mock_get_elevation.return_value)
        mock_create_binary_elevation_profile.return_value = plt.gcf()

        # Apply the preprocess function
        result = preprocess(self.activities)

        # Check the results
        self.assertEqual(len(result), 2)
        self.assertIn("map.polyline", result.columns)
        self.assertIn("start_latlng", result.columns)
        self.assertIn("end_latlng", result.columns)
        self.assertIn("map.elevation", result.columns)
        self.assertIn("map.distance", result.columns)
        self.assertIn("start_location", result.columns)
        self.assertIn("end_location", result.columns)
        self.assertIn("metadata", result.columns)

        # Check if the elevation data was added correctly
        self.assertEqual(result["map.elevation"].iloc[0], [10, 20, 30])
        self.assertEqual(result["map.distance"].iloc[0], [0, 1, 2])
        self.assertIsNotNone(result.metadata.iloc[0]["elevation_profile"])
        self.assertEqual(result.metadata.iloc[0]["average_speed"], 2.78 * 3.6)
        self.assertEqual(result.metadata.iloc[0]["max_speed"], 5.56 * 3.6)

        # Check if the date and time conversions were done correctly
        self.assertEqual(result["date"].iloc[0], pd.to_datetime("2023-01-01").date())
        self.assertEqual(
            result["start_date"].iloc[0], pd.to_datetime("2023-01-01T00:00:00")
        )
        self.assertEqual(
            result["end_date"].iloc[0], pd.to_datetime("2023-01-01T01:00:00")
        )

    @patch("app.strava.preprocess.get_elevation", side_effect=Exception("Mocked error"))
    @patch("app.strava.preprocess.create_binary_elevation_profile")
    @patch("app.strava.preprocess.polyline.decode", lambda x: x)
    def test_preprocess_error(
        self, mock_create_binary_elevation_profile, mock_get_elevation
    ):

        # Apply the preprocess function
        result = preprocess(self.activities)

        # Check the results
        self.assertEqual(len(result), 2)
        self.assertIn("map.polyline", result.columns)
        self.assertIn("start_latlng", result.columns)
        self.assertIn("end_latlng", result.columns)
        self.assertIn("map.elevation", result.columns)
        self.assertIn("map.distance", result.columns)
        self.assertIn("start_location", result.columns)
        self.assertIn("end_location", result.columns)
        self.assertIn("metadata", result.columns)

        # Check if the elevation data was added correctly
        self.assertEqual(result["map.elevation"].iloc[0], [])
        self.assertEqual(result["map.distance"].iloc[0], [])
        self.assertEqual(result.metadata.iloc[0]["elevation_profile"], "")
        self.assertEqual(result.metadata.iloc[0]["average_speed"], 2.78 * 3.6)
        self.assertEqual(result.metadata.iloc[0]["max_speed"], 5.56 * 3.6)

        # Check if the date and time conversions were done correctly
        self.assertEqual(result["date"].iloc[0], pd.to_datetime("2023-01-01").date())
        self.assertEqual(
            result["start_date"].iloc[0], pd.to_datetime("2023-01-01T00:00:00")
        )
        self.assertEqual(
            result["end_date"].iloc[0], pd.to_datetime("2023-01-01T01:00:00")
        )


if __name__ == "__main__":
    unittest.main()
