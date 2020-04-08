#!/usr/bin/env python3

import socket

HOST = ''
PORT = 65432
MAX_CONNS = 1
encoding = 'ascii'


def respond_to_user(data):
    if data.decode(encoding) == 'START GAME':
        conn.sendall(b'OK')
    else:
        conn.sendall(data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(MAX_CONNS)
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            print('User says: ' + data.decode(encoding))
            if not data: break
            respond_to_user(data)
