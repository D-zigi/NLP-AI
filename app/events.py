"""
SocketIO
events handler

handle_join/handle_leave room events 
weren't implemented because of lack of usage
(single user per room is expected)
"""
# import json
import pickle
from flask import request
from flask_socketio import join_room, leave_room, emit #, send

from .extensions import socketio
from .geminiAPI.chat import create_chat, change_model, get_response, get_chat_name
from .formater import html_format


def get_client_ip():
    """
    returns client ip
    """
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return client_ip

# chat events
rooms_data = {} # keys for each room: "chat" - ChatSession

@socketio.on('connect', namespace='/chat')
def connect():
    """
    creates new room if not exist
    joins room with user
    """
    client_ip = get_client_ip()

    if client_ip not in rooms_data:
        rooms_data[client_ip] = {}
    join_room(client_ip)

    print(f'User connected: {client_ip}')

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    """
    removes user from room
    """
    client_ip = get_client_ip()
    leave_room(client_ip)

    print(f'User disconnected: {client_ip}')


@socketio.on('html_cache', namespace='/chat')
def html_cache(html_data):
    """
    caches html data for user
    """
    client_ip = get_client_ip()
    rooms_data[client_ip]["html_data"] = html_data


@socketio.on('start_chat', namespace='/chat')
def start_chat(data):
    """
    creates new chat
    """
    client_ip = get_client_ip()
    model_name = data['model_name']

    if "html_data" in rooms_data[client_ip]:
        chat = rooms_data[client_ip]["chat"]
        html_data = rooms_data[client_ip]["html_data"]
        emit(
            'load-chat',
            html_data,
            namespace='/chat',
            room=client_ip
        )
    else:
        chat = create_chat(model_name)
        rooms_data[client_ip]["chat"] = chat

@socketio.on('load_chat', namespace='/chat')
def load_chat(chat_data):
    """
    loads chat from chat json file:
    contains "history" - chat history and "model" - model name
    """
    client_ip = get_client_ip()

    chat_data = pickle.loads(chat_data)

    html_data = chat_data['html_data']
    model_name = chat_data['model_name']
    history = chat_data['history']

    chat = create_chat(model_name, history)
    rooms_data[client_ip]["chat"] = chat
    rooms_data[client_ip]["html_data"] = html_data

    emit('load-chat', html_data, namespace='/chat', room=client_ip)

@socketio.on('download_chat', namespace='/chat')
def download_chat(html_data):
    """
    returns json data required for downloading chat
    
    "chat": {
        "model_name": model name,
        "history": chat history
    }

    """
    client_ip = get_client_ip()
    chat = rooms_data[client_ip]["chat"]

    model_name = chat.model.model_name.replace('models/', '')
    history = chat.history

    chat_data = {
        "html_data": html_data,
        "model_name": model_name,
        "history": history
    }

    chat_dumped = pickle.dumps(chat_data)
    chat_name = get_chat_name(chat)

    return chat_dumped, chat_name

@socketio.on('change_chat_model', namespace='/chat')
def change_chat_model(data):
    """
    changes model
    """
    client_ip = get_client_ip()
    model_name = data['model_name']

    chat = rooms_data[client_ip]["chat"]
    chat = change_model(chat, model_name)
    rooms_data[client_ip]["chat"] = chat

@socketio.on('clear_chat', namespace='/chat')
def clear_chat():
    """
    clears chat history and cached html data
    """
    client_ip = get_client_ip()
    chat = rooms_data[client_ip]["chat"]
    chat.history = []

    if "html_data" in rooms_data[client_ip]:
        del rooms_data[client_ip]["html_data"]


@socketio.on('message', namespace='/chat')
def message(data):
    """
    receives message from client,
    sends request to geminiAPI, processed
    and returned request with response
    """
    client_ip = get_client_ip()
    chat = rooms_data[client_ip]["chat"]
    count = len(chat.history) // 2 + 1

    html_message = html_format(data['text']) #converted to html client message

    # for fully cleaned messages by formatter.
    # for malware or unaccepted input.
    if html_message.strip():
        # send client's message to client
        emit(
            'client-message',
            {'message': html_message, 'count': count},
            namespace='/chat',
            room=client_ip
        )

        # server is responding to clients' request
        emit('server-typing', namespace='/chat', room=client_ip)

        response = get_response(
                chat,
                data['text'],
                data.get('image', None)
            ) # request to geminiAPI

        if isinstance(response, str):
            html_response = html_format(response) #converted to html response(server)
            # send response to client
            emit(
                'server-message',
                html_response,# {'message': html_message, 'count': count}
                namespace='/chat',
                room=client_ip
            )

            emit('html-cache', namespace='/chat', room=client_ip)

        else:
            emit('error', response[0], namespace='/chat', room=client_ip)
            rooms_data[client_ip]["chat"] = response[1]
