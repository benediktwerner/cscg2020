#!/usr/bin/env python3

import struct

flag = ""
flag += chr(0xF2 ^ 0x9C)
flag += chr(0xEA ^ 0xD9)
flag += chr(0x82 ^ 0xF5)
flag += chr(0x36 ^ 0x69)
flag += chr(0x8E ^ 0xEF)
flag += chr(0x12 ^ 0x75)
flag += chr(0x18 ^ 0x2B)
flag += chr(0x73 ^ 0x2C)
flag += chr(0x7B ^ 0xD)
flag += chr(0x11 ^ 0x20)
flag += chr(0x5B ^ 0x29)
flag += chr(0x69 ^ 0x1D)
flag += chr(0x38 ^ 0x4D)
flag += chr(0x8A ^ 0xBE)
flag += chr(0xB0 ^ 0xDC)
flag += chr(0x8B ^ 0xE2)
flag += chr(0x8E ^ 0xF4)
flag += chr(0x83 ^ 0xB7)
flag += chr(0xF6 ^ 0x82)
flag += chr(0xC4 ^ 0xF5)
flag += chr(0x39 ^ 0x56)
flag += chr(0xF5 ^ 0x9B)
flag += chr(0xA2 ^ 0xFD)

for a in range(0x20, 0x7F):
    for b in range(0x20, 0x7F):
        for c in range(0x20, 0x7F):
            for d in range(0x20, 0x7F):
                k = a | b << 8 | c << 16 | d << 24
                x = 4294967295
                for i in range(32):
                    if x & 1 != (k >> i) & 1:
                        x = (x >> 1) ^ 3988292384
                    else:
                        x >>= 1

                if x == 4094592094:
                    print(flag + struct.pack(k).decode())
                    exit()
