# Intro to Crypto 1

For this challenge, we get two files: A text file `message.txt` containing a single large number and a file `pubkey.pem` containing a public RSA key.

Using `openssl` we can see the details of the key:

```
$ openssl rsa -pubin -in pubkey.pem -text -noout
Public-Key: (2047 bit)
Modulus:
    51:cf:f4:6d:9e:e3:20:96:d6:c8:06:cb:c7:df:2d:
    1d:3b:ea:7e:7b:2f:c4:e8:26:d9:fc:5e:18:79:99:
    12:dc:a1:50:b2:9c:65:c0:f9:e6:64:53:39:6c:e7:
    de:63:1a:0f:9a:67:45:13:8b:61:25:bb:cd:18:5a:
    a1:2e:b0:9a:4a:1b:d8:06:11:8c:97:a8:de:05:ed:
    0b:e6:b4:5f:c1:c9:e9:93:71:92:f5:8b:c4:a5:cc:
    27:67:80:3c:0b:21:34:2a:f5:cb:8f:34:af:fb:1a:
    6e:c2:52:0c:76:5d:87:52:1c:68:48:db:d8:31:81:
    2e:cc:6d:8b:b3:d6:17:33:b0:eb:c3:52:cf:64:d4:
    44:5c:99:55:72:92:2f:49:3d:71:89:95:9d:b2:32:
    1e:1b:ac:59:25:fa:56:dc:69:f6:85:8e:fe:eb:a0:
    a5:a9:d7:6b:a1:98:18:71:53:92:74:24:e5:f7:b6:
    80:98:ab:8c:10:44:2b:73:d1:49:02:7c:fc:37:d0:
    30:05:63:37:c3:e0:f4:21:6c:f4:32:23:96:74:41:
    b6:08:ee:c2:a6:48:e8:ce:85:78:94:c6:65:03:0c:
    01:24:56:29:27:9b:38:7f:cd:bd:c3:5b:61:67:71:
    5b:54:bd:55:56:18:0d:9a:f2:50:4b:52:7a:90:fa:
    e7
Exponent: 65537 (0x10001)
```

In RSA the public key consists of a modulus `N` and an exponent `e` which can both be seen above.

The modulus `N` is a product of two primes `p` and `q` and if we can find out what those primes are we can reconstruct
the private key and decrypt the message.

Since the challenge description promises us that the key was generated using HUGE primes let's see if that is true.

Using Python we can just try some numbers and see if they divide `N`:

```python
import itertools
from Cryptodome.PublicKey import RSA

with open("pubkey.pem") as f:
    key = RSA.import_key(f.read())

for p in itertools.count(2):
    if key.n % p == 0:
        print("p =", p)
        break
```

And we quickly get a result: `p = 622751`.

Using this we can also calculate `q`:

```python
q = key.n // p
```

`q` is indeed a very large prime but this means `p` is small and easy to find.

We can now calculate `phi(N)` and `d` according to the [RSA description](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) and decrypt the message:

```python
phi = (p - 1) * (q - 1)
d = pow(key.e, -1, phi)  # pow(.., -1, ..) requires Python 3.8

with open("message.txt") as f:
    c = int(f.readline())

m = pow(c, d, key.n)

print(bytes.fromhex(hex(m)[2:]).decode())
```

This gives us the flag: `CSCG{factorizing_the_key=pr0f1t}`
