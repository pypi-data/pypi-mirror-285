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

def start_server(local_ip='0.0.0.0', local_port=12345, on_receive=None):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((local_ip, local_port))
    server_socket.listen(1)

    client_socket, client_address = server_socket.accept()

    threading.Thread(target=receive_messages, args=(client_socket, on_receive)).start()

    return server_socket, client_socket
