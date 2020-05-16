#!/usr/bin/env python3

import itertools
from Cryptodome.Util.number import inverse, long_to_bytes
from Cryptodome.PublicKey import RSA


def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


with open("pubkey.pem") as f:
    key = RSA.import_key(f.read())

for p in itertools.count(isqrt(key.n), -1):
    if key.n % p == 0:
        break

q = key.n // p
phi = (p - 1) * (q - 1)
d = inverse(key.e, phi)

with open("message.txt") as f:
    c = int(f.readline())

m = pow(c, d, key.n)

print(long_to_bytes(m).decode())
