#!/usr/bin/env python3

import fileinput, sys

for line in fileinput.input(sys.argv[1:]):
    print(*(f"0x{x}" for x in line.strip().split()), sep=",")
