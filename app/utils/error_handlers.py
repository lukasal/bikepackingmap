# error_handlers.py
from flask import session, Blueprint, jsonify, request, render_template
import logging
import traceback 
from app.activity_manager.activity_manager import ActivityManager
from app.utils.upload_blob import upload_to_blob
import pickle
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

error_bp = Blueprint("error_bp", __name__)


@error_bp.app_errorhandler(404)
def not_found_error(error):
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        response = jsonify({"error": "Resource not found"})
        response.status_code = 404
        return response
    else:
        return render_template("home/page-404.html"), 404


@error_bp.app_errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        response = jsonify({"error": "Internal server error"})
        response.status_code = 500
        return response
    else:
        return render_template("home/page-505.html"), 500


@error_bp.app_errorhandler(Exception)
def unhandled_exception(error):
    # Capture the stack trace
    tb = traceback.format_exc()
    # Extract the routine name from the stack trace
    endpoint = request.endpoint

    logger.error(
        f"Unhandler exception in Endpoint: {endpoint}, with session_id: {session['session_id']}, Error: {error}, stack trace: {tb}"
    )
    try:
        activity_manager = ActivityManager.load_from_cache(session["session_id"])
        # Dump the activity manager to a blob store
        error_info = {
            "activity_manager": activity_manager,
            "error_type": type(Exception).__name__,
            "error_message": str(Exception),
            "traceback": traceback.format_exc(),
            "timestamp": datetime.utcnow().isoformat(),

            "request_info": {
                "endpoint": request.endpoint,
                "path": request.path,
                "method": request.method,
                "args": request.args.to_dict(),
                "form": request.form.to_dict(),
                "json": request.get_json(silent=True),
                "headers": dict(request.headers),
                "remote_addr": request.remote_addr
            },

            "user_info": {
                "sesssion_id": session['session_id'],
            }
        }
        logger.error(
        f"Unhandler exception: {error_info}"
    )
        blob_data = pickle.dumps(
            error_info
        )
        current_timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        blob_store_key = (
            f"activity_manager_dumps/{current_timestamp}_{session['session_id']}.pkl"
        )
        upload_to_blob(
            blob_data,
            "error-data",
            blob_store_key,
        )  # Use the upload_to_blobactivity_manager.dump_to_blob_store(blob_store_key, blob_data)
        logger.info(f"Activity manager dumped to blob store with key: {blob_store_key}")
    except Exception as e:
        logger.error(f"Failed to log activity manager: {e}")

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        response = jsonify({"error": str(error)})
        response.status_code = 500
        return response
    else:
        return render_template("home/page-500.html"), 500


@error_bp.route("/error-route", methods=["GET"])
def error_route():
    """
    Example route to trigger an error for testing purposes.
    """
    raise Exception("This is a test exception")
    return render_template("home/page-500.html"), 500
