import unittest
import pandas as pd
from app.strava.process_strava import process_strava
from unittest.mock import patch
from app.models.activity_model import Activity


class TestProcessStrava(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame(
            {
                "name": [
                    "Stage1: Location A - Location B",
                    "Stage2 : Location C - Location D",
                ],
                "id": [123, 456],
                "map.summary_polyline": [
                    [(52.5200, 13.4050), (52.5201, 13.4051)],
                    [(52.5200, 14.4050), (52.5201, 14.4051)],
                ],
                "start_date_local": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
                "elapsed_time": [3600, 7200],
                "type": ["Run", "Ride"],
                "distance": [10000, 20000],
                "average_speed": [2.78, 5.56],
                "max_speed": [5.56, 11.12],
            }
        )

    @patch("app.strava.process_strava.polyline.decode")
    def test_process_strava_basic(self, mock_decode):
        mock_decode.side_effect = lambda x: x
        result = process_strava(self.data)

        # Check if the result is as expected
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(activity, Activity) for activity in result))

        # Check if polyline decoding was applied
        self.assertEqual(
            result[0].map_polyline, [(52.5200, 13.4050), (52.5201, 13.4051)]
        )

        # Check if start and end lat/lng were extracted correctly
        self.assertEqual(result[0].start_latlng, [52.5200, 13.4050])
        self.assertEqual(result[0].end_latlng, [52.5201, 13.4051])

        # Check if start and end locations were extracted correctly
        self.assertEqual(result[0].start_location, "Location A")
        self.assertEqual(result[0].end_location, "Location B")

        # Check if date and time conversions were applied correctly
        self.assertEqual(result[0].date.strftime("%Y-%m-%d"), "2023-01-01")
        self.assertEqual(
            result[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-01 00:00:00"
        )
        self.assertEqual(
            result[0].end_date.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-01 01:00:00"
        )

        # Check if metadata was created correctly
        self.assertIn("average_speed", result[0].metadata)
        self.assertIn("max_speed", result[0].metadata)

        # Check if speed conversions were applied correctly
        self.assertEqual(result[0].metadata["average_speed"], 2.78 * 3.6)
        self.assertEqual(result[0].metadata["max_speed"], 5.56 * 3.6)
        # Check if polyline decoding was applied
        self.assertEqual(
            result[1].map_polyline, [(52.5200, 14.4050), (52.5201, 14.4051)]
        )

        # Check if start and end lat/lng were extracted correctly
        self.assertEqual(result[1].start_latlng, [52.5200, 14.4050])
        self.assertEqual(result[1].end_latlng, [52.5201, 14.4051])

        # Check if start and end locations were extracted correctly
        self.assertEqual(result[1].start_location, "Location C")
        self.assertEqual(result[1].end_location, "Location D")

        # Check if date and time conversions were applied correctly
        self.assertEqual(result[1].date.strftime("%Y-%m-%d"), "2023-01-02")
        self.assertEqual(
            result[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-02 00:00:00"
        )
        self.assertEqual(
            result[1].end_date.strftime("%Y-%m-%d %H:%M:%S"), "2023-01-02 02:00:00"
        )

    @unittest.skip("test not ready")
    def test_process_strava_empty_dataframe(self):
        empty_activities = pd.DataFrame()
        result = process_strava(empty_activities)

        # Check if the result is an empty list
        self.assertEqual(result, [])

    def test_process_strava_missing_columns(self):
        incomplete_activities = pd.DataFrame(
            {
                "name": ["Run: Start - End"],
                "start_date_local": ["2023-01-01T10:00:00Z"],
            }
        )

        with self.assertRaises(KeyError):
            process_strava(incomplete_activities)

    @unittest.skip("test not ready")
    def test_process_strava_invalid_polyline(self):
        invalid_polyline_activities = pd.DataFrame(
            {
                "name": [
                    "Stage1: Location A - Location B",
                    "Stage2 : Location C - Location D",
                ],
                "id": [123, 456],
                "map.summary_polyline": [
                    "invalid polyline",
                    [(52.5200, 14.4050), (52.5201, 14.4051)],
                ],
                "start_date_local": ["2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z"],
                "elapsed_time": [3600, 7200],
                "type": ["Run", "Ride"],
                "distance": [10000, 20000],
                "average_speed": [2.78, 5.56],
                "max_speed": [5.56, 11.12],
            }
        )

        with self.assertRaises(ValueError):
            process_strava(invalid_polyline_activities)


if __name__ == "__main__":
    unittest.main()
