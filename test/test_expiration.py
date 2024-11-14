import unittest
from flask import Flask, session, redirect, url_for
import time
import sys
import os
from os.path import abspath, dirname, realpath

PATH = realpath(abspath(__file__))
sys.path.insert(0, dirname(dirname(PATH)))

from app.endpoints import create_app
from app.redis_client import redis_client # Adjust the import path accordingly


SESSION_EXPIRATION = 4

class TestSessionLogic(unittest.TestCase):
    
    def setUp(self):
        # Create the Flask test client
        os.environ["SESSION_EXP_TIME"]= str(SESSION_EXPIRATION)
        self.app = create_app().test_client()
        self.app.testing = True

        # Ensure that Redis is clear before each test
        redis_client.flushdb()

    def test_session_initialization(self):
        """Test that a session ID is set if one doesn't exist"""
        with self.app:
            # Send a request to the app (this will trigger the before_request logic)
            response = self.app.get('/')

            # Check if session_id is set
            self.assertIn('session_id', session)
            # Check if session is stored in Redis
            self.assertTrue(redis_client.exists(f"session:{session['session_id']}"))

    def test_session_expiration(self):
        """Test that the session expires after idle time"""
        with self.app:
            # Simulate an initial request (sets session and last_activity)
            self.app.get('/')
            session_id = session['session_id']

            time.sleep(SESSION_EXPIRATION)
            # Check if session is stored in Redis
            self.assertFalse(redis_client.exists(f"session:{session['session_id']}"))
            # Manually set last_activity to be expired
            #session['last_activity'] = time.time() - SESSION_EXPIRATION - 1  # Expires after 10 minutes

            # Send another request (this should trigger the session expiration)
            response = self.app.get('/')

            # Assert that session is cleared and redirected
            self.assertEqual(response.status_code, 302)  # Expecting a redirect
            self.assertIn('/session-expired', response.location)
            self.assertNotIn('session_id', session)  # No session_id is available

    def test_redis_expiration(self):
        """Test that the session's Redis data expiration is set correctly"""
        with self.app:
            # Trigger the session creation
            response = self.app.get('/')
            session_id = session['session_id']

            # Check if Redis expiration is set
            ttl = redis_client.ttl(f"session:{session_id}")
            self.assertGreaterEqual(ttl, 0)  # TTL should be greater than or equal to 0 seconds
            self.assertLessEqual(ttl, SESSION_EXPIRATION)  # TTL should not exceed SESSION_EXPIRATION

if __name__ == '__main__':
    unittest.main()