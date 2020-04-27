#!/usr/bin/env python3

# Import dependencies
import sys
import socket
import random

# Set up required variables
HOST = 'localhost'
PORT = int(sys.argv[1])
MAX_CONNS = 1
MSGLEN = 2048
encoding = 'ascii'


def create_socket():
    """Creates and configures a socket for use by the game server."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(MAX_CONNS)
    return s


def create_word_list(filename):
    """Selects a random word from a given text file.
    The input file should have one word per line.

    Keyword arguments:
    filename -- a text file containing one word per line (a-z chars only)
    """
    file = open(filename, "r")
    word_list = file.read().splitlines()
    file.close()
    return word_list[random.randrange(0, len(word_list))
    ]


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
    msg = msg + "\n"
    conn.sendall(msg.encode(encoding))


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


def run_game(conn, display):
    """Outputs the current display word to the player with unknown letters shown as '_'.
     Loops until the player guesses the word or has guessed every letter.
    Keyword arguments:
    conn -- a socket connection
    display -- the array of masked characters representing the game word being displayed to the user
    """
    while "_" in display:
        send_msg(arr_to_str(display), conn)
        #try:
        data = conn.recv(MSGLEN)
        #except socket.error as err:
         #   print("Connection from user lost.\n", err)
          #  close_conn(conn)
           # break
        guess = data.decode(encoding)
        if len(guess) > 1:
            display = word_guess(guess, display)
        else:
            letter_guess(guess, display)


def end_game(conn):
    """Output appropriate messages to signal the end of the game.
    Keyword arguments:
    conn -- a socket connection
    """
    send_msg(calc_score(), conn)
    send_msg("GAME OVER", conn)
    print("Game ended.\n")


def play_hangman(s):
    """Creates a socket for a single-user and manages the game state.
    Keyword arguments:
    s -- a server socket which will connect to a player
    """
    conn, addr = s.accept()
    with conn:
        letters = []
        data = conn.recv(MSGLEN)
        if not data.decode(encoding) == 'START GAME':
            close_conn(s)
        else:
            setup_game(addr, letters)
            try:
                run_game(conn, letters)
                end_game(conn)
            except socket.error as err:
                print("Connection to user lost.\n", err)
                close_conn(s)
                return
    close_conn(s)


if __name__ == "__main__":
    while True:
        s = create_socket()
        word = create_word_list("wordList.txt")
        guesses, word_guesses = [], []
        char_guesses_count, word_guesses_count = 0, 0
        try:
            play_hangman(s)
        except socket.error as err:
            print("Unable to create the socket on " + str(HOST) + ":" + str(PORT) + "\n" + str(err))
        except KeyboardInterrupt:
            print("\nServer process terminated by user.")
            close_conn(s)
            break
