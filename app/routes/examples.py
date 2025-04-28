from flask import Blueprint, request, session, jsonify,render_template
from app.activity_manager.activity_manager import ActivityManager
import time
import pickle

examples_bp = Blueprint("examples", __name__)


@examples_bp.route("/fetch_examples", methods=["POST"])
def fetch_examples():
    session_id = session["session_id"]
    start = time.time()
    activity_manager = ActivityManager.load_from_cache(session_id)
    print("fetch_examples", time.time() - start)
    with open("data/giro_italia_example.pkl", "rb") as file:
        example_processed = pickle.load(file)
    print("load data", time.time() - start)
    activity_manager.add_activities(example_processed)
    print("preprocess activities", time.time() - start)
    return jsonify({"data": activity_manager.send_to_frontend()})

@examples_bp.route("/display_examples")
def display_examples():
    return render_template(
        "home/select_activities.html",
        fetch_url="/fetch_examples",
        show_calendar=False,
        show_upload_button=False,
    )
