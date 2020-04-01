#!/usr/bin/env python3

from Cryptodome.Util.number import inverse, long_to_bytes
import itertools

e = 65537
N =  int("""
    57:c8:8f:1c:9b:9e:d4:7d:84:4f:87:b2:9f:44:79:
    6e:17:ce:47:c2:fe:24:cc:1a:b7:e3:44:32:b3:35:
    21:24:63:d2:39:9d:07:47:11:80:05:72:ea:68:12:
    e2:90:12:02:bc:5f:19:0c:cb:49:66:d5:70:90:4a:
    41:69:7a:63:64:48:8a:e1:40:b1:b6:35:7f:c6:a6:
    b4:ac:cd:51:7a:74:03:bb:c9:96:df:d0:72:89:5f:
    6a:9a:1e:a8:f2:a6:da:b6:9d:a1:55:75:17:7f:4c:
    ef:1a:db:90:82:5b:bd:4f:ec:50:01:aa:c0:1a:70:
    e8:a1:0e:10:13:34:71:39:32:be:47:d1:a0:9d:70:
    d3:11:57:fe:26:e5:53:77:4f:8d:9e:50:20:98:47:
    2b:ca:87:07:93:1e:2b:c9:cb:92:aa:c9:44:51:be:
    6f:1e:55:8b:93:a8:68:5c:e9:84:f4:84:0a:fa:f8:
    d2:a8:ad:0d:46:54:54:62:a9:18:15:1a:50:de:a1:
    a2:8f:4d:f1:e5:e6:99:b0:05:2d:a5:23:05:9e:b2:
    1d:56:b6:7c:91:e5:6a:b7:5f:35:bc:9f:64:9b:ea:
    76:a1:36:b1:70:d3:a6:76:f5:14:b9:c8:95:5e:af:
    78:a9:0b:ad:d5:48:5b:ba:7f:12:17:8b:1f:8f:ef:
    ef
""".replace("\n", "").replace(":", "").replace(" ", ""), 16)

def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

for p in itertools.count(isqrt(N), -1):
    if N % p == 0:
        break

q = N // p
phi = (p - 1) * (q - 1)
d = inverse(e, phi)

with open("message.txt") as f:
    c = int(f.readline())

m = pow(c, d, N)

print(long_to_bytes(m).decode())
