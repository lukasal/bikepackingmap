import unittest
import folium
import pandas as pd
from datetime import datetime
from app.map.map_polylines import map_polylines


class TestMapPolylines(unittest.TestCase):

    def setUp(self):
        # Sample data for activities
        data = {
            "name": ["Activity 1"],
            "type": ["Run"],
            "map.polyline": [[[51.5, -0.1], [51.5, -0.12], [51.5, -0.14]]],
            "distance": [10.0],
            "total_elevation_gain": [100],
            "moving_time": [3600],
            "elapsed_time": [4000],
            "average_speed": [10.0],
            "max_speed": [15.0],
            "average_heartrate": [150],
            "max_heartrate": [180],
            "average_temp": [20.0],
            "elevation_profile": ["sample_base64_encoded_image"],
        }
        index = [datetime(2023, 10, 1, 12, 0, 0)]
        self.activities = pd.DataFrame(data, index=index)

        # Sample map settings
        class MapSettings:
            line_thickness = 5
            color = {"Run": "blue"}
            spec_width = 300
            spec_height = 200
            spec_resolution = 1

        self.map_settings = MapSettings()

    def test_map_polylines(self):
        polylines = map_polylines(self.activities, self.map_settings)
        self.assertIsInstance(polylines, folium.FeatureGroup)
        self.assertEqual(len(polylines._children), 2)  # Two polylines per activity

        # Check if the first polyline has the correct color and weight
        polyline1 = list(polylines._children.values())[0]
        self.assertEqual(polyline1.options["color"], "white")
        self.assertEqual(
            polyline1.options["weight"], self.map_settings.line_thickness + 3
        )

        # Check if the second polyline has the correct color and weight
        polyline2 = list(polylines._children.values())[1]
        self.assertEqual(polyline2.options["color"], self.map_settings.color["Run"])
        self.assertEqual(polyline2.options["weight"], self.map_settings.line_thickness)

        # Check if the popup is correctly added
        self.assertEqual(len(polyline2._children), 1)
        self.assertTrue(next(iter(polyline2._children.values()))._name, "Popup")


if __name__ == "__main__":
    unittest.main()
