#!/usr/bin/env python3

import sys
import socket

# Define globals
HOST = sys.argv[1]
PORT = int(sys.argv[2])
encoding = 'ascii'
active = False


def start_game(s):
    try:
        s.connect((HOST, PORT))
        s.sendall(("START GAME").encode(encoding))
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


def manage_input(s):
    data = ""
    data = (s.recv(1024)).decode(encoding)
    if len(data) == 0:
        print("Sorry, connection to the server has been lost. Exiting game...")
        return False
    elif "You got it!" in data:
        print(s.recv(1024).decode(encoding))
        print(s.recv(1024).decode(encoding))
        s.close()
        return False
    else:
        print(str(data))
        try:
            entry = input("What's your guess?\n")
            if entry == "{quit}" or entry == "":
                print("Exiting game...")
                s.close()
                return False
            s.sendall(entry.encode(encoding))
        except socket.error as err:
            print("Connection lost:", err)
            return False
        return True


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    active = start_game(s)
    while active:
        active = manage_input(s)


