"""
Flask extensions
"""
from flask_socketio import SocketIO

socketio = SocketIO(max_http_buffer_size=10000000)
