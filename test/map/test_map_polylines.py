import unittest
import folium
import pandas as pd
from datetime import datetime
from app.map.map_polylines import map_polylines
from app.map.MapSettings import MapSettings


class TestMapPolylines(unittest.TestCase):
    class MapSettings:
        line_thickness = 5
        color = {"Run": "blue"}
        spec_width = 300
        spec_height = 200
        spec_resolution = 1

    def setUp(self):
        # Sample data for activities
        data = {
            "name": ["Activity 1"],
            "start_date": [datetime(2023, 10, 1, 12, 0, 0)],
            "date": ["2023-10-01"],
            "type": ["Run"],
            "map_polyline": [[[51.5, -0.1], [51.5, -0.12], [51.5, -0.14]]],
            "metadata": [
                {
                    "distance": 10.0,
                    "total_elevation_gain": 100,
                    "moving_time": 3600,
                    "elapsed_time": 4000,
                    "average_speed": 10.0,
                    "max_speed": 15.0,
                    "average_heartrate": 150,
                    "max_heartrate": 180,
                    "average_temp": 20.0,
                    "elevation_profile": "sample_base64_encoded_image",
                }
            ],
        }
        self.activities = pd.DataFrame(data)

        # Sample map settings
        self.map_settings = MapSettings(
            self.activities, "config/interactive_settings.yml"
        )

    def test_map_polylines(self):
        polylines = map_polylines(self.activities, self.map_settings)
        self.assertIsInstance(polylines, folium.FeatureGroup)
        self.assertEqual(len(polylines._children), 2)  # Two polylines per activity

        # Check if the first polyline has the correct color and weight
        polyline1 = list(polylines._children.values())[0]
        self.assertEqual(polyline1.options["color"], "#ffffff")
        self.assertEqual(
            polyline1.options["weight"],
            self.map_settings.get_interactive_setting("line_thickness") + 3,
        )

        # Check if the second polyline has the correct color and weight
        polyline2 = list(polylines._children.values())[1]
        self.assertEqual(
            polyline2.options["color"],
            self.map_settings.get_interactive_setting("line_color_Run"),
        )
        self.assertEqual(
            polyline2.options["weight"],
            self.map_settings.get_interactive_setting("line_thickness"),
        )

        # Check if the popup is correctly added
        self.assertEqual(len(polyline2._children), 1)
        self.assertTrue(next(iter(polyline2._children.values()))._name, "Popup")


if __name__ == "__main__":
    unittest.main()
