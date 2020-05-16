#!/usr/bin/env python3

import itertools
from Cryptodome.PublicKey import RSA

with open("pubkey.pem") as f:
    key = RSA.import_key(f.read())

for p in itertools.count(2):
    if key.n % p == 0:
        break

q = key.n // p
phi = (p - 1) * (q - 1)
d = pow(key.e, -1, phi)  # pow(.., -1, ..) requires Python 3.8

with open("message.txt") as f:
    c = int(f.readline())

m = pow(c, d, key.n)

print(bytes.fromhex(hex(m)[2:]).decode())
