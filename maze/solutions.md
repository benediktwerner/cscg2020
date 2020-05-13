## Emoji

Use CheatEngine to overwrite emoji in ServerManager.sendEmoji

- 1: angry
- 3: sunglasses
- 4: crying
- 5: large eyes smiling
- 6: devil laughing
- 7: -_-
- 8: hearty eyes
- 12: Flag

Flag: `CSCG{Your_hack_got_reported_to_authorities!}`


## Radar Hack

```python
white_rabbit_uid = None
radar_file = open("radar.txt", "w")

def server_info():
    if name == "The White Rabbit":
        global white_rabbit_uid
        white_rabbit_uid = uid

def serfer_position():
    if uid == white_rabbit_uid:
        print(x, z, file=radar_file, flush=True)
```

Flag: `CSCG{RADAR_HACK_XYZ}`


## Maze Runner

Send the client checkpoint packages to see all checkpoints.
Send the server fake position packets to teleport and be fast enough (also teleport through walls).
Limit: 10 units/s and not far outside walls

Flag: `CSCG{SPEEDH4X_MAZE_RUNNER_BUNNYYYY}`


## Tower

Teleport hack to move through gate. Upwards teleport to walk over walls and teleport up the tower.

Flag: `CSCG{SOLVED_THE_MAZE...LONG_WAY_BACK!}`


## The Floor is Lava

Continously y = 4 to server to avoid lava

Flag: `CSCG{FLYHAX_TOO_CLOSE_TO_THE_SUN!}`


## M4z3 Runn3r

Flag: `CSCG{N3VER_TRUST_T1111ME}`

When teleporting: increase time
