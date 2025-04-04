from flask import (
    Blueprint,
    redirect,
    request,
    session,
    url_for,
    render_template,
    jsonify,
)
import requests
import os
from datetime import datetime, timedelta

from app.activity_manager.activity_manager import ActivityManager
from app.helper import parse_date
from app.strava.process_strava import process_strava
from app.strava.get_data import get_data

strava_bp = Blueprint("strava", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/redirect")
STRAVA_AUTH_URL = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=read,activity:read"
)


@strava_bp.route("/strava_auth")
def strava_auth():
    return redirect(STRAVA_AUTH_URL)


@strava_bp.route("/redirect")
def strava_redirect():
    authorization_code = request.args.get("code")
    if not authorization_code:
        return "Authorization failed: No authorization code provided!", 400

    try:
        token_response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": authorization_code,
                "grant_type": "authorization_code",
            },
        )

        if token_response.status_code != 200:
            return (
                f"Error: Unable to retrieve access token. Response: {token_response.text}",
                500,
            )

        token_data = token_response.json()
        session["access_token"] = token_data.get("access_token")
        return redirect(url_for("strava.display_strava"))
    except Exception as e:
        return f"An error occurred: {str(e)}", 500


@strava_bp.route("/display_strava")
def display_strava():
    return render_template(
        "home/select_activities.html",
        fetch_url="/fetch_strava",
        show_calendar=True,
        show_upload_button=False,
    )


@strava_bp.route("/fetch_strava", methods=["POST"])
def fetch_strava():  

    # Get the current user's ActivityManager
    session_id = session['session_id']
    activity_manager = ActivityManager.load_from_redis(session_id)       
    # Extract parameters
    start_date = request.form.get("start_date")
    # Convert string dates to datetime objects
    start_date = parse_date(start_date)

    end_date = request.form.get("end_date")
    end_date = parse_date(end_date, timedelta(days=1))
    per_page = int(request.form.get("per_page", 10))

    activity_manager.reset()
    # get Activities from strava API
    data = get_data(session['access_token'], start_date, end_date, per_page=per_page, page=1)
    # normalize data to Activity type
    data = process_strava(data)
    # Add activities to the DataFrame
    activity_manager.add_activities(data)

    return jsonify({"data": activity_manager.send_to_frontend()})
