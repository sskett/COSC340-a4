#!/usr/bin/env python3

import sys
import socket
import random


HOST = 'localhost'
PORT = int(sys.argv[1])
MAX_CONNS = 1
encoding = 'ascii'

WORD_LIST = [
    "apple",
    "hello",
    "laminate",
    "sorceror",
    "willow"
]

result = []
word = WORD_LIST[random.randrange(0, len(WORD_LIST))]
guesses = []
word_guesses = []
char_count = 0
word_count = 0


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


def play_hangman(display):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(MAX_CONNS)
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024)
            if not data.decode(encoding) == 'START GAME':
                send_msg("Invalid start request. Disconnecting...", conn)
                s.close()
            else:
                print("Starting game on port", PORT)
                send_msg("Let's play Hangman!", conn)
                for c in word:
                    display.append("_")
                print("The word is:", word)
                while "_" in display:
                    send_msg(str(display), conn)
                    data = conn.recv(1024)
                    if not data:
                        break
                    guess = data.decode(encoding)
                    if 1 < len(guess) <= len(word):
                        display = word_guess(guess, display)
                    else:
                        letter_guess(guess, display)
                send_msg("You got it!\nThe word was " + word, conn)
                score = 10 * len(word) - 2 * char_count - word_count
                send_msg("Your score is: " + str(score), conn)
                send_msg("GAME OVER", conn)
                print("Game ended.\n")
                s.shutdown(socket.SHUT_RDWR)
        s.close()





"""



    guess = input("What is your guess: ")
    if (len(guess) > 1 and len(guess) <= len(word)):
        guesses.append(guess)
        display = word_guess(guess)
    else:
        guesses.append(guess)
        letter_guess(guess)


print("You got it!\n")
print("Your guesses were:\n")
print(guesses)
"""

if __name__ == "__main__":
    try:
        play_hangman(result)
    except socket.error as err:
        print("Unable to create the socket on " + str(HOST) + ":" + str(PORT) + "\n" + str(err))