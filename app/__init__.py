"""
creates the app
"""
from flask import Flask

from .events import socketio
from .routes import main


def create_app():
    """
    creates the app
    """
    app = Flask(__name__)
    app.config['DEBUG'] = True

    app.register_blueprint(main)
    socketio.init_app(app)

    return app, socketio
