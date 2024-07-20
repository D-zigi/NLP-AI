"""
SocketIO
events handler

handle_join/handle_leave room events 
weren't implemented because of lack of usage
(single user per room is expected)
"""
import os
import pickle
import concurrent.futures
import requests
from flask import request
from bs4 import BeautifulSoup
from flask_socketio import join_room, leave_room, emit#, send

from .extensions import socketio

from .gemini_api.chat import (
    create_chat,
    create_webuilder,
    change_model,
    get_response,
    get_chat_name
)

from .formater import html_format

from .firebase import AppRoom


def await_function(func, on_complete):
    """
    runs func function and then runs on_complete function
    """
    executor = concurrent.futures.ThreadPoolExecutor()
    future = executor.submit(func)

    future.add_done_callback(on_complete)

def get_client_ip():
    """
    returns client ip
    """
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return client_ip

def get_app_name():
    """
    returns app name
    """
    app_name = request.args.get('appName')
    return app_name


def remove_html_duplicates(html_data):
    """
    removes html duplicates with same ids
    """
    soup = BeautifulSoup(html_data, 'html.parser')
    non_duplicates = []
    seen = []

    for element in soup:
        element_id = element.get('id')
        if element_id not in seen:
            seen.append(element_id)
            elements = soup.find_all(id=element_id)
            elements.sort(key=lambda x: len(str(x)), reverse=True)

            non_duplicates.append(str(elements[0]))

    return ''.join(non_duplicates)


def save_data(client_ip, app_name, data):
    """
    uploads .pkl data file
    """
    room = rooms.get_user_room(client_ip, app_name)
    data_path = room.data_path
    with open(data_path, 'wb') as file:
        pickle.dump(data, file)

def read_data(client_ip, app_name):
    """
    reads .pkl data file
    and removes it
    """
    room = rooms.get_user_room(client_ip, app_name)
    data_path = room.data_path
    with open(data_path, 'rb') as file:
        data = pickle.load(file)
    return data


def read_blob(blob_url):
    """
    reads blob data from url
    """
    response = requests.get(blob_url, timeout=10)
    return response.content


def save_html_data(client_ip, app_name, data=''):
    """
    saves html data to file
    """
    room = rooms.get_user_room(client_ip, app_name)
    html_data_path = room.html_data_path
    with open(html_data_path, encoding="utf-8", mode='w') as file:
        file.write(data)

def update_html_data(client_ip, app_name, data=''):
    """
    updates html data in file
    """
    room = rooms.get_user_room(client_ip, app_name)
    html_data_path = room.html_data_path


    # Step 1: Read the existing content
    with open(html_data_path, encoding="utf-8", mode='r') as file:
        old_data = file.read()

    # Step 2: Append the new data
    with open(html_data_path, encoding="utf-8", mode='a') as file:
        file.write(data)

    # Step 3: Read the updated content and process it to remove duplicates
    with open(html_data_path, encoding="utf-8", mode='r+') as file:
        file_content = file.read()
        new_data = remove_html_duplicates(file_content)

        # Move the file pointer to the beginning of the file
        file.seek(0)
        file.write(new_data)
        # Truncate the file to the length of new_data to remove any extra content
        file.truncate()

    modified = old_data != new_data

    return modified

def read_html_data(client_ip, app_name):
    """
    reads html data from file
    and removes it from TMP_PATH
    """
    room = rooms.get_user_room(client_ip, app_name)
    html_data_path = room.html_data_path
    with open(html_data_path, encoding="utf-8", mode='r') as file:
        html_data = file.read()
    return html_data


def join_data(client_ip, app_name):
    """
    extracts data related to client
    and joins it to .pkl file in TMP_PATH
    """
    room = rooms.get_user_room(client_ip, app_name)
    chat = room.chat

    html_data = read_html_data(client_ip, app_name)
    model_name = chat.model.model_name.replace('models/', '')
    history = chat.history

    data = {
        "html_data": html_data,
        "model_name": model_name,
        "history": history
    }

    save_data(client_ip, app_name, data)

def split_data(client_ip, app_name):
    """
    extracts client's data from .pkl file
    and removes it from TMP_PATH
    """
    data = read_data(client_ip, app_name)

    html_data = data['html_data']
    model_name = data['model_name']
    history = data['history']

    return html_data, model_name, history


# Start of geminiapi events
class UserRoom:
    """
    user room model
    """
    def __init__(self, ip, app_name):
        self.ip = ip
        self.app_name = app_name
        self.sessions = 1

        self.app_room = AppRoom(ip, app_name)

        self.data_path = self.app_room.local_data_path
        self.html_data_path = self.app_room.local_data_path.replace('.pkl','_html_data.html')
        self.uploaded_files = {}

        if app_name == 'chatbot':
            self.chat = create_chat()
        elif app_name == 'webuilder':
            self.chat = create_webuilder()

    def to_dict(self):
        """
        convert self object to dict
        """
        return {
            'data_path': self.data_path,
            'html_data_path': self.html_data_path,
            'uploaded_files': self.uploaded_files,
            'chat': self.chat
        }

    def exists(self):
        """
        checks if self object exists in firebase
        """
        exists_flag = self.app_room.exists()
        return exists_flag

    def save(self):
        """
        uploads self object to firebase
        """
        self.app_room.save()

    def delete(self):
        """
        deletes self object from firebase
        """
        self.app_room.delete()

    def download_data(self):
        """
        loads self object from firebase storage
        """
        self.app_room.download_data()

    def upload_data(self):
        """
        uploads self object to firebase storage
        """
        self.app_room.upload_data()

class Rooms:
    """
    rooms data model
    """
    def __init__(self):
        self.rooms = {
            'chatbot': {},
            'webuilder': {}
        }

    def add_user_room(self, client_ip, app_name):
        """
        adds user to room
        """
        if self.user_room_exists(client_ip, app_name):
            self.rooms[app_name][client_ip].sessions += 1
        else:
            self.rooms[app_name][client_ip] = UserRoom(client_ip, app_name)

        join_room(f"{app_name}-{client_ip}")
        print(f'User connected to {app_name}: {client_ip}')
        print(f"Sessions: {self.rooms[app_name][client_ip].sessions}")

    def get_user_room(self, client_ip, app_name):
        """
        returns user room
        """
        if self.user_room_exists(client_ip, app_name):
            return self.rooms[app_name][client_ip]
        return None

    def set_user_room(self, client_ip, app_name, user_room):
        """
        sets user room
        """
        self.rooms[app_name][client_ip] = user_room

    def user_room_exists(self, client_ip, app_name):
        """
        checks if user room exists
        """
        return client_ip in self.rooms[app_name]

    def clear_user_room(self, client_ip, app_name):
        """
        clears user room
        """
        user_room = UserRoom(client_ip, app_name)
        self.set_user_room(client_ip, app_name, user_room)

    def delete_user_room(self, client_ip, app_name):
        """
        deletes user room
        """
        user_room = self.get_user_room(client_ip, app_name)
        user_room.sessions -= 1
        user_room.save()
        self.set_user_room(client_ip, app_name, user_room)

        if user_room.sessions == 0:
            os.remove(user_room.data_path)
            os.remove(user_room.html_data_path)

            del self.rooms[app_name][client_ip]
            leave_room(f"{app_name}-{client_ip}")
            print(f'User disconnected from {app_name}: {client_ip}')

rooms = Rooms()

@socketio.on('connect', namespace='/geminiapi')
def connect():
    """
    creates new room if not exist
    room contains:
        'data_url' - .pkl file path
        'html_data_url' - .html data file path
        'uploaded_files' - uploaded files ({id: base64 string}),
        'chat' - ChatSession
    joins room with user
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    rooms.add_user_room(client_ip, app_name)


@socketio.on('load_chat', namespace='/geminiapi')
def load_chat(client_ip=None, app_name=None):
    """
    loads chat data from .pkl file
    contains:
        'history' - chat history, 
        'model' - model name,
        'html_data' - html data
    creates chat session with 'model' and 'history'
    creates html data file with 'html_data'
    sends command to load the chat
    """
    if not client_ip or not app_name: # if the function was called with emit
        client_ip = get_client_ip()
        app_name = get_app_name()

        # data = read_blob(data_url)
        # print(data_url)
        # print(data)
        # save_data(client_ip, app_name, data)

    html_data, model_name, history = split_data(client_ip, app_name)
    if app_name == 'chatbot':
        chat = create_chat(model_name, history)
    elif app_name == 'webuilder':
        chat = create_webuilder(model_name, history)

    room = rooms.get_user_room(client_ip, app_name)
    room.chat = chat
    rooms.set_user_room(client_ip, app_name, room)

    save_html_data(client_ip, app_name, html_data)

    socketio.emit(
        'change-model',
        model_name,
        namespace='/geminiapi',
        room=f"{app_name}-{client_ip}"
    )
    socketio.emit(
        'load-chat',
        room.html_data_path.replace('app', ''),
        namespace='/geminiapi',
        room=f"{app_name}-{client_ip}"
    )

    print("finished loading")

@socketio.on('download_chat', namespace='/geminiapi')
def download_chat():
    """
    downloads chat data from database
    """
    client_ip = get_client_ip()
    app_name = get_app_name()
    room = rooms.get_user_room(client_ip, app_name)

    chat = room.chat

    data_path = room.data_path.replace('app/', '')
    chat_name = get_chat_name(chat)

    return data_path, chat_name


@socketio.on('save_chat', namespace='/geminiapi')
def save_chat(client_ip=None, app_name=None):
    """
    saves chat data to local .pkl file
    contains:
        'history' - chat history, 
        'model' - model name,
        'html_data' - html data

    returns optional chat name for file naming
    """
    if not client_ip or not app_name: # if the function was called with emit
        client_ip = get_client_ip()
        app_name = get_app_name()

    join_data(client_ip, app_name)

    room = rooms.get_user_room(client_ip, app_name)
    room.upload_data()
    print("finished saving")

@socketio.on('update_chat', namespace='/geminiapi')
def update_chat(data):
    """
    updates chat history
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    if update_html_data(client_ip, app_name, data):
        save_chat(client_ip, app_name)


@socketio.on('start_chat', namespace='/geminiapi')
def start_chat(default_data=''):
    """
    loads existing chat if already exist
    creates new chat othewise
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)

    def load(_):
        print("loading data from local")
        load_chat(client_ip, app_name)

    def download(future):
        result = future.result()
        exists = result
        print(f"User exists: {exists}")
        if exists:
            print("downloading data from database")
            await_function(
                room.download_data,
                load
            )
        else:
            save_html_data(client_ip, app_name, default_data)
            save_chat(client_ip, app_name)

    await_function(
        room.exists,
        download,
    )

@socketio.on('clear_chat', namespace='/geminiapi')
def clear_chat(default_data = '', client_ip=None, app_name=None):
    """
    clears chat history and stored html data
    """
    if not client_ip or not app_name: # if the function was called with emit
        client_ip = get_client_ip()
        app_name = get_app_name()

    save_html_data(client_ip, app_name, default_data)
    room = rooms.get_user_room(client_ip, app_name)
    rooms.clear_user_room(client_ip, app_name)
    save_chat(client_ip)

    emit(
        'load-chat',
        room.html_data_path.replace('app', ''),
        namespace='/geminiapi',
        room=f"{app_name}-{client_ip}"
    )

@socketio.on('message', namespace='/geminiapi')
def message(data):
    """
    receives message from client,
    sends request to geminiAPI, processed
    and returned request with response
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)

    chat = room.chat
    count = len(chat.history) // 2 + 1

    text = data['text']

    files = room.uploaded_files # get uploaded files
    room.uploaded_files = {} # clear uploaded files
    rooms.set_user_room(client_ip, app_name, room)

    files = { # get only processed files
        key: value for key, value in files.items() if files[key]['state'] == 'finished'
    }

    images = [ # get all ready images
        files[file]['data'] for file in files if 'image' in files[file]['type']
    ]


    html_message = html_format(text) #converted to html client message

    # for fully cleaned messages by formatter.
    # for malware or unaccepted input.
    if html_message.strip():
        # send client's message to client
        emit(
            'client-message',
            {'message': html_message, 'index': count},
            namespace='/geminiapi',
            room=f"{app_name}-{client_ip}"
        )

        # server is responding to clients' request
        emit('server-responding', namespace='/geminiapi', room=f"{app_name}-{client_ip}")

        response = get_response(
                chat,
                text,
                images
            ) # sends request to geminiAPI

        if isinstance(response, str):
            html_response = html_format(response) #converted to html response(server)
            # send response to client
            emit(
                'server-message',
                {'response': html_response, 'index': count},
                namespace='/geminiapi',
                room=f"{app_name}-{client_ip}"
            )

        else:
            emit('error', response[0], namespace='/geminiapi', room=f"{app_name}-{client_ip}")
            room.chat = response[1]
            rooms.set_user_room(client_ip, app_name, room)


@socketio.on('change_chat_model', namespace='/geminiapi')
def change_chat_model(data):
    """
    changes chat model
    """
    client_ip = get_client_ip()
    app_name = get_app_name()
    model_name = data['model_name']

    room = rooms.get_user_room(client_ip, app_name)

    chat = room.chat
    chat = change_model(chat, model_name)
    room.chat = chat
    rooms.set_user_room(client_ip, app_name, room)


# uploaded files handlers
@socketio.on('base64_load_start', namespace='/geminiapi')
def base64_load_start(data):
    """
    initializes upload process of a file
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)

    filename = data['filename']
    filetype = data['filetype']

    print(filetype)

    room.uploaded_files[filename] = {
        'data': '',
        'type': filetype,
        'state': 'loading'
    }
    rooms.set_user_room(client_ip, app_name, room)

@socketio.on('base64_load_chunk', namespace='/geminiapi')
def base64_load_chunk(data):
    """
    gets chunk of file and adds it to the file data
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)

    filename = data['filename']
    chunk = data['chunk']

    room.uploaded_files[filename]['data'] += chunk
    rooms.set_user_room(client_ip, app_name, room)

@socketio.on('base64_load_end', namespace='/geminiapi')
def base64_load_end(data):
    """
    finishes upload process of a file
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)

    filename = data['filename']

    room.uploaded_files[filename]["state"] = "finished"
    rooms.set_user_room(client_ip, app_name, room)
    print(f"File {filename} uploaded")

@socketio.on('remove_file', namespace='/geminiapi')
def remove_file(filename):
    """
    removes file from uploaded files
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    room = rooms.get_user_room(client_ip, app_name)


    if filename in room.uploaded_files:
        del room.uploaded_files[filename]
        rooms.set_user_room(client_ip, app_name, room)
        print(f"File {filename} removed")
# End of uploaded files handlers


@socketio.on('disconnect', namespace='/geminiapi')
def disconnect():
    """
    removes user from room
    """
    client_ip = get_client_ip()
    app_name = get_app_name()

    rooms.delete_user_room(client_ip, app_name)
#End of chat event
