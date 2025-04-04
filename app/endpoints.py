from flask import (
    Flask,
    session,
    request,
    redirect,
    url_for,
    render_template,
    send_file,
    jsonify,
    send_from_directory,
)
import requests
import os 
import pandas as pd
import matplotlib
from jinja2 import TemplateNotFound
from email.mime.text import MIMEText
import smtplib

from app.elevation_profile import create_elevation_profile
from app.save_png import save_png
matplotlib.use('Agg')  # Use a non-GUI backend for rendering
from app.activity_manager.activity_manager import ActivityManager
from app.strava.get_data import get_data
from datetime import datetime, timedelta
from app.utils.redis_client import redis_client
from app.helper import parse_date
from app.map.generate_map import generate_map
from app.map.MapSettings import MapSettings
from app.gpx.process_gpx import process_gpx_data
from app.strava.process_strava import process_strava
import time
import redis
import json
import pickle

# app = Flask(__name__)

# In-memory store for user-specific activity managers
user_activity_managers = {}

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

website_host = os.getenv("WEBSITE_HOSTNAME")
if website_host:
    REDIRECT_URI = f"https://{website_host}/redirect"
else:
    REDIRECT_URI = "http://localhost:5000/redirect"

print(REDIRECT_URI)
STRAVA_AUTH_URL = (
    f"https://www.strava.com/oauth/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&response_type=code"
    f"&scope=read,activity:read"
)
def create_app():
    # Get the absolute path of your project root directory
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Create the Flask app and set the root path to the project root
    app = Flask(__name__, root_path=project_root)
    # app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = True
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_REDIS"] = redis_client

    app.secret_key = os.getenv("SECRET_KEY")

    @app.before_request
    @app.route("/")
    def home():
        return render_template("home/index.html")  # Render the landing page

    @app.route("/sitemap.xml")
    def serve_sitemap():
        return send_from_directory(app.static_folder, "sitemap.xml")

    @app.route('/strava_auth')
    def strava_auth():
        return redirect(STRAVA_AUTH_URL)

    @app.route('/session-expired')
    def session_expired():
        # Render the expiration page when the session has expired
        return render_template("home/expired.html")

    @app.route('/redirect')
    def strava_redirect():
        # Get the authorization code from the query parameters
        authorization_code = request.args.get('code')

        if not authorization_code:
            return "Authorization failed: No authorization code provided!", 400

        try:
            # Exchange the authorization code for an access token
            token_response = requests.post(
                'https://www.strava.com/oauth/token',
                data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'code': authorization_code,
                    'grant_type': 'authorization_code'
                }
            )

            # Check if the request was successful
            if token_response.status_code != 200:
                return f"Error: Unable to retrieve access token. Response: {token_response.text}", 500

            # Extract access token and other details from the response
            token_data = token_response.json()
            # Store the access token in session
            access_token = token_data.get("access_token")
            session['access_token'] = access_token
            return redirect(url_for("display_strava"))
        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    @app.route('/display_strava')
    def display_strava():  
        return render_template(
            "home/select_activities.html",
            fetch_url="/fetch_strava",
            show_calendar=True,
            show_upload_button=False,
        )

    @app.route("/display_gpx")
    def display_gpx():
        return render_template(
            "home/select_activities.html",
            fetch_url="/fetch_gpx",
            show_calendar=False,
            show_upload_button=True,
        )

    @app.route("/display_examples")
    def display_examples():
        return render_template(
            "home/select_activities.html",
            fetch_url="/fetch_examples",
            show_calendar=False,
            show_upload_button=False,
        )

    @app.route("/fetch_gpx", methods=["POST"])
    def fetch_gpx():
        print("fetch_gpx")
        # Get the current user's ActivityManager
        session_id = session["session_id"]
        activity_manager = ActivityManager.load_from_redis(session_id)
        activity_manager.reset()
        files = request.files.getlist("gpx_files")

        activities = []
        for file in files:
            activities.append(process_gpx_data(file))

        # Sort the list of activities by start_date or name as fallback
        sorted_activities = sorted(
            activities,
            key=lambda activity: (
                (
                    activity.start_date
                    if activity.start_date is not None
                    else datetime.max
                ),
                activity.name,
            ),
        )
        activity_manager.add_activities(sorted_activities)
        # process and GPX files here to the activity manager

        return jsonify({"data": activity_manager.send_to_frontend()})

    @app.route("/fetch_strava", methods=["POST"])
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

    @app.route("/fetch_examples", methods=["POST"])
    def fetch_examples():

        session_id = session["session_id"]
        start = time.time()

        activity_manager = ActivityManager.load_from_redis(session_id)
        print("fetch_examples", time.time() - start)
        # Load the example dataset
        with open("data/giro_italia_example.pkl", "rb") as file:
            example_processed = pickle.load(file)
        print("load data", time.time() - start)
        # Add activities to the DataFrame
        activity_manager.add_activities(example_processed)
        print("preprocess activities", time.time() - start)

        return jsonify({"data": activity_manager.send_to_frontend()})

    @app.route("/select", methods=["POST"])
    def select():
        selected_activities = request.form.getlist("selected_activities")

        session_id = session["session_id"]
        activity_manager = ActivityManager.load_from_redis(session_id)
        # selected_activities = [int(index) for index in selected_activities]

        activity_manager.postprocess(selected_activities)
        activity_manager.set_map_ids(selected_activities)
        # Render the submitted activities in a new template
        return redirect(url_for("build_map"))

    @app.route("/downloads_overview", methods=["GET"])
    def downloads_overview():
        session_id = session["session_id"]
        activity_manager = ActivityManager.load_from_redis(session_id)
        return render_template(
            "home/export.html",
            activities=activity_manager.get_activities_df(activity_manager.map_ids),
        )  # Pass the selected activities to the new template

    @app.route("/get_map", methods=["GET"])
    def get_map():

        filetype = request.args.get("filetype")
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       

        activity_ids = request.args.get("activity_ids")
        if not activity_ids:
            return (
                "No activities selected.",
                400,
            )  # Handle case where no activities are selected
        elif activity_ids == "all":
            activities_to_map = activity_manager.get_activities_df(
                activity_manager.map_ids
            )
            name = "full"
        else:
            activity_ids = [id for id in activity_ids.split(",")]
            activities_to_map = activity_manager.get_activities_df(activity_ids)
            name = "_".join(activities_to_map["name"].tolist())

        # Generate map for the selected activity
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
                )  # Assuming this function creates 'map_output.html'
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
                # Return the image as a downloadable file
                return send_file(
                    png,
                    mimetype="image/png",
                    as_attachment=True,
                    download_name=f"{name}_map.png",
                )
        finally:
            # After the file is sent, delete it
            if filetype == "png" and os.path.exists(png):
                os.remove(png)
            if os.path.exists(filename):
                os.remove(filename)

    @app.route('/download_elevation_profile', methods=['GET'])
    def download_elevation_profile():
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       

        activity_id = request.args.get("activity_ids")
        if activity_id:
            # Filter the DataFrame based on the activity_id
            activity_data = activity_manager.get_activities_df([activity_id]).squeeze()
            # figure
            fig = create_elevation_profile(
                activity_data["map_distance"],
                activity_data["map_elevation"],
                background_color="whitesmoke",
                top_highlight=True,
            )
            png = f"tmp/{activity_data['name']}_elevation_profile.png"
            fig.savefig(png, dpi=150)

            try:
                # Return the image as a downloadable file
                return send_file(png, mimetype='image/png', as_attachment=True, download_name=f"{activity_data['name']}_elevation_profile.png")
            finally:
                # After the file is sent, delete it
                if os.path.exists(png):
                    os.remove(png)

    @app.route("/build_map")
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
        )  # Assuming this function creates 'map_output.html'
        return render_template(
            "home/build_map.html",
            map=m._repr_html_(),
            settings=activity_manager.map_settings,
        )

    @app.route("/update_map", methods=["POST"])
    def update_map():

        # Get updated colors from the form
        session_id = session["session_id"]
        activity_manager = ActivityManager.load_from_redis(session_id)
        settings_data = request.get_json()  # Read the JSON data from the request
        print(settings_data)
        for name, value in settings_data.items():
            try:
                activity_manager.map_settings.set_interactive_setting(name, value)
            except KeyError as e:
                return jsonify({"error": str(e)}), 400

        activity_manager.save()

        # Create a map with updated styles
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

    @app.route("/static/<template>")
    def route_template(template):

        try:

            if not template.endswith(".html"):
                template += ".html"

            # Detect the current page
            segment = get_segment(request)

            # Serve the file (if exists) from app/templates/home/FILE.html
            return render_template("home/" + template, segment=segment)

        except TemplateNotFound:
            return render_template("home/page-404.html"), 404

        except:
            return render_template("home/page-500.html"), 500

    @app.route("/send-email", methods=["POST"])
    def send_email():
        full_name = request.form["full_name"]
        email = request.form["email"]
        message = request.form["message"]

        # Email content
        msg = MIMEText(f"Name: {full_name}\nEmail: {email}\nMessage: {message}")
        msg["Subject"] = "Contact Form Submission"
        msg["From"] = os.getenv("EMAIL")
        msg["To"] = os.getenv("EMAIL_TARGET")

        # Send email
        try:
            with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
                server.starttls()
                server.login(os.getenv("EMAIL"), os.getenv("EMAIL_PW"))
                server.sendmail(
                    os.getenv("EMAIL"), os.getenv("EMAIL_TARGET"), msg.as_string()
                )
            return jsonify({"message": "Contact form successfully submitted!"})
        except smtplib.SMTPException as e:
            return jsonify({"message": f"Failed to send email: {e}"}), 500

    # Helper - Extract current page name from request
    def get_segment(request):

        try:

            segment = request.path.split("/")[-1]

            if segment == "":
                segment = "index"

            return segment

        except:
            return None

    return app
