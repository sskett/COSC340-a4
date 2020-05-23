#COSC340 (2020/T1) - Assignment 2
##Spencer Skett

####ZIP file contents
- readme.md
- startServer.sh
- startClient.sh
- server.py
- client.py
- wordList.txt

####Server instructions
**The startServer.sh, server.py and wordList.txt files should be in a common directory.**

The game server is started by running "./startServer.sh [PORT]" in the terminal.

The server will run until it is force terminated by a system exit (generally a keyboard interrupt, CTRL+C, by the user)
or a fatal program error.

Data and communication errors will disconnect the current user and leave the server in a listening state ready to start 
a new game.

####Client instructions
**The startClient.sh and client.py files must be in the same directory.**

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

#####SSL 
SSL connection method based on:
 
* https://www.electricmonk.nl/log/2018/06/02/ssl-tls-client-certificate-verification-with-python-v3-4-sslcontext/

* https://docs.python.org/3/library/ssl.html

* https://markusholtermann.eu/2016/09/ssl-all-the-things-in-python/

Regenerating keys (not implemented)
* https://medium.com/@md.julfikar.mahmud/secure-socket-programming-in-python-d37b93233c69

AES encryption:

* https://stackoverflow.com/questions/27287306/sending-encrypted-strings-using-socket-in-python
