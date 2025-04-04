from flask import session, request, redirect, url_for, jsonify
from app.activity_manager.activity_manager import ActivityManager
from app.utils.redis_client import redis_client
import os

def ensure_session_id():
    """
    Ensure each user has a unique session ID stored as a cookie.
    This is run before every request.
    """
    SESSION_EXPIRATION = int(os.getenv("SESSION_EXP_TIME", 1800))

    # session expired, then the redis client has deleted the content
    if (
        "session_id" in session
        and redis_client.exists(f"session:{session['session_id']}") != 1
    ):
        session.clear()
        # Check if the request is AJAX
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return (
                jsonify({"session_expired": True}),
                401,
            )  # Send a JSON response indicating session expired
        else:
            return redirect(
                "/session-expired"
            )  # For regular requests, perform a redirect
    # new session
    if "session_id" not in session:
        # Generate a new session ID if one doesn't exist
        session["session_id"] = os.urandom(16).hex()
        ActivityManager(session["session_id"])
    # session ok
    else:
        redis_client.expire(f"session:{session['session_id']}", SESSION_EXPIRATION)
