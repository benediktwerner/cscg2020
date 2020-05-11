import random, socket, struct
from threading import Thread
from importlib import reload

import requests

from . import parser
from .utils import *

GAME_SERVER_ADDR = "hax1.allesctf.net"
GAME_SERVER_HOSTNAME = "maze.liveoverflow.com"


class GameConnection:
    def __init__(self, port):
        self.game = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.game.bind(("", port))
        self.game_addr = None

    def recv(self):
        data, game_addr = self.game.recvfrom(4096)
        if game_addr != self.game_addr:
            print("New game connection")
            self.game_addr = game_addr
        return data

    def send(self, data):
        self.game.sendto(data, self.game_addr)


class Proxy2Server(Thread):
    def __init__(self):
        super().__init__()

        self.game = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        while True:
            data, addr = self.server.recvfrom(4096)

            try:
                result = parser.parse_server(data)
                if result is not None:
                    self.game.send(result)
                    continue
            except Exception as e:
                print("Server parser exception:", e)

            self.game.send(data)


class Game2Proxy(Thread):
    def __init__(self, port):
        super().__init__()

        self.port = port
        self.server = None
        self.game = GameConnection(port)

    def run(self):
        while True:
            data = self.game.recv()

            try:
                result = parser.parse_client(data)
                if result is not None:
                    self.game.send(result)
                    continue
            except Exception as e:
                print("Client parser exception:", e)

            self.send_to_server(data)

    def send_to_server(self, data):
        self.server.sendto(data, (GAME_SERVER_ADDR, self.port))


class ApiServer(Thread):
    def __init__(self, port):
        super().__init__()

        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("0.0.0.0", 80))
        self.sock.listen(1)

        printc(YELLOW, "[api server] listening on port 80")

    def run(self):
        while True:
            conn, addr = self.sock.accept()
            method, path = conn.recv(1024).decode().split(" ")[:2]

            if method != "GET":
                printc(
                    YELLOW,
                    "[api server] Unsupported HTTP request method:",
                    method,
                    path,
                )
                continue

            if path == "/api/hostname":
                response = "localhost"
                # response = "hax1.allesctf.net"
            elif path == "/api/min_port" or path == "/api/max_port":
                response = str(self.port)
            else:
                response = get(path)

            if not path.startswith("/api/highscore"):
                printc(YELLOW, f"[api server] {method} request to {path}: {response}")

            conn.send(b"HTTP/1.1 200 OK\r\n\r\n")
            conn.send(response.encode())
            conn.close()


def get(path):
    return requests.get(
        f"http://{GAME_SERVER_ADDR}{path}", headers={"Host": GAME_SERVER_HOSTNAME}
    ).text


min_port = int(get("/api/min_port"))
max_port = int(get("/api/max_port"))
port = random.randrange(min_port, max_port + 1)

ApiServer(port).start()

p2s = Proxy2Server()
g2p = Game2Proxy(port)

p2s.game = g2p.game
g2p.server = p2s.server

p2s.start()
g2p.start()

while True:
    try:
        cmd = input()
        if cmd in ("quit", "exit"):
            import os

            os._exit(0)

        if cmd == "reload":
            reload(parser)
        else:
            parser.handle_command(cmd, g2p)

    except Exception as e:
        print(e)
