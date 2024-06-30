/* chat sockeio connection and events */

var socket = io('/chat', { forceBase64: true });

/* HTML Elements used for socket */
var logs_input = document.getElementById('logs-input');

var text_input = document.getElementById('text-input')
var image_input = document.getElementById('image-input');
var submit = document.getElementById('submit');

var selected_model_name = document.getElementById('model-name');

var messages_container = document.getElementById('messages-container')
var messages = document.getElementById('messages')
var server_message_common = document.getElementById('server_message_common')
var client_message_common = document.getElementById('client_message_common')
var welcoming_message = document.getElementById('welcoming')


const image_supported = [".png", ".jpg", ".jpeg", ".webp", ".heif", ".heic"]
const logs_supported = [".pkl"]

image_input.accept = image_supported.join(',');
logs_input.accept = logs_supported.join(',');


var model = selected_model_name.innerText; //Gets default model name from HTML
var promise = false; // response/other promises that require waiting before sending response 
var input = false; // input acceptance (whitespace only - false)

/**
 * calls custom alert in red color and error message
 * @param {String} error_message
 * @param {Number} error_code
 */
function errorAlert(error_message, error_code) {
    console.error(`Error ${error_code}:${error_message}`);
    customAlert(error_message, 'error');
}

/**
 * call emit with promise waiting
 * @param {String} event 
 * @param {Object} data 
 */
function promisedEmit(event, data) {
    promise = true
    submit_switch()
    try {
        if (data) {
            socket.emit(event, data, function() {
                promise = false
                submit_switch()
            })

        } else {
            socket.emit(event, function() {
                promise = false
                submit_switch()
            })
        }
    } catch(err) {
        console.log(err)

        promise = false
        submit_switch()
    }
}

/** 
 * starts chat with the specified model name
 * @param {String} model_name
*/
function startChat(model_name) {
    model = model_name
    promisedEmit('start_chat', { model_name: model });
}

/**
 * selected model is being processed and updated in the chat
 * @param {String} model - model name 
*/
function changeModel(model_name) {
    model = model_name
    selected_model_name.innerText = model;
    promisedEmit('change_chat_model', { model_name: model });
}

/**
 * Loads uploaded .json binary chat data (pickled) for loading the chat
 * @param {ArrayBuffer} chat_data - The binary data of the pickled chat
 */
function loadChat(chat_data) {
    logs_input.value = ''; //Clear logs input
    promisedEmit('load_chat', chat_data);
}

/**
 * downloads current chat on user's local storage
 */
function downloadChat() {
    const html_data = messages.innerHTML;
    socket.emit('download_chat', html_data, function(chat_data, chat_name) {

        console.log(chat_data);

        // Create a Blob from the PKL data
        const blob = new Blob([chat_data], { type: 'application/octet-stream' });

        // Create a temporary URL for the Blob
        const url = URL.createObjectURL(blob);

        // Create a link element
        const a = document.createElement('a');
        a.href = url;
        a.download = `${chat_name.trim()}.pkl`; // File name
        document.body.appendChild(a);

        // Trigger the download
        a.click();

        // Clean up: remove the temporary URL and link element
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
}


function clearChat() {
    messages.innerHTML = '';
    promisedEmit('clear_chat', null);
}


/** 
 * submits message if submit is true - available 
*/
function message_submit() {
    var text = text_input.innerText;
    var image = imageData.base64String;

    text_input.innerText = ''; //Clear text input
    image_input.value = ''; //Clear image input

    input = false
    promisedEmit('message', { text: text, image: image });
}

/** 
 * submit switcher according to its current availability 
 * @returns {Boolean}
*/
function submit_switch() {
    var submit_available = input && !promise;

    submit.classList = "submit";
    submit.addEventListener('click', message_submit);

    if (!submit_available) {
        submit.classList.add("disabled");
        submit.removeEventListener('click', message_submit);
    }

    return submit_available
}

/* listens for chat logs input */
logs_input.addEventListener('change', function() {
    var reader = new FileReader()
    var logs = this.files[0];
    reader.onload = function(event) {
        if (logs_supported.includes('.' + logs.name.split('.')[1])) {
            const logsContent = event.target.result;
            loadChat(logsContent);
        }
        else {
            const error = "Unsupported Media Type";
            errorAlert(error, 415);
        }
    }
    reader.readAsArrayBuffer(logs);
});

/* listens for image input */
var imageData = {};
image_input.addEventListener('change', function() {
    var reader = new FileReader();
    var image = this.files[0];
    
    reader.onload = function(event) {
        if (image_supported.includes('.' + image.name.split('.')[1])) {
            imageData.base64String = event.target.result.split(',')[1];
            
            imageData.type = image.type;
            imageData.size = image.size;
            imageData.name = image.name;
            imageData.src = event.target.result;
        }
        else {
            const error = "Unsupported Media Type";
            errorAlert(error, 415);
        }
    }

    reader.readAsDataURL(image);
});

/* Client input and submit listeners */
text_input.addEventListener('input', function() {
    resizeOptimization(this, 0.5);
    input = (this.innerText.trim() != '');
    submit_switch();
});
text_input.addEventListener('keydown', function(event) {
    if (event.key == 'Enter' && !event.shiftKey && submit_switch()) {
        event.preventDefault();
        message_submit();
    }
});

/* Loads raw html chat */
socket.on('load-chat', (html_data) => {
    messages.innerHTML = html_data;
    scrollToBottom(messages_container);
});

/* For CLIENT message handling */
socket.on('client-message', (data) => {

    /**
     * constructs an html elment with clients message content
     * @param {String} message 
     * @param {Number} count 
     * @returns {Node}
     */
    function client_message_construct(message, count) {
        var client_message = client_message_common.cloneNode(true);
        client_message.hidden = false;
        client_message.id = `mc${count}`; // mc{count} - message_client_{count}
        
        var text_container = client_message.children[0];
        text_container.innerHTML = message;
        
        if (Object.keys(imageData).length != 0) {
            var file_container = client_message.children[1];
            file_container.hidden = false;
            file_container.innerText = imageData.name;

            var image = document.createElement('img');
            image.src = imageData.src;
            file_container.appendChild(image);
            
            imageData = {}; //clear input image data
        }

        return client_message;
    }
        
    const client_message = client_message_construct(data.message, data.count);
    messages.appendChild(client_message);
});
/* SERVER message typing(thinking) animation */
socket.on('server-typing', () => { //TODO glass loaded block
    var server_responding = server_message_common.cloneNode(true);
    server_responding.hidden = false;

    messages.appendChild(server_responding);
    scrollToBottom(messages_container);
});
/* For SERVER message handling */
socket.on('server-message', (message) => {
    let server_messages = document.getElementsByClassName('server-message');
    let server_message = server_messages[server_messages.length - 1];

    var gemini_response = server_message.getElementsByClassName("typing")[0];

    gemini_response.classList = 'gemini-response';
    gemini_response.innerHTML = message;
    
    messages.appendChild(server_message);
});

/* sends html-data for caching purposes */
socket.on('html-cache', () => {
    const html_data = messages.innerHTML;
    promisedEmit('html_cache', html_data);
});


socket.on('connect', () => {
    startChat(model); //Starts chat with default model
});


socket.on('error', (error) => {
    var server_messages = document.getElementsByClassName('server-message')
    var server_typing = server_messages[server_messages.length - 1];

    messages.removeChild(server_typing)
    errorAlert(error["message"], error["code"]);
});
