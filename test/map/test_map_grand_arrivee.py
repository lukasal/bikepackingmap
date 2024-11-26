import unittest
import folium
import pandas as pd
from app.map.map_grand_arrivee import map_grand_arrivee


class TestMapGrandArrivee(unittest.TestCase):

    def setUp(self):
        # Sample data for activities
        self.activities = pd.DataFrame(
            {
                "end_date": ["2023-10-01", "2023-10-02"],
                "map.polyline": [
                    [(45.0, 7.0), (46.0, 8.0)],
                    [(47.0, 9.0), (48.0, 10.0)],
                ],
                "end_location": ["Location A", "Location B"],
            }
        )
        # Convert end_date to datetime
        self.activities["end_date"] = pd.to_datetime(self.activities["end_date"])
        self.settings = {}

    def test_map_grand_arrivee(self):
        # Test without final_popup
        result = map_grand_arrivee(self.activities, self.settings, final_popup=False)
        # Check the properties of the marker
        marker = list(result._children.values())[0]
        self.assertIsInstance(marker, folium.map.Marker)
        self.assertEqual(marker.location, [48.0, 10.0])
        self.assertEqual(marker.icon.options["id"], "grand_arrivee")

        self.assertIsInstance(result, folium.FeatureGroup)
        self.assertEqual(result.tile_name, "Grand arrivee")


if __name__ == "__main__":
    unittest.main()
