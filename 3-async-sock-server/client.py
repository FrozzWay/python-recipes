import socket

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.0.150', 8088))
    while text := input():
        s.sendall((text + '\n').encode('utf-8'))
        msg = s.recv(1024*12)
        print(msg.decode('utf-8'))