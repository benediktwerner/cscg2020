# Maze - Map Radar

For this challenge, we need to trace the path of a player that walks in a weird pattern.

I already explained how the client and server communicate in my `Maze - Emoji` writeup.

There are two kinds of messages that are relevant to this challenge:
1. **Info responses**: The client can ask the server for information about a player to which
the server will respond with this response. These messages start with the letter `I`.
They then contain the players `uid` (4 bytes), his unlocks (2 bytes), and his name (1 byte for the length and then the name).
2. **Position updates**: The server periodically sends these messages to the clients to tell them that a player moved and
where he is now. These messages start with the letter `P` and then contain the players `uid` (4 bytes), the time of the update
(8 bytes), the players x, y, and z coordinates (3x4 bytes), the direction the player is facing (3x4 bytes), and some more stuff that isn't relevant for this challenge.

We can now write a proxy to intercept the communication between the server and client
and look for these messages.

The server will send an info response for the player "The White Rabbit" which will tell us the `uid`
we need to look out for.

We can then look for position updates from this player and trace his path.

My complete proxy code is attached although it also contains code
for all the other `Maze` challenges.

To intercept the communication between the client and server I simply changed `%WINDIR%\System32\drivers\etc\hosts` and added this:
```
127.0.0.1			maze.liveoverflow.com
```

The same can be done on Linux by modifying the `/etc/hosts` file.

This redirects all traffic to `maze.liveoverflow.com` to the local machine.

We can now listen for the api requests on port 80 and tell the game that it should connect to
localhost on some port.

We can then again listen to that connection and forward everything to the server.

If we then receive anything from the server we can also send it back to the client.

Because we changed `maze.liveoverflow.com` to point to localhost we can't use that
address to reach the server but we can simply reach the server by addressing
it directly by its IP or we can just send the traffic to `hax1.allesctf.net` which has the same IP.

After we collected the position updates for some time we can then draw it.

I just used Python's built-in `turtle` module to do this:

```python
from turtle import *

cords = []

with open("radar.txt") as f:
    for line in f:
        x, z = map(float, line.split(" "))
        cords.append((x, z))


tracer(False)
speed(0)
hideturtle()

penup()
goto(*cords[0])
pendown()

for x, y in cords:
    goto(x, y)

done()
```

And from the drawing we can then read the flag: `CSCG{RADAR_HACK_XYZ}`

Next: [Maze - Tower](maze_tower.md)
