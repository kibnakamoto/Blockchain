import socket

sock = socket.socket()
host = '192.168.0.19' # socket.gethostname()
port = 8333

sock.connect((host, port))

print(sock.recv(1024).decode())

print(sock, "\n", host)
