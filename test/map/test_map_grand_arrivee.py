import unittest
import folium
import pandas as pd
from app.map.map_grand_arrivee import map_grand_arrivee
from unittest.mock import MagicMock


class TestMapGrandArrivee(unittest.TestCase):

    def setUp(self):
        # Sample data for activities
        self.activities1 = pd.DataFrame(
            {
                "end_date": ["2023-10-03", "2023-10-02"],
                "map_polyline": [
                    [(45.0, 7.0), (46.0, 8.0)],
                    [(47.0, 9.0), (48.0, 10.0)],
                ],
                "end_location": ["Location A", "Location B"],
                "start_latlng": [[45.0, 7.0], [47.0, 9.0]],
                "end_latlng": [[46.0, 8.0], [48.0, 10.0]],
            }
        )
        self.activities2 = pd.DataFrame(
            {
                "end_date": [None, None],
                "map_polyline": [
                    [(45.0, 7.0), (46.0, 8.0)],
                    [(47.0, 9.0), (48.0, 10.0)],
                ],
                "end_location": ["Location A", "Location B"],
                "start_latlng": [[45.0, 7.0], [47.0, 9.0]],
                "end_latlng": [[46.0, 8.0], [48.0, 10.0]],
            }
        )
        # Convert end_date to datetime
        self.activities1["end_date"] = pd.to_datetime(self.activities1["end_date"])
        # Mock settings
        self.settings = MagicMock()
        self.settings.get_interactive_setting.side_effect = lambda x: {
            "arrivee_icon": "flag",
            "arrivee_icon_shape": "circle",
            "arrivee_border_transparent": False,
            "arrivee_border_color": "blue",
            "arrivee_symbol_color": "white",
            "arrivee_background_transparent": False,
            "arrivee_background_color": "red",
            "arrivee_icon_size": 20,
            "arrivee_icon_inner_size": 10,
        }[x]

    def test_map_grand_arrivee(self):
        # Test without final_popup
        result = map_grand_arrivee(self.activities1, self.settings, final_popup=False)
        # Check the properties of the marker
        marker = list(result._children.values())[0]
        self.assertIsInstance(marker, folium.map.Marker)
        self.assertEqual(marker.location, [46.0, 8.0])
        self.assertEqual(marker.icon.options["id"], "grand_arrivee")

        self.assertIsInstance(result, folium.FeatureGroup)
        self.assertEqual(result.tile_name, "Grand arrivee")

    def test_map_grand_arrivee_no_dates(self):
        # Test without final_popup
        result = map_grand_arrivee(self.activities2, self.settings, final_popup=False)
        # Check the properties of the marker
        marker = list(result._children.values())[0]
        self.assertIsInstance(marker, folium.map.Marker)
        self.assertEqual(marker.location, [48.0, 10.0])
        self.assertEqual(marker.icon.options["id"], "grand_arrivee")

        self.assertIsInstance(result, folium.FeatureGroup)
        self.assertEqual(result.tile_name, "Grand arrivee")


if __name__ == "__main__":
    unittest.main()
