import unittest
import folium
from app.map.add_tiles import add_tiles
import sys
import os
from os.path import abspath, dirname, realpath

# PATH = realpath(abspath(__file__))
# sys.path.insert(0, dirname(dirname(PATH)))


class TestAddTiles(unittest.TestCase):

    def setUp(self):
        self.map = folium.Map(location=[45.5236, -122.6750])
        self.settings = type(
            "obj",
            (object,),
            {
                "tiles": {
                    "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    "Stamen Terrain": "https://{s}.tile.stamen.com/terrain/{z}/{x}/{y}.jpg",
                }
            },
        )

    def test_add_tiles_with_dynamic_tiles(self):
        result_map = add_tiles(self.map, self.settings, "OpenStreetMap", True)
        self.assertEqual(
            len(result_map._children), 4
        )  # 2 TileLayers + 1 LayerControl + 1 Map

    def test_add_tiles_without_dynamic_tiles(self):
        result_map = add_tiles(self.map, self.settings, "OpenStreetMap", False)
        self.assertEqual(len(result_map._children), 2)  # 1 TileLayer + 1 Map

    def test_add_tiles_with_invalid_tile_name(self):
        with self.assertRaises(KeyError):
            add_tiles(self.map, self.settings, "InvalidTileName", False)


if __name__ == "__main__":
    unittest.main()
