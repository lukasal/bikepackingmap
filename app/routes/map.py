from flask import Blueprint, request, session, jsonify, render_template, send_file, url_for, redirect
from app.activity_manager.activity_manager import ActivityManager
from app.map.generate_map import generate_map
from app.utils.save_png import save_png
import os

map_bp = Blueprint("map", __name__)


@map_bp.route("/select", methods=["POST"])
def select():
    selected_activities = request.form.getlist("selected_activities")

    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)
    activity_manager.postprocess(selected_activities)
    activity_manager.set_map_ids(selected_activities)

    return redirect(url_for("map.build_map"))


@map_bp.route("/build_map")
def build_map():
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)
    data = activity_manager.get_activities_df(activity_manager.map_ids)
    m = generate_map(
        activity_manager.get_map_settings(),
        data,
        out_file="./templates/tmp/mymap_terrain.html",
        tiles_name="stadia_terrain",
        width="100%",
        height="100%",
        final_popup=False,
        dynamic_tiles=True,
        save=False,
        zoom_margin=0.05,
    )
    return render_template(
        "home/build_map.html",
        map=m._repr_html_(),
        settings=activity_manager.map_settings,
    )


@map_bp.route("/update_map", methods=["POST"])
def update_map():
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)
    settings_data = request.get_json()
    print(settings_data)
    for name, value in settings_data.items():
        try:
            activity_manager.map_settings.set_interactive_setting(name, value)
        except KeyError as e:
            return jsonify({"error": str(e)}), 400

    activity_manager.save()

    m = generate_map(
        activity_manager.get_map_settings(),
        activity_manager.get_activities_df(activity_manager.map_ids),
        out_file="./templates/tmp/mymap_terrain.html",
        tiles_name="stadia_terrain",
        width="100%",
        height="60%",
        final_popup=False,
        dynamic_tiles=True,
        save=False,
        zoom_margin=0.05,
    )

    return jsonify({"map": m._repr_html_()})
