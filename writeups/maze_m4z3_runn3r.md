# Maze - M4z3 Runn3r

For this challenge, we need to race through the maze in a certain amount of time,
similar to the `Maze - Maze Runner` challenge.

However, this time we can't take longer than 5 seconds to complete the whole race.

To do this we can use the same method as I described in my writeup for `Maze Runner`
but we need to somehow circumvent the limit of one 10 unit teleport per second.

To do this we can simply adjust the time we send with the position updates
for the teleport.

If the client sends a position update the server only checks if the time given in the last position
update from the client is at least one second ago from the time given in the new update
but it doesn't check if a second has actually passed since then.

This means we can simply increase the time by one additional second for every teleport
to teleport as fast as we want.

Since we already intercept all the packages from the client to the server
we can simply keep track of the total time offset from the real-time
and add this to every package sent from the client in addition to
increasing it on every teleport.

This way we can now easily complete the maze in under 5 seconds and get the flag: `CSCG{N3VER_TRUST_T1111ME}`
