import unittest
from app.models.activity_model import Activity
import pandas as pd


class TestActivityModel(unittest.TestCase):
    class TestActivityModel(unittest.TestCase):
        def test_get_field_names(self):
            # Expected field names based on the Activity model
            expected_field_names = [
                "name",
                "id",
                "start_date",
                "end_date",
                "date",
                "type",
                "map_polyline",
                "start_latlng",
                "end_latlng",
                "map_elevation",
                "map_distance",
                "start_location",
                "end_location",
                "metadata",
                "source",
                "ready",
            ]

            # Call the method
            field_names = Activity.get_field_names()

            # Assert that the returned field names match the expected field names
            self.assertListEqual(field_names, expected_field_names)

        def test_convert_df_valid_data(self):
            # Create a valid DataFrame
            data = {
                "name": ["Activity 1"],
                "type": ["Run"],
                "map_polyline": [[(0.0, 0.0), (1.0, 1.0)]],
                "start_latlng": [[0.0, 0.0]],
                "end_latlng": [[1.0, 1.0]],
                "metadata": [{}],
                "source": ["GPS"],
                "ready": [True],
            }
            df = pd.DataFrame(data)

            # Call the method
            validated_activities = Activity.convert_df(df)

            # Assert that the returned list contains one valid Activity object
            self.assertEqual(len(validated_activities), 1)
            self.assertIsInstance(validated_activities[0], Activity)
            self.assertEqual(validated_activities[0].name, "Activity 1")

        def test_convert_df_invalid_data(self):
            # Create a DataFrame with invalid data
            data = {
                "name": ["Activity 1"],
                "type": [None],  # Invalid type
                "map_polyline": [[(0.0, 0.0), (1.0, 1.0)]],
                "start_latlng": [[0.0, 0.0]],
                "end_latlng": [[1.0, 1.0]],
                "metadata": [{}],
                "source": ["GPS"],
                "ready": [True],
            }
            df = pd.DataFrame(data)

            # Call the method
            validated_activities = Activity.convert_df(df)

            # Assert that the returned list is empty due to validation error
            self.assertEqual(len(validated_activities), 0)

        def test_convert_df_mixed_data(self):
            # Create a DataFrame with mixed valid and invalid data
            data = {
                "name": ["Activity 1", "Activity 2"],
                "type": ["Run", None],  # Second row has invalid type
                "map_polyline": [[(0.0, 0.0), (1.0, 1.0)], [(0.0, 0.0), (1.0, 1.0)]],
                "start_latlng": [[0.0, 0.0], [0.0, 0.0]],
                "end_latlng": [[1.0, 1.0], [1.0, 1.0]],
                "metadata": [{}, {}],
                "source": ["GPS", "GPS"],
                "ready": [True, True],
            }
            df = pd.DataFrame(data)

            # Call the method
            validated_activities = Activity.convert_df(df)

            # Assert that only the valid row is returned
            self.assertEqual(len(validated_activities), 1)
            self.assertIsInstance(validated_activities[0], Activity)
            self.assertEqual(validated_activities[0].name, "Activity 1")

    if __name__ == "__main__":
        unittest.main()
