import socket
import threading

# Server configuration
HOST = 'localhost'
PORT = 5000

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

# Lists for keeping track of connected clients, their nicknames, and messages
clients = []
nicknames = []
message_history = []

# Locks for thread synchronization
lock = threading.Lock()


# Broadcast messages to all connected clients
def broadcast(message):
    with lock:
        for client in clients:
            client.send(message)


# Handle individual client connections
def handle_client(client):
    while True:
        try:
            message = client.recv(1024)
            if message.decode('utf-8').startswith('PRIVATE'):
                # Private message
                _, recipient, content = message.decode('utf-8').split(' ', 2)
                send_private_message(recipient, content, client)
            else:
                # Broadcast message
                broadcast(message)
                save_message_to_history(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            broadcast(f'{nickname} left the chatroom!'.encode('utf-8'))
            break


# Save message to message history
def save_message_to_history(message):
    with lock:
        message_history.append(message)


# Send message history to a client
def send_message_history(client):
    with lock:
        for message in message_history:
            client.send(message)


# Send a private message to a specific client
def send_private_message(recipient, content, sender):
    with lock:
        if recipient in nicknames:
            recipient_index = nicknames.index(recipient)
            recipient_client = clients[recipient_index]
            sender_nickname = nicknames[clients.index(sender)]
            private_message = f'[PRIVATE] {sender_nickname}: {content}'.encode('utf-8')
            recipient_client.send(private_message)
            sender.send(private_message)
        else:
            sender.send('Recipient not found!'.encode('utf-8'))


# Accept and handle incoming client connections
def accept_connections():
    while True:
        client, address = server_socket.accept()
        print(f'Connected with {str(address)}')

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)

        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chatroom!'.encode('utf-8'))
        client.send('Connected to the chatroom!'.encode('utf-8'))

        # Send message history to the client
        send_message_history(client)

        client.send('You are now connected!'.encode('utf-8'))
        client.send('Start messaging!'.encode('utf-8'))

        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()


# Start the server and accept connections
print('Server started!')
accept_connections()
