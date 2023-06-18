import socket
import threading

# Client configuration
HOST = 'localhost'
PORT = 5000

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


# Listen for incoming messages from the server
def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(message)
        except:
            print('An error occurred while receiving the message!')
            client_socket.close()
            break


# Send messages to the server
def send_message():
    while True:
        message = input('')
        if message.lower() == 'quit':
            client_socket.send('quit'.encode('utf-8'))
            client_socket.close()
            break
        client_socket.send(message.encode('utf-8'))


# Start receiving and sending messages
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

send_thread = threading.Thread(target=send_message)
send_thread.start()
