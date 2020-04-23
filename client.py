#!/usr/bin/env python3

import sys
import socket
import unicodedata

# Define globals
HOST = sys.argv[1]
PORT = int(sys.argv[2])
encoding = 'ascii'
active = False


def close_conn(s):
    try:
        s.shutdown(socket.SHUT_RDWR)
    except socket.error as shutdown_err:
        print("Error shutting down socket", shutdown_err)
    try:
        s.close()
    except socket.error as close_err:
        print("Error closing socket", close_err)


def start_game(s):
    try:
        s.connect((HOST, PORT))
        s.sendall("START GAME".encode(encoding))
        data = ""
        if data == "Invalid start request. Disconnecting...":
            return False
        else:
            print(data)
            return True
    except socket.error as err:
        print(err)
        close_conn(s)
        return False


def is_number(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def take_user_input(s):
    while True:
        entry = input("What's your guess?\n")
        if entry.isalpha():
            break
        else:
            print("Please enter only letters in range a-z\n")
    if entry == "{quit}" or entry == "":
        print("Exiting game...")
        close_conn(s)
        return False
    return entry


def play_game(s):
    data = ""
    data = (s.recv(1024)).decode(encoding)
    if len(data) == 0:
        print("Sorry, connection to the server has been lost. Exiting game...")
        s.close()
        return False
    elif is_number(data):
        print("Your score is:", data)
        #TODO: Need to process fixed length messages to split score from GAME OVER signal
        data = (s.recv(1024)).decode(encoding)
        print(data)
        close_conn(s)
        return False
    else:
        print(str(data))
        try:
            entry = take_user_input(s)
            s.sendall(entry.lower().encode(encoding))
        except socket.error as err:
            print("Connection lost:", err)
            s.close()
            return False
        return True


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        active = start_game(s)
        while active:
            active = play_game(s)


