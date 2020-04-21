#!/usr/bin/env python3

import sys
import socket
import random


HOST = 'localhost'
PORT = int(sys.argv[1])
MAX_CONNS = 1
encoding = 'ascii'

result = []

guesses = []
word_guesses = []
char_count = 0
word_count = 0


def create_word_list(filename):
    file = open(filename, "r")
    word_list = file.read().splitlines()
    file.close()
    return word_list[random.randrange(0, len(word_list))
    ]


def close_conn(s):
    s.shutdown(socket.SHUT_RDWR)
    s.close()


def letter_guess(guess,display):
    global char_count
    char_count += 1
    if guess in guesses:
        return
    else:
        guesses.append(guess)
        for i in range(0, len(display)):
            if guess == word[i]:
                display[i] = guess


def word_guess(guess, display):
    global word_count
    word_count += 1
    if guess in word_guesses:
        return display
    else:
        i = 0
        for c in guess:
            if c == word[i]:
                i += 1
            else:
                break
        if i == len(word):
            return word
        else:
            return display


def send_msg(msg, conn):
    msg = msg + "\n"
    conn.sendall(msg.encode(encoding))


def arr_to_str(arr):
    to_string = ""
    for c in arr:
        to_string += c
    return to_string


def play_hangman(display):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(MAX_CONNS)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if not data.decode(encoding) == 'START GAME':
                send_msg("Invalid start request. Disconnecting...", conn)
                close_conn(s)
            else:
                print("Starting game. Connected with:", addr)
                send_msg("Let's play Hangman!", conn)
                for c in word:
                    display.append("_")
                print("The word is:", word)
                while "_" in display:
                    send_msg(arr_to_str(display), conn)
                    data = conn.recv(1024)
                    if not data:
                        break
                    guess = data.decode(encoding)
                    if len(guess) > 1:
                        display = word_guess(guess, display)
                    else:
                        letter_guess(guess, display)
                send_msg("You got it!\nThe word was " + word, conn)
                score = 10 * len(word) - 2 * char_count - word_count
                send_msg("Your score is: " + str(score), conn)
                send_msg("GAME OVER", conn)
                print("Game ended.\n")
        close_conn(s)


if __name__ == "__main__":
    try:
        word = create_word_list("wordList.txt")
        play_hangman(result)
    except socket.error as err:
        print("Unable to create the socket on " + str(HOST) + ":" + str(PORT) + "\n" + str(err))