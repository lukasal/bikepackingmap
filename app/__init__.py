from flask import Flask, g, request
import os
import logging
import time
from app.utils.config import Config
from app.utils.error_handlers import error_bp
from app.utils.redis_client import redis_client
from app.utils.session import ensure_session_id
from app.routes.download import download_bp
from app.routes.examples import examples_bp
from app.routes.gpx import gpx_bp
from app.routes.home import home_bp
from app.routes.map import map_bp
from app.routes.send_email import email_bp
from app.routes.strava import strava_bp
from app.routes.templates import templates_bp
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    # Create the Flask app and set the root path to the project root
    app = Flask(__name__, root_path=project_root)
    app.config.from_object(Config)
    app.config["SESSION_REDIS"] = redis_client
    CORS(app, resources={r"/*": {"origins": "https://www.bikepackingmap.com"}})

    # Add a before_request function to ensure session ID
    @app.before_request
    def before_request():
        g.start_time = time.time()
        logger.info(f"Request: {request.method} {request.url}")
        return ensure_session_id()

    @app.after_request
    def log_response_info(response):
        duration = time.time() - g.start_time
        logger.info(f"Response status: {response.status}")
        logger.info(f"Request duration: {duration:.4f} seconds")
        return response

    # Register error handlers
    app.register_blueprint(error_bp)

    app.register_blueprint(download_bp)
    app.register_blueprint(examples_bp)
    app.register_blueprint(gpx_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(map_bp)
    app.register_blueprint(email_bp)
    app.register_blueprint(strava_bp)
    app.register_blueprint(templates_bp)

    return app
