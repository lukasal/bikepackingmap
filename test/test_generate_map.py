import unittest
import os

import sys
from os.path import abspath, dirname, realpath
import pickle
from bs4 import BeautifulSoup

PATH = realpath(abspath(__file__))
sys.path.insert(0, dirname(dirname(PATH)))
from app.map.generate_map import generate_map
from app.map.MapSettings import MapSettings


class TestMapMarkers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        with open("data/giro_italia_example_preprocessed.pkl", "rb") as file:
            data_processed = pickle.load(file)

        settings = MapSettings(data_processed)
        generate_map(settings, data_processed, out_file="test_map.html")
        # Set up the Selenium WebDriver
        # cls.driver = webdriver.Chrome()
        # cls.driver.get("file://" + os.path.abspath("test_map.html"))
        with open("test_map.html", "r", encoding="utf-8") as file:
            html_content = file.read()

        cls.soup = BeautifulSoup(html_content, "html.parser")

    @classmethod
    def tearDownClass(cls):
        # Quit the WebDriver
        os.remove("test_map.html")

    def test_tiles_present(self):
        # Find all script tags
        script_tags = self.soup.find_all("script")

        # Check if the id "grand_depart" is in the BeautifyIcon configuration
        found = False
        for script in script_tags:
            if script.string and "L.tileLayer(" in script.string:
                if '"id": "primary_layer"' in script.string:
                    found = True
                    break

        self.assertTrue(
            found,
            "The tiles were not found in the html.",
        )

    def test_polylines_count(self):

        # Find all script tags and count occurrences of 'var poly_line'
        script_tags = self.soup.find_all("script")
        polyline_count = 0
        for script in script_tags:
            if script.string:
                polyline_count += script.string.count("var poly_line_")

        # Assert that there are 23 polylines
        self.assertEqual(polyline_count, 50)

    def test_icon_grand_depart(self):
        # Find all script tags
        script_tags = self.soup.find_all("script")

        # Check if the id "grand_depart" is in the BeautifyIcon configuration
        found = False
        for script in script_tags:
            if script.string and "L.BeautifyIcon.icon(" in script.string:
                if '"id": "grand_depart"' in script.string:
                    found = True
                    break

        self.assertTrue(
            found,
            'The "grand_depart" icon was not found in the html.',
        )

    def test_icon_grand_arrivee(self):
        # Find all script tags
        script_tags = self.soup.find_all("script")

        # Check if the id "grand_depart" is in the BeautifyIcon configuration
        found = False
        for script in script_tags:
            if script.string and "L.BeautifyIcon.icon(" in script.string:
                if '"id": "grand_arrivee"' in script.string:
                    found = True
                    break

        self.assertTrue(
            found,
            'The "grand_arrivee" icon was not found in the html.',
        )

    def test_beautify_icons_count(self):
        # Find all script tags
        script_tags = self.soup.find_all("script")

        # Count the number of BeautifyIcon configurations
        beautify_icon_count = 0
        for script in script_tags:
            if script.string and "L.BeautifyIcon.icon(" in script.string:
                beautify_icon_count += script.string.count("L.BeautifyIcon.icon(")

        # Assert that there are 21 BeautifyIcons (or the number you added)
        self.assertEqual(
            beautify_icon_count,
            22,
            "not the right amount of stage icons were found in the html.",
        )


if __name__ == "__main__":
    unittest.main()
