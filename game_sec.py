"""
These are the game security functions for the word guessing game required for COSC340 Assignment 4.
"""

import hmac, hashlib
from Crypto.Cipher import AES
from Crypto import Random


def encrypt16(msg, key, enc_type='ascii'):
    """Encrypts a message using AES. A random IV value is used for each message to ensure similar messages do not have
    repeating patterns in their ciphertext form and to offset the use of padding characters as necessary for the CBC
    encryption mode.
    Keyword arguments:
    msg -- a message to be encrypted, will be padded to have length as a multiple of 16 bytes
    key -- a key to use for the encryption
    enc_type -- an encoding type to convert strings to byte-form. This defaults to 'ascii'.
    """

    # Create a random IV
    iv = Random.new().read(16)

    # Create the HMAC signature for the plaintext message
    hsig = hmac_signature(msg.encode(enc_type), iv)

    # Pad the message to a required length and encrypt
    while len(msg) % 16 != 0:
        msg = msg + "^"
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Combine the random IV, HMAC signature and encrypted message into one block of ciphertext
    ciphertext = iv + hsig + cipher.encrypt(msg)

    return ciphertext


def decrypt16(msg, key, enc_type='ascii'):
    """Decrypts a message encrypted using AES and checks the HMAC signature for message validity.
     Keyword arguments:
     msg -- the message to be decrypted
     key -- a key to use for the decryption
     enc_type -- an encoding type to convert strings to byte-form and vice-versa. This defaults to 'ascii'.
     """

    # Extract the randomised IV
    iv = msg[:16]

    # Extract the HMAC signature
    signature = msg[16:80].decode(enc_type)

    # Decrypt the actual message and remove padding
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(msg[80:]).decode(enc_type)
    if plaintext.endswith('^'):
        while plaintext.endswith('^'):
            plaintext = plaintext[:-1]

    # Check the HMAC signature for the calculated plaintext matches the one received
    h = hmac_signature(plaintext.encode(enc_type), iv).decode(enc_type)
    if not h == signature:
        print('HMAC failure. Disconnecting from user.')
        return ""

    return plaintext


def hmac_signature(msg, key, enc_type='ascii'):
    """Calculates a SHA3-256 based HMAC value.
    Keyword arguments:
     msg -- the message to sign
     key -- a key to use for the signature
     enc_type -- an encoding type to convert strings to byte-form and vice-versa. This defaults to 'ascii'.
    """

    h = hmac.new(key, msg, hashlib.sha3_256)

    # Return the HMAC object in an appropriately readable and usable format
    return h.hexdigest().encode(enc_type)