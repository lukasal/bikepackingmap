from flask import Blueprint, request, session, render_template, send_file
from app.activity_manager.activity_manager import ActivityManager
from app.map.generate_map import generate_map
from app.save_png import save_png
from app.elevation_profile import create_elevation_profile
import os

download_bp = Blueprint("download", __name__)


@download_bp.route("/downloads_overview", methods=["GET"])
def downloads_overview():
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)
    return render_template(
        "home/export.html",
        activities=activity_manager.get_activities_df(activity_manager.map_ids),
    )


@download_bp.route("/get_map", methods=["GET"])
def get_map():
    filetype = request.args.get("filetype")
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)

    activity_ids = request.args.get("activity_ids")
    if not activity_ids:
        return "No activities selected.", 400
    elif activity_ids == "all":
        activities_to_map = activity_manager.get_activities_df(activity_manager.map_ids)
        name = "full"
    else:
        activity_ids = [id for id in activity_ids.split(",")]
        activities_to_map = activity_manager.get_activities_df(activity_ids)
        name = "_".join(activities_to_map["name"].tolist())

    filename = f"tmp/{session_id}_{os.urandom(4).hex()}_map.html"
    try:
        if filetype == "html" or filetype == "view":
            generate_map(
                activity_manager.map_settings,
                activities_to_map,
                out_file=filename,
                tiles_name="stadia_terrain",
                final_popup=False,
                dynamic_tiles=True,
                zoom_margin=0.05,
            )
            return send_file(
                filename,
                mimetype="text/html",
                as_attachment=True if filetype == "html" else False,
                download_name=f"{name}_map.html",
            )

        if filetype == "png":
            generate_map(
                activity_manager.map_settings,
                activities_to_map,
                filename,
                tiles_name="google_hybrid",
            )

            png = save_png(filename)
            return send_file(
                png,
                mimetype="image/png",
                as_attachment=True,
                download_name=f"{name}_map.png",
            )
    finally:
        if filetype == "png" and os.path.exists(png):
            os.remove(png)
        if os.path.exists(filename):
            os.remove(filename)


@download_bp.route("/download_elevation_profile", methods=["GET"])
def download_elevation_profile():
    session_id = session["session_id"]
    activity_manager = ActivityManager.load_from_redis(session_id)

    activity_id = request.args.get("activity_ids")
    if activity_id:
        activity_data = activity_manager.get_activities_df([activity_id]).squeeze()
        fig = create_elevation_profile(
            activity_data["map_distance"],
            activity_data["map_elevation"],
            background_color="whitesmoke",
            top_highlight=True,
        )
        png = f"tmp/{activity_data['name']}_elevation_profile.png"
        fig.savefig(png, dpi=150)

        try:
            return send_file(
                png,
                mimetype="image/png",
                as_attachment=True,
                download_name=f"{activity_data['name']}_elevation_profile.png",
            )
        finally:
            if os.path.exists(png):
                os.remove(png)
