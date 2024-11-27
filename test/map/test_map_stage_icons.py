import unittest
import pandas as pd
from unittest.mock import MagicMock
from folium import Map, FeatureGroup
from app.map.map_stage_icons import map_stage_icons


class TestMapStageIcons(unittest.TestCase):
    def setUp(self):
        # Sample data for activities
        # first activity is not a stage town as there is a second activity on the same day
        self.activities = pd.DataFrame(
            {
                "date": ["2023-01-01", "2023-01-01", "2023-01-02"],
                "end_date": [
                    "2023-01-01 10:00:00",
                    "2023-01-01 12:00:00",
                    "2023-01-02 11:00:00",
                ],
                "map.polyline": [
                    [[51.5, -0.1], [51.5, -0.12], [51.7, -0.13]],
                    [[51.0, -0.1], [51.5, -0.13], [51.2, -0.11]],
                    [[51.0, -0.12], [51.5, -0.14], [51.5, -0.11]],
                ],
                "end_location": ["Location A", "Location B", "Location C"],
                "start_latlng": [(51.5, -0.1), (51.0, -0.1), (51.0, -0.12)],
                "end_latlng": [(51.7, -0.13), (51.2, -0.11), (51.5, -0.11)],
            }
        )
        self.activities["date"] = pd.to_datetime(self.activities["date"])
        self.activities["end_date"] = pd.to_datetime(self.activities["end_date"])

        # Mock settings
        self.settings = MagicMock()
        self.settings.get_interactive_setting.side_effect = lambda key: {
            "stage_start_icon": "star",
            "stage_icon_shape": "circle",
            "stage_border_transparent": False,
            "stage_border_color": "blue",
            "stage_symbol_color": "red",
            "stage_background_transparent": False,
            "stage_background_color": "green",
            "stage_icon_size": 20,
            "stage_icon_inner_size": 10,
        }[key]

    def test_map_stage_icons(self):
        stage_icons = map_stage_icons(self.activities, self.settings)
        self.assertIsInstance(stage_icons, FeatureGroup)
        self.assertEqual(stage_icons.layer_name, "Stage Icons")
        self.assertFalse(stage_icons.control)

        # Check if markers are added correctly
        map_ = Map(location=[51.5, -0.1], zoom_start=10)
        stage_icons.add_to(map_)
        html = map_._repr_html_()
        # Check if the coordinates of the markers are correct
        # end of first activity should not create a marker
        self.assertNotIn("[51.7, -0.13]", html)
        self.assertNotIn("Location A", html)
        # second and third activity should create markers
        self.assertIn("[51.2, -0.11]", html)
        self.assertIn("Location B", html)
        self.assertIn("[51.5, -0.11]", html)
        self.assertIn("Location C", html)


if __name__ == "__main__":
    unittest.main()
