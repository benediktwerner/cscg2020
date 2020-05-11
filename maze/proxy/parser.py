import struct

from .utils import *

HIDE_CLIENT_HEARTBEAT = True
HIDE_SERVER_HEARTBEAT = True

last_pos = None
last_secret = None
last_time = None
white_rabbit_uid = None
radar_file = open("radar.txt", "w")

def decrypt(data):
    result = bytearray(len(data) - 2)
    rand1 = data[0]
    rand2 = data[1]
    for i, c in enumerate(data[2:]):
        result[i] = rand1 ^ c
        rand1 = (rand1 + rand2) % 0xFF
    return result


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
    global last_time
    time = struct.unpack("Q", data[:8])[0] / 10000
    last_time = time
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
    global last_pos
    secret, data = parse_secret(data)
    time, data = parse_time(data)
    x, y, z, ax, ay, az = map(lambda x: x / 10_000, struct.unpack("iiiiii", data[:24]))
    last_pos = (x, y, z, ax, ay, az)
    trigger = data[24]
    grounded, not_grounded = struct.unpack("hh", data[25:])
    return
    print_client(
        f"Position at {time: 5.2f}",
        "=",
        f"{x},{y},{z}",
        f"{ax},{ay},{az}",
        trigger,
        grounded,
        not_grounded,
    )


def parse_info_request(data):
    secret, data = parse_secret(data)
    uid = struct.unpack("I", data)[0]
    print_client("Info request about", uid)


def parse_emoji(data):
    secret, data = parse_secret(data)
    index = data[0]
    print_client("Emoji", index)


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
    if HIDE_SERVER_HEARTBEAT:
        return
    print_server(f"Heartbeat at {time: 5.2f}, {server_time}")


def server_login(data):
    uid, unlocks, version = struct.unpack("IHB", data)
    print_server(f"Login response: {uid=} {unlocks=} {version=}")


def server_info(data):
    uid, unlocks, name_length = struct.unpack("IHB", data[:7])
    name = data[7:].decode()
    if name == "The White Rabbit":
        global white_rabbit_uid
        white_rabbit_uid = uid
    print_server(f"Info reponse about {uid}: {name=} {unlocks=}")


def server_emoji(data):
    uid, emoji_time, emoji = struct.unpack("IIB", data)
    print_server(f"Emoji {emoji} from {uid} at {emoji_time}")


def server_position(data):
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
        if uid == white_rabbit_uid:
            print(x, y, z, trigger, grounded, not_grounded, file=radar_file, flush=True)
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


def server_unlock(data):
    unlocks = struct.unpack("H", data)[0]
    print_server("Got a new unlock: {unlocks}")


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


def tp(g2p, *cords):
    data = b"P" + last_secret
    data += struct.pack("Q", round(last_time * 10000 + 10000))
    data += struct.pack("iiiiii", *cords)
    data += b"0000000000"
    g2p.send_to_server(data)


def handle_command(cmd, g2p):
    cmd, *args = cmd.split()

    if cmd == "tp":
        x, y, z = map(int, args)
        tp(g2p, x, y, z, 0, 0, 0)
    elif cmd == "tpr":
        xd, yd, zd = map(int, args)
        x, y, z, ax, ay, az = last_pos
        tp(g2p, x + xd, y + yd, z + zd, ax, ay, az)
    elif cmd == "pos":
        print(last_pos)
    else:
        print("Unknown command:", cmd)
