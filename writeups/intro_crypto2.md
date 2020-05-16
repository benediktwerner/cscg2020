# Intro to Crypto 2

For this challenge, we again get two files: A text file `message.txt` containing a single large number and a file `pubkey.pem` containing a public RSA key.

This time the description promises us that "now p and q are huge".

This sounds dangerous again. If `p` and `q` are very similar in size they
must be very close to the square root of `N`.

Since `N` is so large we need to be careful when calculating the square root.

Using `math.sqrt(N)` or `N**0.5` in Python will return a float that doesn't have nearly enough precision.

Since we don't actually need any decimals but certainly need precision for all integer digits we can use a function like
this to calculate the integer square root of a number:

```ptyhon
def isqrt(n):
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x
```

We can now try to factor `N` using some numbers near its square root:

```python
import itertools
from Cryptodome.Util.number import inverse, long_to_bytes
from Cryptodome.PublicKey import RSA

with open("pubkey.pem") as f:
    key = RSA.import_key(f.read())

for p in itertools.count(isqrt(key.n), -1):
    if key.n % p == 0:
        break
```

And indeed we quickly get a result.

We can now again calculate `q`, `phi(N)` and `d` according to the [RSA description](https://en.wikipedia.org/wiki/RSA_(cryptosystem)#Decryption) and decrypt the message:

```python
q = key.n // p
phi = (p - 1) * (q - 1)
d = inverse(key.e, phi)

with open("message.txt") as f:
    c = int(f.readline())

m = pow(c, d, key.n)

print(long_to_bytes(m).decode())
```

This will give us the flag: `CSCG{Ok,_next_time_I_choose_p_and_q_random...}`

Choosing `p` and `q` at random really sounds like a good idea.
