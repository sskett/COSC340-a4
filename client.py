#!/usr/bin/env python3

import socket

# Define globals
HOST = "localhost"
PORT = 65432
encoding = 'ascii'


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    entry = (input("What do you want to say?")).encode(encoding)
    while entry:
        s.sendall(entry)
        data = s.recv(1024)
        data = data.decode(encoding)
        print(str(data))
        entry = (input("What do you want to say?")).encode(encoding)


