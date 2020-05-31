# Maze - Tower

For this challenge, we need to reach the top of the tower in the castle.

I already explained how the game and server communicate in my writeup
for `Maze - Emoji` and how we can intercept that communication
in my writeup for `Maze - Map Radar`.

For this challenge, we can abuse the fact that the server
doesn't check the position updates sent from the client too closely.

The only restriction is that the target position isn't in a wall and that
it isn't too far away from the previous position update.

The maximum allowed distance depends on the time since the last update
but it can never be bigger than 10 units which is allowed after at least
1 second has passed since the last update.

To solve this challenge we can simply add some code to the proxy
that allows us to send a position package to both the game and server
and tells them a position we want to teleport to.

For convenience, I added some code that listens for
emojis from the client and teleports the player
forward or upwards if the first or second emoji is sent.

This way we can just teleport up onto and through the walls to
get to the castle and then teleport onto the tower to get the flag: `CSCG{SOLVED_THE_MAZE...LONG_WAY_BACK!}`

For convenience during exploration, we can also add some
code that intercepts position updates from the client to the server
and just always sends the server the same position.

This way we can ignore the teleport limit and freely explore the map on the client.

This, of course, has no impact on the server so we can't use this to get the flag
but it makes it much easier to explore the map and find the castle.
