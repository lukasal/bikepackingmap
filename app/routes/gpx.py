from flask import Blueprint, request, session, render_template, jsonify
from app.activity_manager.activity_manager import ActivityManager
from app.gpx.process_gpx import process_gpx_data
from datetime import datetime

gpx_bp = Blueprint("gpx", __name__)


@gpx_bp.route("/display_gpx")
def display_gpx():
    return render_template(
        "home/select_activities.html",
        fetch_url="/fetch_gpx",
        show_calendar=False,
        show_upload_button=True,
    )


@gpx_bp.route("/fetch_gpx", methods=["POST"])
def fetch_gpx():
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)
    activity_manager.reset()
    files = request.files.getlist("gpx_files")

    activities = []
    for file in files:
        activities.append(process_gpx_data(file))

    sorted_activities = sorted(
        activities,
        key=lambda activity: (
            (activity.start_date if activity.start_date is not None else datetime.max),
            activity.name,
        ),
    )
    activity_manager.add_activities(sorted_activities)

    return jsonify({"data": activity_manager.send_to_frontend()})
