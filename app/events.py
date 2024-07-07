"""
SocketIO
events handler

handle_join/handle_leave room events 
weren't implemented because of lack of usage
(single user per room is expected)
"""
import os
import pickle
import requests
import concurrent.futures
from flask import request
from bs4 import BeautifulSoup
from flask_socketio import join_room, leave_room, emit #, send

from .extensions import socketio
from .gemini_api.chat import create_chat, change_model, get_response, get_chat_name
from .formater import html_format

from .firebase import ChatRoom


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


def remove_html_duplicates(html_data, element, class_name):
    """
    removes html elements' duplicates
    """
    soup = BeautifulSoup(html_data, 'html.parser')
    non_duplicates = []
    seen = []
    for div in soup.find_all(element, class_=class_name):
        div_id = div.get('id')
        if div_id not in seen:
            seen.append(div_id)
            divs = soup.find_all(element, id=div_id)
            divs.sort(key=lambda x: len(str(x)), reverse=True)

            non_duplicates.append(str(divs[0]))

    return ''.join(non_duplicates)


def save_data(client_ip, data):
    """
    uploads .pkl data file
    """
    data_path = rooms_data[client_ip]['data_path']
    with open(data_path, 'wb') as file:
        pickle.dump(data, file)

def read_data(client_ip):
    """
    reads .pkl data file
    and removes it
    """
    data_path = rooms_data[client_ip]['data_path']
    with open(data_path, 'rb') as file:
        data = pickle.load(file)
    return data


def read_blob(blob_url):
    """
    reads blob data from url
    """
    response = requests.get(blob_url)
    return response.content


def save_html_data(client_ip, data=''):
    """
    saves html data to file
    """
    html_data_path = rooms_data[client_ip]['html_data_path']
    with open(html_data_path, encoding="utf-8", mode='w') as file:
        file.write(data)

def update_html_data(client_ip, data=''):
    """
    updates html data in file
    """
    html_data_path = rooms_data[client_ip]['html_data_path']

    # Step 1: Read the existing content
    with open(html_data_path, encoding="utf-8", mode='r') as file:
        old_data = file.read()

    # Step 2: Append the new data
    with open(html_data_path, encoding="utf-8", mode='a') as file:
        file.write(data)

    # Step 3: Read the updated content and process it to remove duplicates
    with open(html_data_path, encoding="utf-8", mode='r+') as file:
        file_content = file.read()
        new_data = remove_html_duplicates(file_content, 'div', 'message')

        # Move the file pointer to the beginning of the file
        file.seek(0)
        file.write(new_data)
        # Truncate the file to the length of new_data to remove any extra content
        file.truncate()

    modified = old_data != new_data

    return modified

def read_html_data(client_ip):
    """
    reads html data from file
    and removes it from TMP_PATH
    """
    html_data_path = rooms_data[client_ip]['html_data_path']
    with open(html_data_path, encoding="utf-8", mode='r') as file:
        html_data = file.read()
    return html_data


def join_data(client_ip):
    """
    extracts data related to client
    and joins it to .pkl file in TMP_PATH
    """
    chat = rooms_data[client_ip]["chat"]

    html_data = read_html_data(client_ip)
    model_name = chat.model.model_name.replace('models/', '')
    history = chat.history

    data = {
        "html_data": html_data,
        "model_name": model_name,
        "history": history
    }

    save_data(client_ip, data)

def split_data(client_ip):
    """
    extracts client's data from .pkl file
    and removes it from TMP_PATH
    """
    data = read_data(client_ip)

    html_data = data['html_data']
    model_name = data['model_name']
    history = data['history']

    return html_data, model_name, history


# Start of chat events

rooms_data = {} # keys for each room: "chat" - ChatSession
TMP_PATH = os.getenv('TMP_PATH')

@socketio.on('connect', namespace='/chat')
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

    if client_ip in rooms_data:
        rooms_data[client_ip]['sessions'] += 1
    else:
        rooms_data[client_ip] = {
            'sessions': 1,
            'data_path': f'{TMP_PATH}/chat-rooms/{client_ip}.pkl',
            'html_data_path': f'{TMP_PATH}/chat-rooms/{client_ip}_html_data.html',
            'uploaded_files': {},
            'chat': create_chat()
        }

    join_room(client_ip)
    print(f'User connected: {client_ip}')


@socketio.on('load_chat', namespace='/chat')
def load_chat(data_url=None, client_ip=None):
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
    if not client_ip: # if the function was called manually
        client_ip = get_client_ip()
        data = read_blob(data_url)
        print(data_url)
        print(data)
        # save_data(client_ip, data)

    html_data, model_name, history = split_data(client_ip)

    chat = create_chat(model_name, history)
    rooms_data[client_ip]["chat"] = chat
    # socketio.emit(change_model)
    print("finished loading")

    save_html_data(client_ip, html_data)

    socketio.emit(
        'load-chat',
        rooms_data[client_ip]['html_data_path'].replace('app/', ''),
        namespace='/chat',
        room=client_ip
    )

@socketio.on('download_chat', namespace='/chat')
def download_chat():
    """
    downloads chat data from database
    """
    client_ip = get_client_ip()
    chat = rooms_data[client_ip]["chat"]

    data_path = rooms_data[client_ip]['data_path'].replace('app/', '')
    chat_name = get_chat_name(chat)

    return data_path, chat_name


@socketio.on('save_chat', namespace='/chat')
def save_chat(client_ip=None):
    """
    saves chat data to .pkl file
    contains:
        'history' - chat history, 
        'model' - model name,
        'html_data' - html data

    returns optional chat name for file naming
    """
    if not client_ip: # if the function was called with emit
        client_ip = get_client_ip()
    join_data(client_ip)

    chat_room = ChatRoom(client_ip)
    chat_room.upload_data()
    print("finished saving")

@socketio.on('update_chat', namespace='/chat')
def update_chat(data):
    """
    updates chat history
    """
    client_ip = get_client_ip()

    if update_html_data(client_ip, data):
        save_chat(client_ip)


@socketio.on('start_chat', namespace='/chat')
def start_chat():
    """
    loads existing chat if already exist
    creates new chat othewise
    """
    client_ip = get_client_ip()
    chat_room = ChatRoom(client_ip)

    def load(_):
        print("loading data from local:")
        print(chat_room.local_data_path)
        load_chat(client_ip=client_ip)

    def download(future):
        result = future.result()
        exists = result
        print(f"User exists: {exists}")
        if exists:
            print("downloading data from database:")
            print(chat_room.data_url)
            await_function(
                chat_room.download_data,
                load
            )
        else:
            save_html_data(client_ip)
            save_chat(client_ip)
            chat_room.save()

    await_function(
        chat_room.exists,
        download,
    )

@socketio.on('clear_chat', namespace='/chat')
def clear_chat(client_ip=None):
    """
    clears chat history and stored html data
    """
    if not client_ip: # if the function was called with emit
        client_ip = get_client_ip()

    save_html_data(client_ip)
    rooms_data[client_ip]["chat"].history = []
    save_chat(client_ip)
    emit(
        'load-chat',
        rooms_data[client_ip]['html_data_path'].replace('app/', ''),
        namespace='/chat',
        room=client_ip
    )

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

    text = data['text']

    files = rooms_data[client_ip]['uploaded_files'] # get uploaded files
    rooms_data[client_ip]['uploaded_files'] = {} # clear uploaded files

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
            namespace='/chat',
            room=client_ip
        )

        # server is responding to clients' request
        emit('server-typing', namespace='/chat', room=client_ip)

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
                namespace='/chat',
                room=client_ip
            )

        else:
            emit('error', response[0], namespace='/chat', room=client_ip)
            rooms_data[client_ip]["chat"] = response[1]


@socketio.on('change_chat_model', namespace='/chat')
def change_chat_model(data):
    """
    changes chat model
    """
    client_ip = get_client_ip()
    model_name = data['model_name']

    chat = rooms_data[client_ip]["chat"]
    chat = change_model(chat, model_name)
    rooms_data[client_ip]["chat"] = chat


# uploaded files handlers
@socketio.on('base64_load_start', namespace='/chat')
def base64_load_start(data):
    """
    initializes upload process of a file
    """
    client_ip = get_client_ip()

    filename = data['filename']
    filetype = data['filetype']

    print(filetype)

    rooms_data[client_ip]['uploaded_files'][filename] = {
        'data': '',
        'type': filetype,
        'state': 'loading'
    }

@socketio.on('base64_load_chunk', namespace='/chat')
def base64_load_chunk(data):
    """
    gets chunk of file and adds it to the file data
    """
    client_ip = get_client_ip()

    filename = data['filename']
    chunk = data['chunk']

    rooms_data[client_ip]['uploaded_files'][filename]['data'] += chunk

@socketio.on('base64_load_end', namespace='/chat')
def base64_load_end(data):
    """
    finishes upload process of a file
    """
    client_ip = get_client_ip()
    filename = data['filename']

    rooms_data[client_ip]['uploaded_files'][filename]["state"] = "finished"
    print(f"File {filename} uploaded")

@socketio.on('remove_file', namespace='/chat')
def remove_file(filename):
    """
    removes file from uploaded files
    """
    client_ip = get_client_ip()

    if filename in rooms_data[client_ip]['uploaded_files']:
        del rooms_data[client_ip]['uploaded_files'][filename]
        print(f"File {filename} removed")
# End of uploaded files handlers

@socketio.on('disconnect', namespace='/chat')
def disconnect():
    """
    removes user from room
    """
    client_ip = get_client_ip()

    rooms_data[client_ip]['sessions'] -= 1
    if rooms_data[client_ip]['sessions'] == 0:
        leave_room(client_ip)
        print(f'User disconnected: {client_ip}')
        os.remove(rooms_data[client_ip]['data_path'])
        os.remove(rooms_data[client_ip]['html_data_path'])
        del rooms_data[client_ip]
#End of chat event
