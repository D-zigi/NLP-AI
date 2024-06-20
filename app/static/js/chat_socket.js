function scrollToBottom(id) {
    var element = document.getElementById(id);
    element.scrollTop = element.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function () {
    var socket = io('/chat');

    current_chat = false; //TODO change boolean to "null | chat.id"

    /* Client input and server rensponse wait*/
    document.getElementById('text-input').addEventListener('keydown', function(event) {
        if (event.key == 'Enter' & event.shiftKey == false & this.innerText.trim() != '') {
            event.preventDefault();
            
            if (!current_chat) {
                socket.emit('start_chat');
                current_chat = true;
            }

            var client_message = document.getElementById('text-input').innerText;
            document.getElementById('text-input').innerText = '';
            socket.emit('message', { text: client_message });
        }
    });


    /* For CLIENT message handling */
    socket.on('client-message', function(message) {
        var client_message = document.createElement('div');
        client_message.classList = 'client-message message glass';

        client_message.innerHTML = message;

        document.getElementById('messages').appendChild(client_message);
        scrollToBottom('messages');
    });

    /* SERVER message typing(thinking) animation */
    socket.on('server-typing', function() { //TODO glass loaded block
        var gemini_responding = document.getElementById('gemini_response_common').cloneNode(true);
        gemini_responding.classList = 'server-message message';
        gemini_responding.id = ""

        document.getElementById('messages').appendChild(gemini_responding);
        scrollToBottom('messages');
    });
    /* For SERVER message handling */
    socket.on('server-message', function(message) {
        let server_messages = document.getElementsByClassName('server-message');
        let server_message = server_messages[server_messages.length - 1];

        var gemini_response = server_message.getElementsByClassName("typing")[0]

        gemini_response.classList = 'gemini-response'
        gemini_response.innerHTML = message;
        
        document.getElementById('messages').appendChild(server_message);
        scrollToBottom('messages');
    });

});