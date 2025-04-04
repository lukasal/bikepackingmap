# main.py
from app import create_app
from app.utils.session import ensure_session_id

app = create_app()


# @app.before_request
# def before_request():
#     ensure_session_id()


if __name__ == '__main__':
    app.run(port=5000, host='0.0.0.0', debug=True)
