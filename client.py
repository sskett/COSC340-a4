#!/usr/bin/env python3

# Import dependencies
import sys
import socket

# Set up required variables
HOST = sys.argv[1]
PORT = int(sys.argv[2])
MSGLEN = 2048
encoding = 'ascii'
active = False


def close_conn(s):
    """Properly closes the socket connection.
    Keyword arguments:
    s -- a socket connection
    """
    try:
        s.shutdown(socket.SHUT_RDWR)
    except socket.error as shutdown_err:
        print("Error shutting down socket", shutdown_err)
    try:
        s.close()
    except socket.error as close_err:
        print("Error closing socket", close_err)


def start_game(s):
    """Completes initial start up process by connecting to a game server.
    Keyword arguments:
    s -- a local socket
    """
    try:
        s.connect((HOST, PORT))
        s.sendall("START GAME".encode(encoding))
        return True
    except socket.error as err:
        print(err)
        close_conn(s)
        return False


def check_gameover(string):
    """Checks the server response to determine if the game has completed,
    Keyword arguments:
    string -- a decoded message received from the game server
    """
    try:
        int(string[0])
        return True
    except ValueError:
        return False


def take_user_input(s):
    """Prompts the user for their letter/word guess or a user-requested exit.
    Keyword arguments:
    s -- a socket connection to a game server
    """
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


def send_guess(s):
    """Takes a char string input by the user, converts it into an ASCII encoded byte-form and sends to
    the game server.
    Keyword arguments:
    s -- a socket connection to the game server
    """
    try:
        entry = take_user_input(s)
        s.sendall(entry.lower().encode(encoding))
    except socket.error as err:
        print("Connection lost:", err)
        s.close()
        return False
    except KeyboardInterrupt as user_err:
        print("\nGame process terminated by user.\n", user_err)
        s.close()
        return False
    return True


def receive_msg(s):
    """Receives a message in byte form from the game server and decodes it into an ASCII based string.
    Keyword arguments:
    s -- a socket connection to the game server
    """
    try:
        data = (s.recv(MSGLEN)).decode(encoding)
        return data
    except socket.error as err:
        print("Server communication error.\n", err)
        close_conn(s)
        return False


def process_guess(s):
    """If there is still an active connection, receives and displays to the user a masked string
    representing the current state (ie known/unknown letters) of the game word, then responds to the
    server with the player's next guess.
    Keyword arguments:
    s -- a socket connection to a game server
    """
    data = receive_msg(s)
    if len(data) == 0:
        print("Sorry, connection to the server has been lost. Exiting game...")
        s.close()
        return False
    elif data[0].isupper():
        print("Server response error. Disconnecting.")
        close_conn(s)
        return False
    elif check_gameover(data):
        print("Your score is:", data)
        close_conn(s)
        return False
    else:
        print(str(data))
        return send_guess(s)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        active = start_game(s)
        while active:
            active = process_guess(s)


