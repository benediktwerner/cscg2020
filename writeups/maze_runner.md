# Maze - Maze Runner

For this challenge, we need to race through the maze in a certain amount of time.

There are a number of checkpoints that we need to touch in order to complete
the challenge and we can never take more than 15 seconds to reach the next checkpoint.

Using the normal game controls this is impossible since the paths between
some of the checkpoints are too long. However, we can use the teleportation functionality
that I explained in my writeup about `Maze - Tower` to complete the maze much quicker.

The first step is to collect a list of positions that
we want to teleport to, to complete the race.

To make this step easier I added an option to the proxy that
sends a "checkpoint reached" message to the client every
time it receives a heartbeat message from the server.

This can be enabled by typing `checkpoint on` into the proxy script window.

This way the client never thinks the race is over and continuously shows the checkpoint positions.

We can then walk around the maze and use the `pos` command from the proxy to print the current position.

The proxy always stores the position from the last update the client sent to the server
and this command just prints this position.

With this, we can now plan a path through the maze by noting down waypoints that the player should
teleport to.
Since the walls of the maze are fairly thin we can also teleport through them at some positions to save some time.

When using the `race` command the proxy now blocks all position
updates from the client to the server and then continuously
teleports the player to the next waypoint by sending a position
update to both the client and server. To prevent the server
from denying the update it also waits 1 second between
each teleport and if the distance between
two waypoints are larger than 10 units it teleports multiple times.

This method should now be fast enough to complete the challenge and get the flag: `CSCG{SPEEDH4X_MAZE_RUNNER_BUNNYYYY}`

The proxy code attached already contains code to solve the `M4z3 Runn3r` challenge
which circumvents the need to wait 1 second between teleports.
