import unittest
from flask import Flask, jsonify
from app import create_app
import traceback

class TestErrorHandlers(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing = True

        # # Register error handlers
        # from app.utils.error_handlers import error_bp
        # self.app.register_blueprint(error_bp)

        # Define a route to simulate an internal server error
        @self.app.route("/trigger-500")
        def trigger_500():
            raise Exception("Simulated internal server error")

        self.client = self.app.test_client()

    def test_not_found_error(self):
        response = self.client.get("/non-existent-endpoint")
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "The page you're looking for doesn't exist.",
            response.get_data(as_text=True),
        )
        self.assertIn("<html", response.get_data(as_text=True).lower())

    def test_not_found_error_ajax(self):
        response = self.client.get(
            "/non-existent-endpoint", headers={"X-Requested-With": "XMLHttpRequest"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("Resource not found", response.get_json()["error"])

    @unittest.mock.patch("app.utils.error_handlers.upload_to_blob")
    def test_internal_error(self, mock_upload_to_blob):
        response = self.client.get("/trigger-500")
        self.assertEqual(response.status_code, 500)
        self.assertIn("internal server error", response.get_data(as_text=True).lower())
        self.assertIn("<html", response.get_data(as_text=True).lower())

    @unittest.mock.patch("app.utils.error_handlers.upload_to_blob")
    def test_internal_error_ajax(self, mock_upload_to_blob):
        response = self.client.get(
            "/trigger-500",
            headers={"X-Requested-With": "XMLHttpRequest"}
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("internal server error", response.get_json()["error"].lower())

if __name__ == "__main__":
    unittest.main()
