#!/usr/bin/env python3

"""
This is the game client for the word guessing game required for COSC340 Assignment 2. The client will connect to a server
and run the game until the game completes or there is an error.
CLI Arguments:
    1 - hostname
    2 - communication port
"""

# Import dependencies
import sys, socket, ssl, hmac, hashlib
from Crypto.Cipher import AES
from Crypto import Random


# Set up required variables
try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except IndexError as err:
    print("Failed to run game client. Insufficient arguments - please provide valid hostname and port number.")
    sys.exit(1)
MSGLEN = 1024  # the maximum size of any individual message
encoding = 'ascii'  # the encoding to be used for strings (as messages are sent and received in byte-form)
active = False  # a flag indicating game state

server_hostname = 'cosc340GameServer'
server_certfile = 'server.crt'
client_certfile = 'client.crt'
client_keyfile = 'client.key'

blocksize = 16
session_key = Random.new().read(32)
hkey = Random.new().read(16)



def close_conn(s):
    """Properly closes the socket connection.
    Keyword arguments:
    s -- a socket connection
    """
    try:
        s.shutdown(socket.SHUT_RDWR)
    except socket.error as shutdown_err:
        print("Error shutting down socket.\n", shutdown_err)
    try:
        s.close()
    except socket.error as close_err:
        print("Error closing socket.\n", close_err)


def start_game(s):
    """Completes initial start up process by connecting to a game server.
    Keyword arguments:
    s -- a local socket
    """
    try:
        s.connect((HOST, PORT))
    except socket.error as conn_err:
        print("Error connecting to server.\n", conn_err)
        return False
    try:
        s.sendall("START GAME".encode(encoding) + session_key)
        global game_hash
        game_hash = (receive_msg(s))[:-1]
    except socket.error as send_err:
        print("Error communicating with server. Exiting game.\n", send_err)
        close_conn(s)
        return False
    return True


def check_gameover(string):
    """Checks the server response to determine if the game has completed,
    Keyword arguments:
    string -- a decoded message received from the game server
    """
    try:
        int(string.splitlines()[0])
        return True
    except ValueError:
        return False


def take_user_input(s):
    """Prompts the user for their letter/word guess or a user-requested exit.
    Keyword arguments:
    s -- a socket connection to a game server
    """
    try:
        while True:
            entry = input("What's your guess?\n")
            if entry.isalpha():
                break
            else:
                print("Please enter only letters in range a-z\n")
    except KeyboardInterrupt as user_err:
        print("\nGame process terminated by user.\n", user_err)
        s.close()
        return False
    return entry


def encrypt16(msg, key):
    hmsg = msg
    while len(msg) % 16 != 0:
        msg = msg + "^"
    iv = Random.new().read(16)
    hsig = hmac_signature(hmsg.encode(encoding), iv)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = iv + hsig + cipher.encrypt(msg)
    return ciphertext


def decrypt16(msg, key):
    iv = msg[:16]
    signature = msg[16:80].decode(encoding)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(msg[80:]).decode(encoding)
    if plaintext.endswith('^'):
        while plaintext.endswith('^'):
            plaintext = plaintext[:-1]
    h = hmac_signature(plaintext.encode(encoding), iv).decode(encoding)
    if not h == signature:
        print('HMAC failure') #TODO: raise an exception to exit the game
    return plaintext


def hmac_signature(msg, key):
    h = hmac.new(key, msg, hashlib.sha3_256)
    return h.hexdigest().encode(encoding)


def send_guess(s):
    """Takes a char string input by the user, converts it into an ASCII encoded byte-form and sends to
    the game server.
    Keyword arguments:
    s -- a socket connection to the game server
    """
    try:
        entry = take_user_input(s)
        if not entry:
            return False
        s.sendall(encrypt16(entry.lower(), session_key))
    except socket.error as err:
        print("Connection lost:", err)
        s.close()
        return False
    return True


def contains_upper(string):
    """Checks if there are any uppercase characters in the string."""
    for c in string:
        if c.isupper():
            return True


def receive_msg(s):
    """Receives a message in byte form from the game server and decodes it into an ASCII based string.
    Keyword arguments:
    s -- a socket connection to the game server
    """
    try:
        data = decrypt16(s.recv(MSGLEN), session_key)
        return data
    except socket.error as err:
        print("Server communication error.\n", err)
        close_conn(s)
        return False


def check_valid_game(word, key, hashval):
    word_hash = hashlib.sha3_256(key + word.encode(encoding)).hexdigest()

    return word_hash == hashval


def process_end_game(data, conn):
    msg = data.splitlines()
    if check_valid_game(msg[2], session_key, game_hash):
        print("Your score is:", msg[0])
        print(msg[1])
    else:
        print("Game invalid - server word hash doesn't match")

    close_conn(conn)


def process_guess(s):
    """If there is still an active connection, receives and displays to the user a masked string
    representing the current state (ie known/unknown letters) of the game word, then responds to the
    server with the player's next guess.
    Keyword arguments:
    s -- a socket connection to a game server
    """
    data = receive_msg(s)
    if not data or len(data) == 0:
        print("Server response error. Terminating game.\n")
        close_conn(s)
        return False
    end_game = check_gameover(data)
    if end_game:
        process_end_game(data, s)
        return False
    elif not end_game and contains_upper(data):
        print("Invalid response from server. Terminating game.\n")
        close_conn(s)
        return False
    else:
        print(str(data))
        return send_guess(s)


if __name__ == "__main__":

    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_certfile)
    context.load_cert_chain(certfile=client_certfile, keyfile=client_keyfile)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = context.wrap_socket(s, server_side=False, server_hostname=server_hostname)
    try:
        active = start_game(conn)
        while active:
            active = process_guess(conn)
    except socket.error as err:
        print(err)
    finally:
        conn.close()
