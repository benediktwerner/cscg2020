#!/usr/bin/env python3

from z3 import *

a = ""
a += chr(0xf2 ^ 0x9c)
a += chr(0xea ^ 0xd9)
a += chr(0x82 ^ 0xf5)
a += chr(0x36 ^ 0x69)
a += chr(0x8e ^ 0xef)
a += chr(0x12 ^ 0x75)
a += chr(0x18 ^ 0x2b)
a += chr(0x73 ^ 0x2c)
a += chr(0x7b ^ 0xd)
a += chr(0x11 ^ 0x20)
a += chr(0x5b ^ 0x29)
a += chr(0x69 ^ 0x1d)
a += chr(0x38 ^ 0x4d)
a += chr(0x8a ^ 0xbe)
a += chr(0xb0 ^ 0xdc)
a += chr(0x8b ^ 0xe2)
a += chr(0x8e ^ 0xf4)
a += chr(0x83 ^ 0xb7)
a += chr(0xf6 ^ 0x82)
a += chr(0xc4 ^ 0xf5)
a += chr(0x39 ^ 0x56)
a += chr(0xf5 ^ 0x9b)
a += chr(0xa2 ^ 0xfd)

# x = BitVec("x", 32)
# y = BitVecVal(4294967295, 32)

# for i in range(32):
#     y = If(Extract(0, 0, y) == Extract(i, i, x), y >> 1, (y >> 1) ^ 3988292384)

# s = Solver()
# s.add(y == 4094592094)

# while s.check() == sat:
#     res = s.model()[x].as_long()
#     s.add(x != res)
#     print(res)

for k in range(1064054892, 1 << 32):
    if k % 100_000 == 0:
        print(k, k * 100 / (1 << 32))

    x = 4294967295
    for i in range(32):
        if x & 1 != (k >> i) & 1:
            x = (x >> 1) ^ 3988292384
        else:
            x >>= 1
    
    if x == 4094592094:
        print(a + bytes.fromhex(hex(k)[2:]).decode()[::-1])
        break
