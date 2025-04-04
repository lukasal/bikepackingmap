from flask import (
    Blueprint,
    request,
    jsonify,
)
from email.mime.text import MIMEText
import smtplib
import os

email_bp = Blueprint("email", __name__)


@email_bp.route("/send-email", methods=["POST"])
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
