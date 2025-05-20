import unittest
from flask import session
from redis import Redis
import time
import os

from app import create_app
from app.utils.cache import cache  # Adjust the import path accordingly
from parameterized import parameterized

SESSION_EXPIRATION = 4


class TestSessionLogicRedis(unittest.TestCase):
    @parameterized.expand(
        [
            ("redis",),  # Run this test with Redis
            ("simple",),  # Run this test with SimpleCache
        ]
    )
    def test_session_initialization(self, cache_type):
        """Test that a session ID is set if one doesn't exist"""
        # Create the Flask test client
        os.environ["CACHE_TYPE"] = cache_type
        os.environ["SESSION_EXP_TIME"] = str(SESSION_EXPIRATION)
        self.app = create_app()
        cache.init_app(self.app, config={"CACHE_TYPE": os.getenv("CACHE_TYPE")})

        self.app.config["TESTING"] = True
        self.app.config["PROPAGATE_EXCEPTIONS"] = True
        self.app.config["CACHE_TYPE"] = cache_type
        self.client = self.app.test_client()
        self.client.testing = True

        if cache_type == "redis":
            self.assertIsInstance(
                cache.cache._read_client,
                Redis,
                "Cache client should be a Redis instance",
            )
        else:
            self.assertIsInstance(
                cache.cache._cache,
                dict,
                "Cache client should be a SimpleCache instance",
            )

        with self.client:
            # Send a request to the client (this will trigger the before_request logic)
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            # Check if session_id is set
            self.assertIn("session_id", session)
            # Check if session is stored in Cache
            self.assertTrue(cache.has(f"session:{session['session_id']}"))

    @parameterized.expand(
        [
            ("redis",),  # Run this test with Redis
            ("simple",),  # Run this test with SimpleCache
        ]
    )
    def test_session_expiration(self, cache_type):
        """Test that the session expires after idle time"""
        # Create the Flask test client
        os.environ["CACHE_TYPE"] = cache_type
        os.environ["SESSION_EXP_TIME"] = str(SESSION_EXPIRATION)
        self.app = create_app()
        cache.init_app(self.app, config={"CACHE_TYPE": os.getenv("CACHE_TYPE")})
        self.app.config["TESTING"] = True
        self.app.config["PROPAGATE_EXCEPTIONS"] = True
        self.app.config["CACHE_TYPE"] = cache_type
        self.client = self.app.test_client()
        self.client.testing = True

        if cache_type == "redis":
            self.assertIsInstance(
                cache.cache._read_client,
                Redis,
                "Cache client should be a Redis instance",
            )
        else:
            self.assertIsInstance(
                cache.cache._cache,
                dict,
                "Cache client should be a SimpleCache instance",
            )

        with self.client:
            # Simulate an initial request (sets session and last_activity)
            self.client.get("/")

            time.sleep(SESSION_EXPIRATION)
            # Check if session is stored in Cache
            self.assertFalse(cache.has(f"session:{session['session_id']}"))
            # Manually set last_activity to be expired
            # session['last_activity'] = time.time() - SESSION_EXPIRATION - 1  # Expires after 10 minutes

            # Send another request (this should trigger the session expiration)
            response = self.client.get("/static/page-what.html")

            # Assert that session is cleared and redirected
            self.assertEqual(response.status_code, 302)  # Expecting a redirect
            self.assertIn("/session-expired", response.location)
            self.assertNotIn("session_id", session)  # No session_id is available

    @parameterized.expand(
        [
            ("redis",),  # Run this test with Redis
            ("simple",),  # Run this test with SimpleCache
        ]
    )
    def test_session_renewed(self, cache_type):
        """Test that the session expires after idle time"""
        # Create the Flask test client
        os.environ["CACHE_TYPE"] = cache_type
        os.environ["SESSION_EXP_TIME"] = str(SESSION_EXPIRATION)
        self.app = create_app()
        cache.init_app(self.app, config={"CACHE_TYPE": os.getenv("CACHE_TYPE")})
        self.app.config["TESTING"] = True
        self.app.config["PROPAGATE_EXCEPTIONS"] = True
        self.client = self.app.test_client()
        self.client.testing = True
        print(cache.cache)

        if cache_type == "redis":
            self.assertIsInstance(
                cache.cache._read_client,
                Redis,
                "Cache client should be a Redis instance",
            )
        else:
            self.assertIsInstance(
                cache.cache._cache,
                dict,
                "Cache client should be a SimpleCache instance",
            )

        with self.client:
            # Simulate an initial request (sets session and last_activity)
            self.client.get("/")

            time.sleep(int(SESSION_EXPIRATION * 2 / 3))
            # Check if session is stored in Cache
            self.assertTrue(cache.has(f"session:{session['session_id']}"))
            # Manually set last_activity to be expired
            # session['last_activity'] = time.time() - SESSION_EXPIRATION - 1  # Expires after 10 minutes

            # Send another request (this should trigger the session expiration)
            response = self.client.get("/static/page-what.html")

            time.sleep(int(SESSION_EXPIRATION * 2 / 3))

            self.assertTrue(cache.has(f"session:{session['session_id']}"))
            # Manually set last_activity to be expired
            # session['last_activity'] = time.time() - SESSION_EXPIRATION - 1  # Expires after 10 minutes

            # Send another request (this should trigger the session expiration)
            response = self.client.get("/static/page-what.html")
            # Check if session is stored in Cache
            self.assertTrue(cache.has(f"session:{session['session_id']}"))
            # Assert that session is not cleared and redirected
            self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
