"""
creates the app
"""
import os
from dotenv import load_dotenv
from flask import Flask

from .events import socketio
from .routes import main


def create_app():
    """
    creates the app
    """
    app = Flask(__name__)
    app.config['DEBUG'] = True

    load_dotenv()
    app.config['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
    app.config['FIREBASE_CREDENTIALS'] = os.getenv('FIREBASE_CREDENTIALS')
    app.config['TMP_PATH'] = os.getenv('TMP_PATH')

    app.register_blueprint(main)
    socketio.init_app(app)

    return app
