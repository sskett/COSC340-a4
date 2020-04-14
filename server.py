#!/usr/bin/env python3

import sys
import socket


HOST = 'localhost'
PORT = int(sys.argv[1])
MAX_CONNS = 1
encoding = 'ascii'


def respond_to_user(data, conn):
    if data.decode(encoding) == 'START GAME':
        print("Starting game")
    else:
        conn.sendall(data)


def play_hangman():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(MAX_CONNS)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if not data.decode(encoding) == 'START GAME':
                msg = "Invalid start request. Disconnecting..."
                conn.sendall(msg.encode(encoding))
                s.close()
            else:
                print("Starting game")
                conn.send(b'Let\'s play hangman')
                while True:
                    data = conn.recv(1024)
                    if not data: break
                    respond_to_user(data, conn)


if __name__ == "__main__":
    try:
        play_hangman()
    except socket.error as err:
        print("Unable to create the socket on " + str(HOST) + ":" + str(PORT) + "\n" + str(err))
