"""
runs the app
"""
import os
from dotenv import load_dotenv

def load_environ():
    """
    loads environment variables
    """
    load_dotenv()
    os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
    os.environ['FIREBASE_CREDENTIALS'] = os.getenv('FIREBASE_CREDENTIALS')
    os.environ['TMP_PATH'] = os.getenv('TMP_PATH')

if __name__ == '__main__':
    load_environ()

    from app import create_app
    app, socketio = create_app()
    socketio.run(app)
