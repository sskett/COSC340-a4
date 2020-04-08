#!/usr/bin/env python3

def letter_guess(guess):
    for i in range(0, len(display)):
        if guess == word[i]:
            display[i] = guess
            print(display)

def word_guess(guess):
    i = 0
    for c in guess:
        if c == word[i]:
            i += 1
        else:
            break
    if i == len(word):
        print("You guessed correct!")
        return word
    else:
        print("Sorry. Try again")

WORD_LIST = [
    "apple",
    "hello",
    "laminate",
    "sorceror",
    "willow"
]
display = []
print("Hello player.\n")
seed = int(input("Pick a number: "))
word = WORD_LIST[seed % len(WORD_LIST)]

for c in word:
    display.append("_")

print("START GAME")
print(display)

guesses = []


while "_" in display:
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




