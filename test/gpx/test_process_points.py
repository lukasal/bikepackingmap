import unittest
from unittest.mock import Mock
import numpy as np
from haversine import haversine, Unit
from app.gpx.process_points import process_points

class MockPoint:
    def __init__(self, latitude, longitude, elevation=None, time=None):
        self.latitude = latitude
        self.longitude = longitude
        self.elevation = elevation
        self.time = time

class TestProcessPoints(unittest.TestCase):
    def test_process_points_without_speed_func(self):
        points = [
            MockPoint(latitude=0, longitude=0),
            MockPoint(latitude=0, longitude=1),
            MockPoint(latitude=1, longitude=1),
        ]

        result = process_points(points)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], 0)  # Longitude of first point
        self.assertEqual(result[0][1], 0)  # Latitude of first point
        self.assertTrue(np.isnan(result[0][5]))  # Distance for the first point
        self.assertAlmostEqual(result[1][5], haversine((0, 0), (0, 1), unit=Unit.KILOMETERS))  # Distance for second point

    def test_process_points_with_speed_func(self):
        points = [
            MockPoint(latitude=0, longitude=0),
            MockPoint(latitude=0, longitude=1),
        ]

        mock_speed_func = Mock(return_value=10)
        result = process_points(points, get_speed_func=mock_speed_func)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][4], 10)  # Speed for the first point
        self.assertEqual(result[1][4], 10)  # Speed for the second point
        mock_speed_func.assert_called()

    def test_process_points_with_elevation_and_time(self):
        points = [
            MockPoint(latitude=0, longitude=0, elevation=100, time="2023-01-01T00:00:00Z"),
            MockPoint(latitude=0, longitude=1, elevation=200, time="2023-01-01T00:01:00Z"),
        ]

        result = process_points(points)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][2], 100)  # Elevation of first point
        self.assertEqual(result[0][3], "2023-01-01T00:00:00Z")  # Time of first point
        self.assertEqual(result[1][2], 200)  # Elevation of second point
        self.assertEqual(result[1][3], "2023-01-01T00:01:00Z")  # Time of second point

if __name__ == "__main__":
    unittest.main()