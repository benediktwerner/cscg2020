# Maze - The Floor Is Lava

For this challenge, we need to reach a chest surrounded by lava which kills us if we touch it.

I already explained how the game client and server communicate in my writeup
for `Maze - Emoji`, how we can intercept that communication
in my writeup for `Maze - Map Radar` and how we can teleport in my writeup for `Maze - Tower`.

For this challenge, the only change we need to make is to tell the server
we are slightly up in the air. We can just intercept all the position updates
from the client and modify them a bit so that we are always 4 units up in the air.

In my proxy script, this can be achieved by entering the `fly on` command.

We can then simply walk over the lava since the client doesn't know that it should
kill us and the server thinks we are flying above the lava.

We can then use the teleport functionality from `Maze - Tower` to teleport onto the
isle and turn flying off again to get the flag: `CSCG{FLYHAX_TOO_CLOSE_TO_THE_SUN!}`
