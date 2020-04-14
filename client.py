#!/usr/bin/env python3

import sys
import socket

# Define globals
HOST = sys.argv[1]
PORT = int(sys.argv[2])
encoding = 'ascii'


def start_game(s):
    try:
        s.connect((HOST, PORT))
        s.sendall(("START GAM").encode(encoding))
        data = s.recv(1024)
        data = data.decode(encoding)
        if data == "Invalid start request. Disconnecting...":
            print(data)
            s.close()
            return False
        else:
            print(data)
            return True
    except socket.error as err:
        print(err)
        s.close()
        return False


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    active = start_game(s)
    while active:
        data = ""
        entry = input("What do you want to say?")
        if entry == "{quit}" or entry == "":
            print("Exiting game...")
            s.close()
            active = False
        else:
            try:
                s.sendall(entry.encode(encoding))
                data = s.recv(1024)
            except socket.error as err:
                print("Connection lost:", err)
                active = False
                break
            if len(data) == 0:
                print("Sorry, connection to the server has been lost. Exiting game...")
                active = False
                break
            else:
                data = data.decode(encoding)
                print(str(data))


