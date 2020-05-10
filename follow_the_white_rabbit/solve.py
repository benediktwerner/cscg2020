#!/usr/bin/env python3

text = "aof\\`drfe`dbbjQ|st|vg"
num = 0
result = ""

for c in text:
    result += chr(ord(c) ^ num)
    num += 1

print(result)
