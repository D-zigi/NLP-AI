"""
SocketIO
events handler

commented 'get_response' functions
because they are for test only
"""
from .extensions import socketio
from .geminiAPI.chat import create_chat, get_response
from .formater import html_format

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
    #converted to html request(client)
    socketio.emit('client-message', html_format(data['text']), namespace='/chat')

    # server is responding to clients' request
    socketio.emit('server-typing', namespace='/chat')

    # request to geminiAPI
    response = get_response(CHAT, data['text'], data.get('image', None))

    #converted to html response(server)
    socketio.emit('server-message', html_format(response), namespace='/chat')
