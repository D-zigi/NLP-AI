document.addEventListener('DOMContentLoaded', function () {
    var socket = io('/chat');

    current_chat = false;

    /* For SERVER message handling */
    socket.on('message', function(message) {
        var server_message = document.createElement('div');
        server_message.classList.add('server-message');

        server_message.innerHTML = message;
        
        document.getElementById('messages').appendChild(server_message);
    });

    /* For CLIENT message handling */
    document.getElementById('text-input').addEventListener('keyup', function(event) {
        if (event.key == 'Enter' & event.shiftKey == false) {
            event.preventDefault();

            var text = document.getElementById('text-input').value;

            var client_message = document.createElement('div');
            client_message.classList.add('client-message');
            client_message.textContent = text; //TODO python auto formatting
            document.getElementById('messages').appendChild(client_message);
            
            if (!current_chat) {
                socket.emit('start_chat');
                current_chat = true;
            }

            socket.emit('message', { text: text });
            document.getElementById('text-input').value = '';
        }
    });
});