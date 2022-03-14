import socket
port = 5000
found = False
while (not found):
    print(port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect_ex(('localhost', port))
        found = True
    except:
        port += 10
        continue
print(port)