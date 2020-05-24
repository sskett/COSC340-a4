#COSC340 (2020/T1) - Assignment 4
##Spencer Skett

####ZIP file contents
- readme.md
- protocol.pdf
- report.pdf
- startServer.sh
- startClient.sh
- server.py
- client.py
- game_sec.py
- server.crt
- server.key
- client.crt
- client.key
- wordList.txt

####Server instructions
**The startServer.sh, server.py, game_sec.py, server.crt, server.key, client.crt and wordList.txt files must 
be in a common directory.**

The game server is started by running "./startServer.sh [PORT]" in the terminal.

The server will run until it is force terminated by a system exit (generally a keyboard interrupt, CTRL+C, by the user)
or a fatal program error. If a game is currently running the interrupt will exit the game and return to the listening
state. A further interrupt is required to close the server.

Data and communication errors will disconnect the current user and leave the server in a listening state ready to start 
a new game.

####Client instructions
**The startClient.sh, client.py, game_sec.py, server.crt, client.crt and client.key files must be in the same directory.**

The game is started by running "./startClient.sh [HOST] [PORT]" in the terminal.

The game will exit back to the terminal if any errors occur. The user can voluntarily leave the game by pressing CTRL+C.

On successful connection the game server a series of dashes will be displayed, with each dash representing one letter of
the word to be guessed. eg for the word 'hello' the user's display will initiate with '_ _ _ _ _'.

The user can either guess one letter or attempt to guess the whole word. The display will update with any correctly guessed
letters, eg guessing 'l' in the previous example would update the display to '_ _ l l _'. The display will not change if
a letter or word guess is incorrect.

Once the final letter is guessed, or the whole word is guessed correctly, the game will display your score and then exit.
Scoring is based on the length of the word and how many guesses you took to solve it. You will score higher if you use
word guesses rather than guessing every letter.

####Security
The connection between server and client is negotiated over TLS using the included self-signed certificates.

All communications between server and client are sent using AES encryption. Each message is checked against a digital
signature using a hash-based message authentication code (HMAC). The client performs a hash-value check on the game word
to ensure the server has operated on the correct word. 

