import socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_address = ('localhost', 5000)
client_socket.connect(client_address)
message = 'host'
client_socket.sendall(message.encode('utf-8'))
message = client_socket.recv(1024)
print(message.decode('utf-8'))

