import unittest
from app.map.helper import centroid
from app.map.helper import bounding_box


class TestMapHelperFunctions(unittest.TestCase):

    def test_centroid_single_polyline(self):
        polylines = [[[0, 2], [2, 4], [4, 0]]]
        result = centroid(polylines)
        expected = [2, 2]
        self.assertEqual(result, expected)

    def test_centroid_multiple_polylines(self):
        polylines = [[[0, 0], [2, 2]], [[4, 4], [6, 6]]]
        result = centroid(polylines)
        expected = [3, 3]
        self.assertEqual(result, expected)

    def test_centroid_negative_coordinates(self):
        polylines = [[[-1, -1], [-3, -3]], [[-5, -5], [-7, -7]]]
        result = centroid(polylines)
        expected = [-4, -4]
        self.assertEqual(result, expected)

    def test_centroid_mixed_coordinates(self):
        polylines = [[[1, 1], [-1, -1]], [[3, 3], [-3, -3]]]
        result = centroid(polylines)
        expected = [0, 0]
        self.assertEqual(result, expected)

    def test_bounding_box_single_polyline(self):
        polylines = [[[0, 0], [2, 2], [4, 4]]]
        result = bounding_box(polylines)
        expected = [[-0.3, -0.3], [4.3, 4.3]]
        self.assertEqual(result, expected)

    def test_bounding_box_multiple_polylines(self):
        polylines = [[[0, 0], [2, 2]], [[4, 4], [6, 6]]]
        result = bounding_box(polylines)
        expected = [[-0.3, -0.3], [6.3, 6.3]]
        self.assertEqual(result, expected)

    def test_bounding_box_negative_coordinates(self):
        polylines = [[[-1, -1], [-3, -3]], [[-5, -5], [-7, -7]]]
        result = bounding_box(polylines)
        expected = [[-7.3, -7.3], [-0.7, -0.7]]
        self.assertEqual(result, expected)

    def test_bounding_box_mixed_coordinates(self):
        polylines = [[[1, 1], [-1, -1]], [[3, 3], [-3, -3]]]
        result = bounding_box(polylines)
        expected = [[-3.3, -3.3], [3.3, 3.3]]
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
