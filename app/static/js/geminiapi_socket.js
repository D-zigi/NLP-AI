/* chat sockeio connection and events */
const url = window.location.href.split('/')
const appName = url[url.length - 1];
var socket = io('/geminiapi', {
    forceBase64: true ,
    query: {
        appName: appName
    }
});

/* HTML Elements used for socket */
var logs_input = document.getElementById('logs-input');

var text_input = document.getElementById('text-input')
var image_input = document.getElementById('image-input');
var submit = document.getElementById('submit');

var input_files_container = document.getElementById('input-files-container');

var selected_model_name = document.getElementById('model-name');

var messages_container = document.getElementById('messages-container')
var messages = document.getElementById('messages')
var server_message_common = document.getElementById('server_message_common')
var client_message_common = document.getElementById('client_message_common')
var welcoming_message = document.getElementById('welcoming')

if (appName == 'chatbot') {
    var defaultData = '';
}
else if(appName == 'webuilder') {
    var server_response = document.getElementById("server-response");
    var webview = document.getElementById('webview');
    var code_container = document.getElementById('code-container');
    var defaultData = server_response.outerHTML;
}

const image_supported = [".png", ".jpg", ".jpeg", ".webp", ".heif", ".heic"]
const logs_supported = [".pkl"]

image_input.accept = image_supported.join(',');
logs_input.accept = logs_supported.join(',');

var filesData = {};
var files_size = 0;
const max_size = 1000000 * 10; // in bytes

var html_data_path = null;

var model = selected_model_name.innerText; //Gets default model name from HTML
document.getElementById(model).classList.add("selected");

var promise = false; // response/other promises that require waiting before sending response 
var input = false; // input acceptance (whitespace only - false)


/**
 * call emit with promise waiting
 * @param {String} event 
 * @param {Object} data 
 */
function promisedEmit(event, data = null) {
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
 * selected model is being processed and updated in the chat
 * @param {String} model - model name 
*/
function changeModel(model_name) {
    old_model = model;
    model = model_name
    if (old_model != model) {
        document.getElementById(old_model).classList.remove("selected");
        document.getElementById(model).classList.add("selected");

        selected_model_name.innerText = model;
        promisedEmit('change_chat_model', { model_name: model });
    }
}

/**
 * sends html_data for update chat data on server side
 * saves the data in external db and storage
 * @param {String} html_data 
 */
function updateChat(html_data) {
    const chunkSize = max_size;
    const totalChunks = Math.ceil(html_data.length / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = (i + 1) * chunkSize;
        const chunk = html_data.substring(start, end);
        socket.emit('update_chat', chunk);
    }
}

/**
 * clears chat on the server and client
 */
function clearChat() {
    promisedEmit('clear_chat', defaultData)
}


/**
 * Loads chat html data
 * @param {String} html_data_path - html data path
 * @param {Number} attempts
 */
function loadChat(html_data_path, attempts = 0) {
    const timeout = 1000; //ms
    const max_attempts = 5;

    fetch(html_data_path)
    .then(response => response.text())
    .then(text => {
        if (text.includes("<title>404</title>")) {
            if (attempts < max_attempts) {
                setTimeout(loadChat, timeout / max_attempts, html_data_path, attempts + 1);
            }
            text = "";
        }
        
        messages.innerHTML = text;
        scrollToBottom(messages_container);
    })
    .catch(
        error => console.error('Error fetching the file:', error)
    );
}

/**
 * downloads current chat on user's local storage
 * temporarly unused function on the app due to lack of additional server:
 * for each user folder: .pkl .txt + other.pkl
 */
function downloadChat() {
    socket.emit('download_chat', function(data_path, chat_name) {
        // Fetch the file from the server using the provided URL
        fetch(data_path)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(blob => {
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
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    });
}

/**
 * uploads chat to server
 * @param {String} data_url 
 */
function uploadChat(data_url) {
    promisedEmit('load_chat', data_url);
}


/**
 * sends base64 data to the server in seperate chunks.
 * @param {String} data - file base64 data
 * @param {String} filename - file name
 * @param {String} filetype - file type
 */
function sendBase64Data(data, filename, filetype) {
    const chunkSize = 1024 * 1024 / 2;
    const totalChunks = Math.ceil(data.length / chunkSize);

    socket.emit('base64_load_start', {filename: filename, filetype: filetype});
    for (let i = 0; i < totalChunks; i++) {
        const start = i * chunkSize;
        const end = (i + 1) * chunkSize;
        const chunk = data.substring(start, end);
        socket.emit('base64_load_chunk', {filename: filename, chunk: chunk});
    }
    
    socket.emit('base64_load_end', {filename: filename});
}

/**
 * creates file container of the attached file
 * @param {String} image_src 
 * @param {String} image_name 
 * @returns 
 */
function fileContainer(image_src, image_name, upload = true) {
    var file_container = document.createElement('div')
    file_container.id = upload ? "upload-" + image_name : image_name;
    file_container.classList.add('file-container');
    
    var img = document.createElement('div');
    img.classList.add('img');
    img.style.backgroundImage = `url(${image_src})`;

    if (upload) {
        var remove_button = document.createElement('span');
        remove_button.classList.add('remove-button');
        remove_button.onclick = function() { removeFile(image_name); };
    
        file_container.appendChild(remove_button);
    }
    file_container.appendChild(img);
    
    return file_container
}

/**
 * passes all the checks and returns apennds all needed image data to `filesData`
 * if not passes returns errors accordingly
 * @param {Number} max_size - in bytes 
 * @param {File} image 
 */
function uploadImage(image) {
    const max_image_size = max_size
    const reader = new FileReader();
    let imageData = {};
    
    reader.onload = function(event) {

        if (!image_supported.includes('.' + image.name.split('.')[1])) { // If file is an unsupported image ext
            const error = "Unsupported Media Type";
            errorAlert(error, 415);
        }

        else if(image.size > max_image_size) { // If file is too large
            const error = "File too large";
            errorAlert(error, 413);
        }

        else if(files_size + image.size > max_size) { // If file limit is exceeded
            const error = "File limit exceeded";
            errorAlert(error, 413);
        }

        else {  // If OK
            imageData.type = image.type;
            imageData.size = image.size;
            imageData.src = event.target.result;

            filesData[image.name] = imageData;

            const file_container = fileContainer(imageData.src, image.name)

            input_files_container.appendChild(file_container);
            
            input_files_container.hidden = false;

            files_size += image.size;

            sendBase64Data(event.target.result.split(',')[1], image.name, image.type);
        }
    }
    reader.readAsDataURL(image);
}

/**
 * removes attached file
 * @param {String} filename 
 */
function removeFile(filename) {
    document.getElementById("upload-" + filename).remove();
    files_size -= filesData[filename].size;
    delete filesData[filename];
    if (Object.keys(filesData).length == 0) {
        input_files_container.hidden = true;
    }
    socket.emit('remove_file', filename);
};


/** 
 * submits message if submit is true - available 
*/
function message_submit() {
    var text = text_input.innerText;

    text_input.innerText = ''; //Clear text input
    image_input.value = ''; //Clear images input

    input = false
    promisedEmit('message', { text: text });
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
    errorAlert("Service Unavailable, Maintenance Mode", 503);
    var logs = this.files[0];
    //TODO POST
});

/* listens for image input */
image_input.addEventListener('change', function() {
    var images = this.files;
    
    for (const image of images) {
        uploadImage(image);
    }
});
text_input.addEventListener('paste', function(event) {
    const files = event.clipboardData.files;
    for (const file of files) {
        uploadImage(file);
    }
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
socket.on('load-chat', (html_data_path) => {
    loadChat(html_data_path);
});

socket.on('change-model', (model_name) => {
    changeModel(model_name);
});

if (appName == 'chatbot') {
    /* For CLIENT message handling */
    socket.on('client-message', (data) => {
    
        /**
         * constructs an html elment with clients message content
         * @param {String} message 
         * @param {Number} count 
         * @returns {Node}
         */
        function client_message_construct(message, index) {
            var client_message = client_message_common.cloneNode(true);
            client_message.hidden = false;
            client_message.id = 'cm' + index; // cm{index} - client_message_{index}
            
            var text_container = client_message.querySelector('.text-container');
            text_container.innerHTML = message;
            
            if (Object.keys(filesData).length != 0) {
                for (const filename in filesData) {
                    var files_container = client_message.querySelector('.files-container');
                    files_container.hidden = false;
    
                    const file_container = fileContainer(filesData[filename].src, filename, removable = false)
    
                    files_container.appendChild(file_container);
                }
                filesData = {};
                input_files_container.hidden = true;
                input_files_container.innerHTML = '';
            }
    
            return client_message;
        }
        
        const message = data.message;
        const index = data.index;
    
        const client_message = client_message_construct(message, index);
        messages.appendChild(client_message);
        updateChat(client_message.outerHTML)
    });
    /* SERVER message responding animation */
    socket.on('server-responding', () => {
        var server_responding = server_message_common.cloneNode(true);
        server_responding.id = '';
        server_responding.hidden = false;
    
        messages.appendChild(server_responding);
        scrollToBottom(messages_container);
    });
    /* For SERVER message handling */
    socket.on('server-message', (data) => {
        const message = data.response;
        const index = data.index;
    
        let server_messages = document.getElementsByClassName('server-message');
        let server_message = server_messages[server_messages.length - 1];
    
        server_message.id = 'sm' + index; // sm{index} - server_message_{index}'
    
        var typing = document.querySelectorAll(".typing")[1];
        typing.remove();
    
        var text_container = server_message.querySelector('.text-container');
        text_container.innerHTML = message;
        
        updateChat(server_message.outerHTML)
    });
}
else if (appName == 'webuilder') {
    /* For CLIENT message handling */
    socket.on('client-message', (data) => {
    
        /**
         * constructs an html elment with clients message content
         * @param {String} message 
         * @param {Number} count 
         * @returns {Node}
         */
        function client_message_construct(message, index) {
            var client_message = client_message_common.cloneNode(true);
            client_message.hidden = false;
            client_message.id = 'cm' + index; // cm{index} - client_message_{index}
            
            var text_container = client_message.querySelector('.text-container');
            text_container.innerHTML = message;
            
            if (Object.keys(filesData).length != 0) {
                for (const filename in filesData) {
                    var files_container = client_message.querySelector('.files-container');
                    files_container.hidden = false;
    
                    const file_container = fileContainer(filesData[filename].src, filename, removable = false)
    
                    files_container.appendChild(file_container);
                }
                filesData = {};
                input_files_container.hidden = true;
                input_files_container.innerHTML = '';
            }
    
            return client_message;
        }
        
        const message = data.message;
        const index = data.index;
    
        const client_message = client_message_construct(message, index);
        messages.appendChild(client_message);
    });
    /* SERVER message responding animation */
    socket.on('server-responding', () => {
        // var server_responding = server_message_common.cloneNode(true);
        // server_responding.id = '';
        // server_responding.hidden = false;
    
        // messages.appendChild(server_responding);
        // scrollToBottom(messages_container);
    });
    /* For SERVER message handling */
    socket.on('server-message', (data) => {
        // webview = document.getElementById('webview');
        const message = data.response;
        var webview = document.getElementById('webview');
        var code_container = document.getElementById('code-container');

        server_message = document.createElement('div');
        server_message.innerHTML = message;

        if (message.includes("<pre>")) {
            const html_code = server_message.querySelector('pre').innerText.replace('HTML', '');
            console.log(html_code);
            code_container.innerHTML = message;
            
            webview.srcdoc = html_code;
            // welcoming_message.style.display = 'none';
            webview.classList.add('active');
        }

        else if (message.includes("EMPTY")) {
            errorAlert("Try again, Bad Request", 400);
        }

        else {
            errorAlert("Invalid server response, try again or change model, Internal Server Error", 500);
        }

        updateChat(messages.innerHTML);
    });
}

socket.on('connect', () => {
    promisedEmit('start_chat', defaultData);
});

socket.on('disconnect', () => {
})

socket.on('error', (error) => {
    messages.lastChild.remove()
    errorAlert(error["message"], error["code"]);
});
