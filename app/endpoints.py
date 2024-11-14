from flask import Flask, session, request, redirect, url_for, render_template, send_file, jsonify
import requests
import os 
import pandas as pd
from app.map_activities import map_activities
import matplotlib
from app.elevation_profile import create_elevation_profile
from app.save_png import save_png
matplotlib.use('Agg')  # Use a non-GUI backend for rendering
from app.activity_manager import ActivityManager
from app.strava.get_data import get_data
from datetime import datetime, timedelta
from app.redis_client import redis_client
import time
#app = Flask(__name__)

# In-memory store for user-specific activity managers
user_activity_managers = {}

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:5000/redirect'  # Your redirect URI

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
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=1)

    app.secret_key = os.urandom(24)  # Secret key for signing session cookies

    @app.before_request
    def ensure_session_id():
        """
        Ensure each user has a unique session ID stored as a cookie.
        This is run before every request.
        """
        SESSION_EXPIRATION = int(os.getenv("SESSION_EXP_TIME", 1800))
        if 'session_id' in session:
            print("before request")

            print(redis_client.exists(f"session:{session['session_id']}"))
            print('session_id' in session)
            print(redis_client.ttl(f"session:{session['session_id']}"))
        #session expired, then the redis client has deleted the content
        if 'session_id' in session and redis_client.exists(f"session:{session['session_id']}")!=1:
            session.clear()
            # Check if the request is AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'session_expired': True}), 401  # Send a JSON response indicating session expired
            else:
                return redirect(url_for('session_expired'))  # For regular requests, perform a redirect
        #new session
        if 'session_id' not in session:
            # Generate a new session ID if one doesn't exist
            session['session_id'] = os.urandom(16).hex()
            ActivityManager(session['session_id'])
        #session ok
        else:            
            redis_client.expire(f"session:{session['session_id']}", SESSION_EXPIRATION)

    @app.route('/')
    def home():
        return render_template('landing.html')  # Render the landing page

    @app.route('/strava_auth')
    def strava_auth():
        return redirect(STRAVA_AUTH_URL)
    
    @app.route('/session-expired')
    def session_expired():
        # Render the expiration page when the session has expired
        return render_template('expired.html')

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
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_at = token_data.get('expires_at')
            session['access_token'] = access_token
            return redirect(url_for("display_strava"))
        except Exception as e:
            return f"An error occurred: {str(e)}", 500

    @app.route('/display_strava')
    def display_strava():  
        return render_template('strava_activities.html')
    
    @app.route('/fetch_strava')
    def fetch_strava():  
  
        # Get the current user's ActivityManager
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       
         # Extract parameters
        start_date = request.args.get('start_date')
        # Convert string dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        
        end_date = request.args.get('end_date')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        per_page = int(request.args.get('per_page', 10))
        
        # Create a sample DataFrame with name and start_date
        data = get_data(session['access_token'], start_date, end_date, per_page=per_page, page=1)
            # normalize data
        data = pd.json_normalize(data)
        # Add activities to the DataFrame
        activity_manager.add_activities(data)

        df = activity_manager.get_activities()
        filtered_df = df[(df['start_date'] >= start_date.strftime('%Y-%m-%d')) & (df['start_date'] <= end_date.strftime('%Y-%m-%d'))]
   
        # Prepare data to send to the frontend
        data_to_send = filtered_df[["start_date", "name", "id"]].to_dict(orient='records')

        return jsonify({'data': data_to_send})
            # Render a template with the authorization code, tokens, and the DataFrame
            # return render_template('redirect.html', 
            #                     df=df)  # Pass the DataFrame to the template

    @app.route('/select_activities', methods=['POST'])
    def select_activities():
        selected_activities = request.form.getlist('selected_activities')


        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       
        selected_activities = [int(index) for index in selected_activities]

        selected_activities = activity_manager.select_activities(selected_activities)
        activity_manager.preprocess_selected()
        
        # Render the submitted activities in a new template
        return render_template('submitted.html', activities=activity_manager.preprocessed[["name", "id"]])  # Pass the selected activities to the new template
    

    @app.route('/map', methods=['GET'])
    def map_view():
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       
        # Get activity ID(s) from query parameters
        activity_ids = request.args.get('activity_ids')
        if not activity_ids:
            return "No activities selected.", 400  # Handle case where no activities are selected
        elif activity_ids == "all":
            activities_to_map = activity_manager.preprocessed
        else :
            activity_ids = [int(id) for id in activity_ids.split(',')]
            activities_to_map = activity_manager.preprocessed[activity_manager.preprocessed['id'].isin(activity_ids)]


        # Call your complex function to generate the map HTML
        map_activities(activities_to_map,
                    out_file = './templates/tmp/mymap_terrain.html', 
                    tiles_name = 'stadia_terrain',
                    final_popup = False,
                    dynamic_tiles = True,
                    zoom_margin = 0.05)  # Assuming this function creates 'map_output.html'
        return render_template('tmp/mymap_terrain.html') # Serve the generated map HTML

    @app.route('/download_map', methods=['GET'])
    def download_map():
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       
        
        activity_id = request.args.get('activity_ids')
        activity_id = int(activity_id) if activity_id else None
        if activity_id:
            # Filter the DataFrame based on the activity_id
            activity_data = activity_manager.preprocessed[activity_manager.preprocessed['id'] == activity_id]
            # figure
            # Gen   erate map for the selected activity
            filename = f"plots/{activity_data['name'].squeeze()}_map.html"
            map_activities(activity_data, filename, tiles_name = 'google_hybrid')
            png = save_png(filename)
            
            try:
            # Return the image as a downloadable file
                return send_file(png, mimetype='image/png', as_attachment=True, download_name=f"{activity_data['name'].squeeze()}_map.png")
            finally:
                # After the file is sent, delete it
                if os.path.exists(png):
                    os.remove(png)

    @app.route('/download_elevation_profile', methods=['GET'])
    def download_elevation_profile():
        session_id = session['session_id']
        activity_manager = ActivityManager.load_from_redis(session_id)       
        
        activity_id = request.args.get('activity_ids')
        activity_id = int(activity_id) if activity_id else None
        if activity_id:
            # Filter the DataFrame based on the activity_id
            activity_data = activity_manager.preprocessed[activity_manager.preprocessed['id'] == activity_id].squeeze()
            # figure
            fig = create_elevation_profile(activity_data, background_color = 'whitesmoke')
            png = f"plots/{activity_data['name']}_elevation_profile.png"
            fig.savefig(png, dpi=150)

            try:
                # Return the image as a downloadable file
                return send_file(png, mimetype='image/png', as_attachment=True, download_name=f"{activity_data['name']}_elevation_profile.png")
            finally:
                # After the file is sent, delete it
                if os.path.exists(png):
                    os.remove(png)

    return app