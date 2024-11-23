import unittest
from unittest.mock import patch, MagicMock
from flask import Flask, session, request
import sys
from os.path import abspath, dirname, realpath
import pickle

PATH = realpath(abspath(__file__))
sys.path.insert(0, dirname(dirname(PATH)))
from app.endpoints import create_app


class TestStravaRedirect(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    @patch("requests.post")
    def test_strava_redirect_no_authorization_code(self, mock_post):
        with self.client as client:
            response = client.get("/redirect")
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                b"Authorization failed: No authorization code provided!", response.data
            )

    @patch("requests.post")
    def test_strava_redirect_successful_token_exchange(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_at": 1234567890,
        }
        mock_post.return_value = mock_response

        with self.client as client:
            response = client.get("/redirect?code=test_code")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, "/display_strava")
            self.assertEqual(session["access_token"], "test_access_token")

    @patch("requests.post")
    def test_strava_redirect_failed_token_exchange(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with self.client as client:
            response = client.get("/redirect?code=test_code")
            self.assertEqual(response.status_code, 500)
            self.assertIn(
                b"Error: Unable to retrieve access token. Response: Bad Request",
                response.data,
            )

    @patch("requests.post", side_effect=Exception("Test Exception"))
    def test_strava_redirect_exception(self, mock_post):
        with self.client as client:
            response = client.get("/redirect?code=test_code2")
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"An error occurred: Test Exception", response.data)


if __name__ == "__main__":
    unittest.main()
