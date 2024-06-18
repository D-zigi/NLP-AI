"""
SocketIO
events handler

commented 'get_response' functions
because they are for test only
"""
import markdown
from .extensions import socketio
from .geminiAPI.chat import create_chat#, get_response

# chat events
CHAT = None
@socketio.on('start_chat', namespace='/chat')
def start_chat():
    """
    creates new chat
    """
    global CHAT
    CHAT = create_chat()


@socketio.on('message', namespace='/chat')
def message(data):
    """
    receives message from client,
    sends request to geminiAPI, processed
    and returned request with response
    """
    #response = get_response(CHAT, data['text'], data.get('image', None))
    response = "200 OK"

    socketio.emit('message', markdown.markdown(response), namespace='/chat') #converted to html element/s response