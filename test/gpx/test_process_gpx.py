import unittest
import pandas as pd
from io import BytesIO
from app.gpx.process_gpx import process_gpx_data
from app.models.activity_model import Activity

class MockFileStorage:
    def __init__(self, filename, stream):
        self.filename = filename
        self.stream = stream


class TestProcessGpxData(unittest.TestCase):

    def test_process_gpx_data_with_tracks(self):
        gpx_data = """
        <gpx version="1.1" creator="test">
            <trk>
                <name>Test Track</name>
                <trkseg>
                    <trkpt lat="52.5200" lon="13.4050">
                        <ele>34.0</ele>
                        <time>2023-01-01T12:00:00Z</time>
                    </trkpt>
                    <trkpt lat="52.5201" lon="13.4051">
                        <ele>36.0</ele>
                        <time>2023-01-01T12:01:00Z</time>
                    </trkpt>
                </trkseg>
            </trk>
        </gpx>
        """
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)

        self.assertIsInstance(result, Activity)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.type, "GPX")
        self.assertEqual(result.start_latlng, [52.5200, 13.4050])
        self.assertEqual(result.end_latlng, [52.5201, 13.4051])
        self.assertEqual(result.map_polyline, [(52.5200, 13.4050), (52.5201, 13.4051)])
        self.assertGreater(result.metadata["distance"], 0)

    def test_process_gpx_data_with_routes(self):
        gpx_data = """
        <gpx version="1.1" creator="test">
            <rte>
                <name>Test Route</name>
                <rtept lat="52.5200" lon="13.4050">
                    <ele>34.0</ele>
                </rtept>
                <rtept lat="52.5201" lon="13.4051">
                    <ele>36.0</ele>
                </rtept>
            </rte>
        </gpx>
        """
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)

        self.assertIsInstance(result, Activity)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.type, "GPX")
        self.assertEqual(result.map_polyline, [(52.5200, 13.4050), (52.5201, 13.4051)])
        self.assertEqual(result.start_latlng, [52.5200, 13.4050])
        self.assertEqual(result.end_latlng, [52.5201, 13.4051])
        self.assertGreater(result.metadata["distance"], 0)

    def test_process_gpx_data_with_no_tracks_or_routes(self):
        gpx_data = """
        <gpx version="1.1" creator="test">
        </gpx>
        """
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)

        self.assertIsNone(result)

    def test_process_gpx_data_with_missing_elevation(self):
        gpx_data = """
        <gpx version="1.1" creator="test">
            <trk>
                <name>Test Track</name>
                <trkseg>
                    <trkpt lat="52.5200" lon="13.4050">
                        <time>2023-01-01T12:00:00Z</time>
                    </trkpt>
                    <trkpt lat="52.5201" lon="13.4051">
                        <time>2023-01-01T12:01:00Z</time>
                    </trkpt>
                </trkseg>
            </trk>
        </gpx>
        """
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)
        self.assertEqual(result.name, "test")
        self.assertEqual(result.start_latlng, [52.5200, 13.4050])
        self.assertEqual(result.end_latlng, [52.5201, 13.4051])
        self.assertEqual(result.map_polyline, [(52.5200, 13.4050), (52.5201, 13.4051)])
        self.assertEqual(result.start_date.isoformat(), "2023-01-01T12:00:00+00:00")
        self.assertEqual(result.end_date.isoformat(), "2023-01-01T12:01:00+00:00")
        self.assertEqual(result.date.isoformat(), "2023-01-01")
        self.assertGreater(result.metadata["distance"], 0)
        self.assertIsInstance(result, Activity)

        self.assertIsNone(result.map_elevation)

    def test_process_gpx_data_with_errorous_file(self):
        gpx_data = ""
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)

        self.assertIsNone(result)

    def test_process_gpx_data_with_invalid_gpx(self):
        gpx_data = "<invalid>Not a valid GPX</invalid>"
        file_storage = MockFileStorage("test.gpx", BytesIO(gpx_data.encode("utf-8")))
        result = process_gpx_data(file_storage)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
