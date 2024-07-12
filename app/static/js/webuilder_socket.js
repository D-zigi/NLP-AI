/* chat sockeio connection and events */
var socket = io('/webuilder', { forceBase64: true });

/* HTML Elements used for socket */
var text_input = document.getElementById('text-input')
var image_input = document.getElementById('image-input');
var submit = document.getElementById('submit');

var input_files_container = document.getElementById('input-files-container');

var selected_model_name = document.getElementById('model-name');

var welcoming_message = document.getElementById('welcoming')

const image_supported = [".png", ".jpg", ".jpeg", ".webp", ".heif", ".heic"]
const logs_supported = [".pkl"]

image_input.accept = image_supported.join(',');
logs_input.accept = logs_supported.join(',');

var filesData = {};
var files_size = 0;
const max_size = 1000000 * 10; // in bytes

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

function fileContainer(image_src, image_name) {
    var file_container = document.createElement('div')
    var img = document.createElement('div');
    file_container.id = image_name;
    file_container.classList = 'file-container';
    img.classList.add('img');
    img.style.backgroundImage = `url(${image_src})`;
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
            var remove_button = document.createElement('span');
            remove_button.classList.add('remove-button');
            remove_button.innerText = 'X';
            remove_button.onclick = function(event) { removeFile(image.name);};

            input_files_container.hidden = false;

            file_container.prepend(remove_button);
            input_files_container.appendChild(file_container);

            files_size += image.size;

            sendBase64Data(event.target.result.split(',')[1], image.name, image.type);
        }
    }
    reader.readAsDataURL(image);
}

function removeFile(filename) {
    document.getElementById(filename).remove();
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


socket.on('connect', () => {
    //promisedEmit('start_chat');
});

socket.on('disconnect', () => {
})

socket.on('error', (error) => {
    messages.lastChild.remove()
    errorAlert(error["message"], error["code"]);
});
