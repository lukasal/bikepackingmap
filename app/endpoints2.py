from flask import Flask, session, request, redirect, url_for, render_template, send_file
import requests
import os 
import pandas as pd
from app.map_activities import map_activities
import matplotlib
from app.elevation_profile import create_elevation_profile
from app.save_png import save_png
matplotlib.use('Agg')  # Use a non-GUI backend for rendering
from app.activity_manager import ActivityManager
from app.strava import get_data
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler



app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for signing session cookies

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
# Define session expiration time (e.g., 30 minutes)
SESSION_EXPIRATION_TIME = timedelta(minutes=30)

def cleanup_inactive_sessions():
    """Cleanup expired sessions based on inactivity"""
    
    for session_id in list(user_activity_managers.keys()):

        # Check if the session has been inactive for more than 30 minutes
        if datetime.utcnow() - user_activity_managers[session_id].last_activity > SESSION_EXPIRATION_TIME:
            del user_activity_managers[session_id]  # Remove the expired session

# Background scheduler to clean up inactive sessions
scheduler = BackgroundScheduler()
# Schedule the cleanup task to run every 5 minutes
scheduler.add_job(func=cleanup_inactive_sessions, trigger="interval", minutes=10)
scheduler.start()

@app.before_request
def ensure_session_id():
    """
    Ensure each user has a unique session ID stored as a cookie.
    This is run before every request.
    """
    if 'session_id' not in session:
        # Generate a new session ID if one doesn't exist
        session['session_id'] = os.urandom(16).hex()
    
    # Initialize a new ActivityManager for the user if not already present
    session_id = session['session_id']
    if session_id not in user_activity_managers:
        user_activity_managers[session_id] = ActivityManager(session_id)
    user_activity_managers[session_id].set_last_activity() # If session does not have 'last_activity', initialize it
    
@app.route('/')
def home():
    return render_template('landing.html')  # Render the landing page

@app.route('/strava_auth')
def strava_auth():
    return redirect(STRAVA_AUTH_URL)

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
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    
@app.route('/fetch')
def get_data(before, after, per_page, page):  

        
        # Get the current user's ActivityManager
        session_id = session['session_id']
        activity_manager = user_activity_managers.get(session_id)       
        
        # Create a sample DataFrame with name and start_date
        data = get_data(session['access_token'], be per_page=60, page=1)
            # normalize data
        data = pd.json_normalize(data)
        # Add activities to the DataFrame
        activity_manager.add_activities(data)
        df = activity_manager.get_activities()

        # Render a template with the authorization code, tokens, and the DataFrame
        return render_template('redirect.html', 
                               code=authorization_code,
                               access_token=access_token,
                               refresh_token=refresh_token,
                               expires_at=expires_at,
                               df=df)  # Pass the DataFrame to the template




@app.route('/select_activities', methods=['POST'])
def select_activities():
    selected_activities = request.form.getlist('selected_activities')  # Get selected activities
    if not selected_activities:
        return "No activities selected.", 400  # Handle case where no activities are selected
    session_id = session['session_id']
    activity_manager = user_activity_managers.get(session_id)
    selected_activities = [int(index) for index in selected_activities]

    selected_activities = activity_manager.select_activities(selected_activities)
    activity_manager.preprocess_selected()
    
    # Render the submitted activities in a new template
    return render_template('submitted.html', activities=activity_manager.preprocessed)  # Pass the selected activities to the new template

@app.route('/activities')
def activities():
    activities_df = ActivityManager.get_activities()  # Get all activities from the manager
    return render_template('activities.html', activities=activities_df.to_dict(orient='records'))  # Render activities in a new template

@app.route('/map', methods=['GET'])
def map_view():
    session_id = session['session_id']
    activity_manager = user_activity_managers.get(session_id)
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
    activity_manager = user_activity_managers.get(session_id)
    
    activity_id = request.args.get('activity_ids')
    activity_id = int(activity_id) if activity_id else None
    if activity_id:
        # Filter the DataFrame based on the activity_id
        activity_data = activity_manager.preprocessed[activity_manager.preprocessed['id'] == activity_id]
        # figure
        # Gen   erate map for the selected activity
        filename = f'plots/{activity_data['name'].squeeze()}_map.html'
        map_activities(activity_data, filename, tiles_name = 'google_hybrid')
        png = save_png(filename)
        # Return the image as a downloadable file
        return send_file(png, mimetype='image/png', as_attachment=True, download_name=f'{activity_data['name'].squeeze()}_map.png')


@app.route('/download_elevation_profile', methods=['GET'])
def download_elevation_profile():
    session_id = session['session_id']
    activity_manager = user_activity_managers.get(session_id)
    
    activity_id = request.args.get('activity_ids')
    activity_id = int(activity_id) if activity_id else None
    if activity_id:
        # Filter the DataFrame based on the activity_id
        activity_data = activity_manager.preprocessed[activity_manager.preprocessed['id'] == activity_id].squeeze()
        # figure
        fig = create_elevation_profile(activity_data, background_color = 'whitesmoke')
        png = f'plots/{activity_data['name']}_elevation_profile.png'
        fig.savefig(png, dpi=150)

        # Return the image as a downloadable file
        return send_file(png, mimetype='image/png', as_attachment=True, download_name=f'{activity_data['name']}_elevation_profile.png')


