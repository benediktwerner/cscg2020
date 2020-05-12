import struct, math, time as pytime

from .utils import *

HIDE_CLIENT_HEARTBEAT = True
HIDE_CLIENT_POSITION = True
HIDE_CLIENT_INFO = True

HIDE_SERVER_HEARTBEAT = True
HIDE_SERVER_POSITION = True
HIDE_SERVER_INFO = True

last_pos = None
last_secret = None
last_time = None
start_time = None
block_movement = False
g2p = None
last_cmd = None
checkpoint = None
last_checkpoint_time = 0
abort_teleport = False
lock_position = False
locked_position = None
lock_y = False


def decrypt(data):
    result = bytearray(len(data) - 2)
    rand1 = data[0]
    rand2 = data[1]
    for i, c in enumerate(data[2:]):
        result[i] = rand1 ^ c
        rand1 = (rand1 + rand2) % 0xFF
    return result


def encrypt(data):
    return b"\0\0" + data


def dist(a, b):
    x1, y1, z1 = a
    x2, y2, z2 = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5


def add(a, b):

    x1, y1, z1 = a
    x2, y2, z2 = b
    return (x1 + x2, y1 + y2, z1 + z2)


def diff(a, b):
    x1, y1, z1 = a
    x2, y2, z2 = b
    return (x1 - x2, y1 - y2, z1 - z2)


def scalar_mul(v, s):
    x, y, z = v
    return (x * s, y * s, z * s)


def norm(v):
    d = dist(v, (0, 0, 0))
    return scalar_mul(v, 1 / d)


def print_client(*args):
    printc(GREEN, "[client]", *args)


def print_server(*args):
    printc(RED, " [server]", *args)


def parse_secret(data):
    global last_secret
    secret = data[:8]
    if secret != last_secret:
        if last_secret is not None:
            last_secret = last_secret.hex()
        print_client("Secret changed from", last_secret, "to", secret.hex())
    last_secret = secret
    return secret, data[8:]


def parse_time(data):
    global last_time, start_time

    time = struct.unpack("Q", data[:8])[0] / 10_000
    last_time = time
    start_time = pytime.time() - last_time

    return time, data[8:]


def parse_login(data):
    secret, data = parse_secret(data)
    name_length = data[0]
    name = data[1 : 1 + name_length].decode()
    print_client("Login request:", secret.hex(), name)


def parse_heartbeat(data):
    assert data[0] == ord("3"), "invalid 2nd byte in heart beat request"
    secret, data = parse_secret(data[1:])
    time, data = parse_time(data)
    if HIDE_CLIENT_HEARTBEAT:
        return
    print_client(f"Heartbeat at {time: 5.2f}")


def parse_position(data):
    global last_pos, locked_position

    orig = data
    secret, data = parse_secret(data)
    time, data = parse_time(data)
    x, y, z, ax, ay, az = map(lambda x: x / 10_000, struct.unpack("iiiiii", data[:24]))
    last_pos = (x, y, z, ax, ay, az)
    trigger = data[24]
    grounded, not_grounded = struct.unpack("hh", data[25:])

    if not HIDE_CLIENT_POSITION:
        print_client(
            f"Position at {time: 5.2f}",
            "=",
            f"{x},{y},{z}",
            f"{ax},{ay},{az}",
            trigger,
            grounded,
            not_grounded,
        )

    if block_movement:
        return False

    if lock_position:
        if locked_position is None:
            locked_position = data[:24]
        else:
            return b"P" + orig[:16] + locked_position + data[24:]

    if lock_y:
        return b"P" + orig[:20] + struct.pack("i", 40_000) + orig[24:]



def parse_info_request(data):
    secret, data = parse_secret(data)
    uid = struct.unpack("I", data)[0]

    if HIDE_CLIENT_INFO:
        return

    print_client("Info request about", uid)


def parse_emoji(data):
    secret, data = parse_secret(data)
    index = data[0]
    print_client("Emoji", index)

    if index == 23:
        x, y, z, _, angle, _ = last_pos
        angle = math.radians(angle)
        xd = math.sin(angle) * 9
        zd = math.cos(angle) * 9
        tp(x + xd, y + 0.5, z + zd)
        return False
    elif index == 22:
        x, y, z, *_ = last_pos
        tp(x, y + 10, z)
        return False


client_handlers = {
    ord("L"): parse_login,
    ord("<"): parse_heartbeat,
    ord("P"): parse_position,
    ord("I"): parse_info_request,
    ord("E"): parse_emoji,
}


def parse_client(data):
    data = decrypt(data)
    pkttype = data[0]
    if pkttype in client_handlers:
        return client_handlers[pkttype](data[1:])
    else:
        print_client(f"Unknown packet '{chr(pkttype)}' ({pkttype}):", data.hex())


def server_heartbeat(data):
    assert data[0] == ord("3")
    time, server_time = struct.unpack("QQ", data[1:])
    time /= 10_000

    global last_checkpoint_time
    if checkpoint is not None and pytime.time() - last_checkpoint_time > 5:
        last_checkpoint_time = pytime.time()
        g2p.game.send(encrypt(b"R" + bytes([checkpoint])))

    if HIDE_SERVER_HEARTBEAT:
        return

    print_server(f"Heartbeat at {time: 5.2f}, {server_time}")


def server_login(data):
    uid, unlocks, version = struct.unpack("IHB", data)
    print_server(f"Login response: {uid=} {unlocks=} {version=}")


def server_info(data):
    uid, unlocks, name_length = struct.unpack("IHB", data[:7])
    name = data[7:].decode()

    if HIDE_SERVER_INFO:
        return

    print_server(f"Info reponse about {uid}: {name=} {unlocks=}")


def server_emoji(data):
    uid, emoji_time, emoji = struct.unpack("IIB", data)
    print_server(f"Emoji {emoji} from {uid} at {emoji_time}")


def server_position(data):
    if HIDE_SERVER_POSITION:
        return

    for i in range(0, len(data) - 40, 42):
        uid = struct.unpack("I", data[i : i + 4])[0]
        time = struct.unpack("Q", data[i + 4 : i + 12])[0]
        x, y, z, ax, ay, az = map(
            lambda x: x / 10_000, struct.unpack("iiiiii", data[i + 12 : i + 36])
        )
        trigger = data[36]
        grounded, not_grounded = map(
            lambda x: x / 100, struct.unpack("hh", data[i + 37 : i + 41])
        )
        print_server(
            f"Position of {uid} at {time}:",
            f"{x},{y},{z}",
            f"{ax},{ay},{az}",
            trigger,
            grounded,
            not_grounded,
        )


def server_teleport(data):
    instant = data[0]
    x, y, z = map(lambda x: x / 10_000, struct.unpack("iii", data[1:]))
    print_server(f"Teleport at {instant} to {x},{y},{z}")

    global abort_teleport
    abort_teleport = True


def server_unlock(data):
    unlocks = struct.unpack("H", data)[0]
    print_server("Got a new unlock:", unlocks)


server_handlers = {
    ord("<"): server_heartbeat,
    ord("L"): server_login,
    ord("I"): server_info,
    ord("E"): server_emoji,
    ord("P"): server_position,
    ord("T"): server_teleport,
    ord("R"): lambda data: print_server("Got race checkpoint", data[0]),
    ord("U"): server_unlock,
    ord("X"): lambda x: print_server("Recieved force logout"),
    ord("Y"): lambda x: print_server("Already logged in"),
    ord("D"): lambda x: print_server("You died"),
    ord("F"): lambda x: print_server("Block movement"),
    ord("C"): lambda data: print_server("Recieved flag:", data),
    ord(" "): lambda data: print_server("Message:", data),
}


def parse_server(data):
    data = decrypt(data)
    pkttype = data[0]
    if pkttype in server_handlers:
        return server_handlers[pkttype](data[1:])
    else:
        print_server(f"Unknown packet '{chr(pkttype)}' ({pkttype}):", data.hex())


def tp(*cords):
    print("Teleporting to", *cords)

    cords = map(lambda x: round(x * 10_000), cords)
    cords = struct.pack("iii", *cords)

    if not lock_position:
        data = b"P" + last_secret
        data += struct.pack("Q", round((pytime.time() - start_time) * 10_000))
        data += cords
        data += b"\0" * 17
        g2p.send_to_server(encrypt(data))

    g2p.game.send(encrypt(b"T\x01" + cords))


CHECKPOINTS = [
    (204, 0, 193),
    (180, 0, 180),
    (167, 0, 178),
    (168, 0, 198),
    (172, 0, 209),
    (186.7, 0, 233.4),
    (180.9493, 0, 227.8392),
    (184.8671, 0, 226.8441),
    (177.2907, 0, 227.3973),
    (167.2907, 0, 227.3973),
    (163.3865, 0, 230.7832),
    (159.3865, 0, 221.7832),
    (159.3865, 0, 211.7832),
    (156.6486, 0, 212.0267),
    (153.9269, 0, 203.0084),
    (152.2758, 0, 184.3855),
    (155.0973, 0, 164.5933),
    (175.9359, 0.0, 163.5304),
    (179.7533, 0.0, 159.3532),
    (177.1522, 0.0, 133.3842),
    (162.7332, 0.0, 117.5862),
    (147.1328, 0.0, 99.9839),
    (122.7027, 0.0, 99.2823),
    (116.0438, 0.0, 107.8459),
    (116.0665, 0.0, 122.708),
    (122.7653, 0.0, 125.3277),
    (125.7652, 0.0, 134.8275),
    (123.5945, 0.0, 137.3972),
    (123.5945, 0, 147.3972),
    (113.6882, 0, 191.3666),
    (108.2361, 0, 198.4183),
    (108.2361, 0, 208.9183),
    (94.5119, 0.0, 213.611),
    (82.8364, 0.0, 213.5013),
    (76.2122, 0.0, 209.9654),
]


def handle_command(cmd):
    global last_cmd, block_movement, abort_teleport

    if cmd:
        last_cmd = cmd
    elif last_cmd:
        cmd = last_cmd
    else:
        return

    cmd, *args = cmd.split()
    abort_teleport = False

    if cmd == "tp":
        x, y, z = map(float, args)
        tp(x, y, z)
    elif cmd == "tpr":
        xd, yd, zd = map(float, args)
        x, y, z, *_ = last_pos
        tp(x + xd, y + yd, z + zd)
    elif cmd == "pos":
        print(last_pos)
    elif cmd == "race":
        todo = CHECKPOINTS
        last = last_pos[:3]

        if dist(last, CHECKPOINTS[0]) > 9:
            for i, cp in reversed(list(enumerate(CHECKPOINTS))):
                if dist(last, cp) < 9:
                    todo = list(reversed(CHECKPOINTS[: i + 1]))
                    break
            else:
                print("Too far away from start")
                return

        block_movement = True
        pytime.sleep(2)

        for cp in todo:
            if abort_teleport:
                break
            while dist(last, cp) > 10:
                direction = norm(diff(cp, last))
                last = add(last, scalar_mul(direction, 9.5))
                tp(*last)
                pytime.sleep(1)
            if dist(last, cp) > 1:
                last = cp
                tp(*cp)
                pytime.sleep(1)

        block_movement = False
    elif cmd == "checkpoint":
        global checkpoint
        if args[0] == "off":
            checkpoint = None
        else:
            checkpoint = int(args[0])
    elif cmd == "lock":
        global lock_position, locked_position
        if args:
            lock_position = args[0] == "on"
            locked_position = None
        print("Position lock", ("off", "on")[lock_position])
    elif cmd == "fly":
        global lock_y
        if args:
            lock_y = args[0] == "on"
        print("Flying is", ("off", "on")[lock_y])
    else:
        print("Unknown command:", cmd)
