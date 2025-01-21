import unittest
from datetime import datetime
from app.map.map_popup import html_popup

# import html5lib


class TestHtmlPopup(unittest.TestCase):
    def setUp(self):
        self.template_path = "templates/map/popup.html"
        self.row_values = {
            "name": "Test Name",
            "date": "2023-10-01",
            "start_date": datetime(2023, 10, 1, 14, 30),
            "type": "Test Type",
            "metadata": {
                "distance": 10.5,
                "total_elevation_gain": 200.01,
                "moving_time": 3600,
                "elapsed_time": 4000,
                "average_speed": 2.50235,
                "max_speed": 3.000001,
                "average_heartrate": 120,
                "max_heartrate": 150,
                "average_temp": 20.0,
                "elevation_profile": "Test Profile",
            },
        }
        self.parser = html5lib.HTMLParser(strict=True)

    def test_html_popup(self):
        result = html_popup(self.row_values, self.template_path)
        # Validate the HTML content
        self.parser.parse(result)  # This should raise no exception if the HTML is valid
        self.assertIn("Test Name", result)
        self.assertIn("2023-10-01", result)
        self.assertIn("14:30:00", result)
        self.assertIn("Test Type", result)
        self.assertIn("10.50", result)
        self.assertIn("200", result)
        self.assertIn("01:00:00", result)
        self.assertIn("01:06:40", result)
        self.assertIn("2.50", result)
        self.assertIn("3.00", result)
        self.assertIn("120", result)
        self.assertIn("150", result)
        self.assertIn("20.0", result)
        self.assertIn("Test Profile", result)

    def test_html_popup_missing_optional_fields(self):
        row_values = {
            "name": "Test Name",
            "date": "2023-10-01",
            "type": "Test Type",
            "metadata": {},
        }

        result = html_popup(row_values, self.template_path)
        self.parser.parse(result)  # This should raise no exception if the HTML is valid

        self.assertIn("Test Name", result)
        self.assertIn("2023-10-01", result)
        self.assertIn("Test Type", result)

    def test_html_popup_no_metadata(self):
        row_values = {
            "name": "Test Name",
            "date": "2023-10-01",
            "type": "Test Type",
        }

        result = html_popup(row_values, self.template_path)
        self.parser.parse(result)  # This should raise no exception if the HTML is valid
        self.assertIn("Test Name", result)
        self.assertIn("2023-10-01", result)
        self.assertIn("Test Type", result)


if __name__ == "__main__":
    unittest.main()
