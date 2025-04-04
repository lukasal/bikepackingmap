from flask import Blueprint, render_template, send_from_directory

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():
    return render_template("home/index.html")


@home_bp.route("/sitemap.xml")
def serve_sitemap():
    return send_from_directory("static", "sitemap.xml")


@home_bp.route("/session-expired")
def session_expired():
    return render_template("home/expired.html")
