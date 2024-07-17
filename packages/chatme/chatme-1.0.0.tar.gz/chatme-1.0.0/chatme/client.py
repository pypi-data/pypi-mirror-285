import socket
import threading

def receive_messages(sock, on_receive):
    while True:
        try:
            message = sock.recv(1024).decode()
            if message:
                on_receive(message)
            else:
                break
        except:
            break

def start_client(server_ip, server_port=12345, on_receive=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    threading.Thread(target=receive_messages, args=(client_socket, on_receive)).start()

    return client_socket
