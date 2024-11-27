import unittest
from unittest.mock import patch, mock_open
from app.map.MapSettings import MapSettings
from app.map.InteractiveSetting import (
    BooleanSetting,
    ColorSetting,
    NumberSetting,
    TextSetting,
)
import pandas as pd


class TestMapSettings(unittest.TestCase):

    def setUp(self):
        activities = pd.DataFrame({"type": []})
        self.map_settings = MapSettings(activities)

    def test_load_settings(
        self,
    ):
        activities = pd.DataFrame({"type": ["run", "bike"]})
        map_settings = MapSettings(activities, "test/data/dummy_config.yaml")

        self.assertIn("line_color_run", map_settings.interactive_settings)
        self.assertIn("line_color_bike", map_settings.interactive_settings)
        self.assertIn("test_thickness", map_settings.interactive_settings)
        self.assertIn("test_stroke", map_settings.interactive_settings)
        self.assertEqual(map_settings.interactive_settings["test_thickness"].value, 5)
        self.assertEqual(map_settings.interactive_settings["test_stroke"].value, True)

    def test_not_load_settings(
        self,
    ):
        activities = pd.DataFrame({"type": ["run", "bike"]})
        map_settings = MapSettings(activities)

        self.assertEqual(len(map_settings.interactive_settings), 2)
        self.assertIn("line_color_run", map_settings.interactive_settings)
        self.assertIn("line_color_bike", map_settings.interactive_settings)

    def test_add_setting_boolean(self):

        self.map_settings.add_setting(
            id="test_boolean",
            type="BooleanSetting",
            group="Test",
            label="Test Boolean",
            value=True,
        )
        self.assertIn("test_boolean", self.map_settings.interactive_settings)
        self.assertIsInstance(
            self.map_settings.interactive_settings["test_boolean"], BooleanSetting
        )
        self.assertEqual(
            self.map_settings.interactive_settings["test_boolean"].value, True
        )

    def test_add_setting_color(self):

        self.map_settings.add_setting(
            id="test_color",
            type="ColorSetting",
            group="Test",
            label="Test Color",
            value="#FFFFFF",
        )
        self.assertIn("test_color", self.map_settings.interactive_settings)
        self.assertIsInstance(
            self.map_settings.interactive_settings["test_color"], ColorSetting
        )
        self.assertEqual(
            self.map_settings.interactive_settings["test_color"].value, "#FFFFFF"
        )

    def test_add_setting_number(self):

        self.map_settings.add_setting(
            id="test_number",
            type="NumberSetting",
            group="Test",
            label="Test Number",
            value=42,
        )
        self.assertIn("test_number", self.map_settings.interactive_settings)
        self.assertIsInstance(
            self.map_settings.interactive_settings["test_number"], NumberSetting
        )
        self.assertEqual(
            self.map_settings.interactive_settings["test_number"].value, 42
        )

    def test_add_setting_text(self):

        self.map_settings.add_setting(
            id="test_text",
            type="TextSetting",
            group="Test",
            label="Test Text",
            value="Hello, World!",
        )
        self.assertIn("test_text", self.map_settings.interactive_settings)
        self.assertIsInstance(
            self.map_settings.interactive_settings["test_text"], TextSetting
        )
        self.assertEqual(
            self.map_settings.interactive_settings["test_text"].value, "Hello, World!"
        )

    def test_get_interactive_groups(self):

        self.map_settings.add_setting(
            id="test_number",
            type="NumberSetting",
            group="Group1",
            label="Test Number",
            value=42,
        )
        self.map_settings.add_setting(
            id="test_text",
            type="TextSetting",
            group="Group2",
            label="Test Text",
            value="Hello, World!",
        )
        groups = self.map_settings.get_interactive_groups()
        self.assertEqual(groups, ["Group1", "Group2"])

    def test_set_interactive_setting_number(self):

        self.map_settings.add_setting(
            id="test_number",
            type="NumberSetting",
            group="Test",
            label="Test Number",
            value=42,
        )
        self.map_settings.set_interactive_setting("test_number", 100)
        self.assertEqual(
            self.map_settings.interactive_settings["test_number"].value, 100
        )
        self.map_settings.set_interactive_setting("test_number", "200")
        self.assertEqual(
            self.map_settings.interactive_settings["test_number"].value, 200
        )
        self.map_settings.set_interactive_setting("test_number", "300.5")
        self.assertEqual(
            self.map_settings.interactive_settings["test_number"].value, 300.5
        )

    def test_set_interactive_setting_boolean(self):

        self.map_settings.add_setting(
            id="test_boolean",
            type="BooleanSetting",
            group="Test",
            label="Test Boolean",
            value=True,
        )
        self.map_settings.set_interactive_setting("test_boolean", False)
        self.assertEqual(
            self.map_settings.interactive_settings["test_boolean"].value, False
        )
        self.map_settings.set_interactive_setting("test_boolean", "true")
        self.assertEqual(
            self.map_settings.interactive_settings["test_boolean"].value, True
        )
        self.map_settings.set_interactive_setting("test_boolean", "false")
        self.assertEqual(
            self.map_settings.interactive_settings["test_boolean"].value, False
        )

    def test_set_interactive_setting_color(self):

        self.map_settings.add_setting(
            id="test_color",
            type="ColorSetting",
            group="Test",
            label="Test Color",
            value="#FFFFFF",
        )
        self.map_settings.set_interactive_setting("test_color", "#000000")
        self.assertEqual(
            self.map_settings.interactive_settings["test_color"].value, "#000000"
        )

    def test_set_interactive_setting_text(self):

        self.map_settings.add_setting(
            id="test_text",
            type="TextSetting",
            group="Test",
            label="Test Text",
            value="Hello, World!",
        )
        self.map_settings.set_interactive_setting("test_text", "New Text")
        self.assertEqual(
            self.map_settings.interactive_settings["test_text"].value, "New Text"
        )

    def test_set_interactive_setting_not_found(self):

        with self.assertRaises(KeyError):
            self.map_settings.set_interactive_setting("non_existent_setting", "value")

    def test_get_interactive_setting(self):

        self.map_settings.add_setting(
            id="test_text",
            type="TextSetting",
            group="Test",
            label="Test Text",
            value="Hello, World!",
        )
        self.assertEqual(
            self.map_settings.get_interactive_setting("test_text"), "Hello, World!"
        )


if __name__ == "__main__":
    unittest.main()
