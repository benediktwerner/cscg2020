#!/usr/bin/env python3

import hashlib, string, itertools

for i in range(10):
    print(i)
    for g in itertools.product(string.ascii_letters + string.digits, repeat=i):
        if hashlib.md5("".join(g).encode()).hexdigest() == "b72f3bd391ba731a35708bfd8cd8a68f":
            print(g)
            exit()
