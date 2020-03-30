#!/usr/bin/env python3

import socket

s = socket.socket()
print('Socket created')

port = 12345

s.bind(('', port))
print('Socket bound to ', port)

s.listen(5)
print('Socket is listening')

while True:
    c, addr = s.accept()
    print('Got connection from', addr)
    c.send(b'Thank you for connecting')
    c.close()


