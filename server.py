#!/usr/bin/env python3

"""
This is the single player server for the word guessing game required for COSC340 Assignment 2. The server will accept
a connection and communicate with a single player via a TCP socket.

CLI Arguments:
    1 - communication port
"""

# Import dependencies
import sys, socket, random, ssl, hashlib
from game_sec import encrypt16
from game_sec import decrypt16


# Set up required variables
HOST = ''
try:
    PORT = int(sys.argv[1])
except IndexError:
    print("Failed to initiate server. No port number provided.")
    sys.exit(1)

MAX_CONNS = 1           # this is a single player server
MSGLEN = 1024           # maximum size of any single message
encoding = 'ascii'      # the encoding for strings (as messages are sent and received in byte-form)

# Details required for establishing a secure connection. Note: Self-signed certificates are used
# in lieu of a third party certification authority (CA)
server_certfile = 'server.crt'
server_keyfile = 'server.key'
client_certfiles = 'client.crt'


def create_socket():
    """Creates and configures a socket for use by the game server."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(certfile=server_certfile, keyfile=server_keyfile)
    context.load_verify_locations(cafile=client_certfiles)
    context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(MAX_CONNS)

    return s, context


def create_word_list(filename):
    """Selects a random word from a given text file.
    The input file should have one word per line.

    Keyword arguments:
    filename -- a text file containing one word per line (a-z chars only)
    """
    try:
        file = open(filename, "r")
        word_list = file.read().splitlines()
        file.close()
    except FileNotFoundError as err:
        print("Fatal error opening game dictionary:", err)
        sys.exit(1)
    for w in word_list:
        if not w.isalpha():
            word_list.remove(w)
    if len(word_list) < 1:
        print("No valid words found\n")
        sys.exit(1)
    else:
        return word_list[random.randrange(0, len(word_list))].lower()


def close_conn(s):
    """Properly closes the socket
    Keyword arguments:
    s -- a socket connection
    """
    s.shutdown(socket.SHUT_RDWR)
    s.close()


def letter_guess(guess, display):
    """Checks if the guessed letter is in the word and uncovers any matching blank spaces for the player if so.
    Keyword arguments:
    guess -- the player's guess, which should be a single character in the range a-z
    display -- the current 'blankified' representation of the game word that has been displayed to the player
    """
    global char_guesses_count
    char_guesses_count += 1
    if guess in guesses:
        return
    else:
        guesses.append(guess)
        for i in range(0, len(display)):
            if guess == word[i]:
                display[i] = guess


def word_guess(guess, display):
    """Checks if the player's guess matches the word and triggers the end game if it does.
    Keyword arguments:
    guess -- the player's guess, which should be a single word string consisting of characters from a-z
    display -- the current 'blankified' representation of the game word that has been displayed to the player
    """
    global word_guesses_count
    word_guesses_count += 1
    if guess == word:
        return word
    else:
        return display


def send_msg(msg, conn):
    """Appends a newline to the base message string and sends the message using ASCII encoding.
    Keyword arguments:
    msg -- a string that is to be sent to the connected user
    conn -- a socket connection
    """
    msg = encrypt16(msg + "\n", game_key, )
    conn.sendall(msg)


def arr_to_str(arr):
    """Converts an array to a string.
    Keyword arguments:
    arr -- an array of characters, eg representing the characters in the game word
    """
    to_string = ""
    for c in arr:
        to_string += c
    return to_string


def calc_score():
    """Calculates the player's score based on the difficulty of the word and how many guesses they needed."""
    score = (len(word) * 10) - (char_guesses_count * 2) - word_guesses_count
    return str(score)


def setup_game(addr, display):
    """Outputs connection details to the server terminal and prepares a blanked version of the word to display.
    Keyword arguments:
    addr -- the IP address of the user connected to the socket
    display -- an array to store the blank character representation of the game word
    """
    print("Starting game. Connected with:", addr)
    for c in word:
        display.append("_")
    print("The word is:", word)
    global game_hash
    game_hash = hashlib.sha3_256(game_key + word.encode(encoding)).hexdigest()


def recv_valid_msg(conn, msglen):
    """Receives a user input message and check that it is valid, ie only contains characters from a-z and is only
    one line. If an invalid message is detected the user is disconnected.
    Keyword arguments:
    conn - a socket connection to the user
    msglen - the maximum message length for the connection
    """
    try:
        data = decrypt16(conn.recv(msglen), game_key)
    except socket.error as err:
        print("Error receiving message:", err)
        close_conn(conn)
    if not data or len(data) == 0:
        return ""

    msg = data
    if len(msg.splitlines()) > 1 or not msg.isalpha() or contains_upper(msg):
        print("Invalid user input. Game terminated.")
        close_conn(conn)
    else:
        return msg


def contains_upper(string):
    """Checks if there are any uppercase characters in the string."""
    for c in string:
        if c.isupper():
            return True


def run_game(conn, display):
    """Outputs the current display word to the player with unknown letters shown as '_'.
     Loops until the player guesses the word or has guessed every letter.
    Keyword arguments:
    conn -- a socket connection
    display -- the array of masked characters representing the game word being displayed to the user
    """
    while "_" in display:
        send_msg(arr_to_str(display), conn)
        guess = recv_valid_msg(conn, MSGLEN)
        if len(guess) == 0:
            break
        elif len(guess) > 1:
            display = word_guess(guess, display)
        else:
            letter_guess(guess, display)


def end_game(conn):
    """Output appropriate messages to signal the end of the game.
    Keyword arguments:
    conn -- a socket connection
    """
    send_msg(calc_score() + "\nGAME OVER\n" + word, conn)
    print("Game ended.\n")


def play_hangman(s, c):
    """Creates a socket for a single-user and manages the game state.
    Keyword arguments:
    s -- a server socket which will connect to a player
    """
    ssock, addr = s.accept()
    try:
        conn = c.wrap_socket(ssock, server_side=True)
        with conn:
            letters = []
            data = conn.recv(MSGLEN)
            if not data[:10].decode(encoding) == 'START GAME':
                close_conn(s)
            else:
                global game_key
                game_key = data[10:]
                setup_game(addr, letters)
                send_msg(game_hash, conn)
                try:
                    run_game(conn, letters)
                    end_game(conn)
                except socket.error as err:
                    print("Connection to user lost.\n", err)
                    close_conn(s)
                    return
                except KeyboardInterrupt:
                    print("\nGame instance terminated by user.")
                    close_conn(s)
    except ssl.SSLError as ssl_err:
        print(ssl_err)
    finally:
        close_conn(s)


if __name__ == "__main__":
    while True:
        s, c = create_socket()
        print("\nWaiting for game request...")
        word = create_word_list("wordList.txt")
        guesses, word_guesses = [], []
        char_guesses_count, word_guesses_count = 0, 0
        try:
            play_hangman(s, c)
        except socket.error as err:
            print("Unable to create the socket on " + str(HOST) + ":" + str(PORT) + "\n" + str(err))
        except ValueError as val_err:
            print("User disconnected. Error in user's secure message.")
        except KeyboardInterrupt or SystemExit:
            print("\nServer process terminated by user.")
            close_conn(s)
            break
