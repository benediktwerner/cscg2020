## Login
User: 1vader
Pass: U4XB90SSKRKQ5CIV
Hash: faa777179b665fe4

`netstat -oa`

`tcp.port == xxx && tcp.len > 0`

maze.liveoverflow.com:1337-1357

connected port is changing

```
$ ping maze.liveoverflow.com
PING maze.liveoverflow.com (147.75.85.99) 56(84) bytes of data.

$ ping hax1.allesctf.net
PING hax1.allesctf.net (147.75.85.99) 56(84) bytes of data.
```

```
$ netstat -bn
  TCP    192.168.178.57:52120   35.241.26.53:443       HERGESTELLT
 [Maze.exe]
  TCP    192.168.178.57:52121   35.241.52.229:443      HERGESTELLT
 [Maze.exe]
  TCP    192.168.178.57:52122   147.75.85.99:80        SCHLIESSEN_WARTEN
 [Maze.exe]
```

```
$ netstat -bf
  TCP    192.168.178.57:52353   53.26.241.35.bc.googleusercontent.com:https  HERGESTELLT
 [Maze.exe]
  TCP    192.168.178.57:52354   229.52.241.35.bc.googleusercontent.com:https  HERGESTELLT
 [Maze.exe]
  TCP    192.168.178.57:52355   hax1.allesctf.net:http  SCHLIESSEN_WARTEN
 [Maze.exe]
```

certificate by `*.unity3d.com`

`35.241.26.53`:     HTTP ERROR 405
`35.241.52.229`:    empty response
`147.75.85.99`:     nginx RHEL default page

when connecting to the game the connection to `hax1.allesctf.net` changes to `HERGESTELLT`

```
$ netstat -abn
  UDP    0.0.0.0:53083          *:*
 [Maze.exe]
```

Wireshark, record game startup, filter `tcp` or `ip.addr == 147.75.85.99`

Requests:
```
/api/health         yes
/api/welcome        Maze - hotfix v2.1 available to download now
/api/hostname       maze.liveoverflow.com
/api/ratelimit      20
/api/min_port       1337
/api/max_port       1357
/api/login_queue    0
```

When trying to access in browser it only works when using hostname `maze.liveoverflow.com`.

After login more requests:
```
/api/highscore                      Highscore list
/api/highscore/FAA777179B665FE4     Probably my highscore
```

No login packets over TCP

Edit `%WINDIR%\System32\drivers\etc\hosts` and add:
```
127.0.0.1			maze.liveoverflow.com
```

Find x-refs to `sendData`:
- `ServerManager.update`: sending heartbeat
- `ServerManager.sendHeartbeat`
- `ServerManager.LoginLoop`
- `ServerManger.UpdateServerPosition`
