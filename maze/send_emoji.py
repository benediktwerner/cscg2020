#!/usr/bin/env python3

import socket
from random import randrange
from hashlib import sha256
from sys import argv

PASSWORD = b"U4XB90SSKRKQ5CIV"


def encode(data):
    result = bytearray(len(data) + 2)
    rand1 = result[0] = randrange(256)
    rand2 = result[1] = randrange(256)
    for i, c in enumerate(data):
        result[i + 2] = rand1 ^ c
        rand1 = (rand1 + rand2) % 0xFF
    return result

secret = sha256(PASSWORD).digest()[:8]
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(encode(b"E" + secret + bytes([int(argv[2])])), ("hax1.allesctf.net", int(argv[1])))
