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
