#!/usr/bin/env python3

import sys
import socket


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
word = WORD_LIST[1]


def letter_guess(guess,display):
    for i in range(0, len(display)):
        if guess == word[i]:
            display[i] = guess
            print(display)


def word_guess(guess, display):
    i = 0
    for c in guess:
        if c == word[i]:
            i += 1
        else:
            break
    if i == len(word):
        print("They got it!")
        return word
    else:
        return display


def send_msg(msg, conn):
    conn.sendall(msg.encode(encoding))


def play_hangman(display):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(MAX_CONNS)
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = conn.recv(1024)
            if not data.decode(encoding) == 'START GAME':
                send_msg("Invalid start request. Disconnecting...\n", conn)
                conn.sendall(msg.encode(encoding))
                s.close()
            else:
                print("Starting game")
                send_msg("Let's play Hangman!\n", conn)
                for c in word:
                    display.append("_")
                print("The word is:", word)
                guesses = []
                while "_" in display:
                    remaining = str(display) + "\n"
                    print("Guesses used: " + str(len(guesses)))
                    send_msg(remaining, conn)
                    data = conn.recv(1024)
                    if not data:
                        break
                    guess = data.decode(encoding)
                    print("This guess:", guess)
                    if 1 < len(guess) <= len(word):
                        guesses.append(guess)
                        display = word_guess(guess, display)
                    else:
                        guesses.append(guess)
                        letter_guess(guess, display)
                send_msg("\nYou got it!\nThe word was '" + word + "'\n", conn)
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