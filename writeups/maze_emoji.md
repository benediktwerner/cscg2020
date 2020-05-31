# Maze - Emoji

For this challenge, we apparently need to use a secret emoji.

Let's first analyze how communication with the game server works.

Using Wrieshark we can see some `HTTP`-requests to `maze.liveoverflow.com` and their responses:

```
/api/health         yes
/api/welcome        Maze - hotfix v2.1 available to download now
/api/hostname       maze.liveoverflow.com
/api/ratelimit      20
/api/min_port       1337
/api/max_port       1357
/api/login_queue    0
```

After that, we can see some `UDP` traffic to port `1340`.

It looks like the game selects a random port between `min_port` and `max_port`
and all communication is then done via UDP on that port.
However, the data doesn't look meaningful and is changing a lot
so it probably is encrypted or at least encoded in some way.

Because the LiveOverflow used `il2cpp` to compile
the game code to `C++` we can't reverse the code as easily
but luckily there is a tool called `Il2CppDumper` that can somewhat reverse this process.

The tool recovers a lot of type information and function names
and generates a file that can then be imported into IDA using an IDAPytohn script.

With some reversing we can find out that all data that is sent to or from the server
is encoded using code like this:

```python
def encode(data):
    result = bytearray(len(data) + 2)
    rand1 = result[0] = randrange(256)
    rand2 = result[1] = randrange(256)
    for i, c in enumerate(data):
        result[i + 2] = rand1 ^ c
        rand1 = (rand1 + rand2) % 0xFF
    return result
```

We can easily reverse this process with code like this:

```python
def decode(data):
    result = bytearray(len(data) - 2)
    rand1 = data[0]
    rand2 = data[1]
    for i, c in enumerate(data[2:]):
        result[i] = rand1 ^ c
        rand1 = (rand1 + rand2) % 0xFF
    return result
```

With some more work, we can also fairly easily reverse the protocol used for communication.

The messages always start with one or two letters identifying the type of the message
and then the message content depending on the type.

All the messages sent by the client also start with a secret that is just
the first 8 bytes of the SHA256 hash of the user's password.

Emoji messages start with the letter `E`, then the secret and then
one byte identifying the emoji to show.

We can now just send our own messages with different emoji values to the server using a script like this:

```python
import socket
from random import randrange
from hashlib import sha256
from sys import argv

PASSWORD = b"XXX"

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
sock.sendto(encode(b"E" + secret + bytes([int(argv[2])])), ("maze.liveoverflow.com", int(argv[1])))
```

This script takes the port and the emoji value as command-line arguments.

The game helpfully tells us the port it connects to in the top right corner.

After trying a few different emoji values we finally get the flag when sending the emoji number 13: `CSCG{Your_hack_got_reported_to_authorities!}`
