#!/usr/bin/env python3

import struct
from sys import stdout, argv

OP_LOWEST_BIT = 0x959EE2
OP_SHIFT = 0xA19EE2
OP_DUP = 0xBC80E2
OP_OR = 0x859CE2
OP_WRITE = 0x8F9CE2
OP_EXIT = 0x80929FF0
OP_XOR = 0x80949FF0
OP_JUMP_EQ = 0x94A49FF0
OP_READ = 0x96939FF0
OP_PUSH_DATA_INT = 0xA08C9FF0
OP_PUSH_DATA_BYTE = 0xBEA69FF0
OP_PUSH_IMMEDIATE = 0xAA929FF0


def opcode_length(op):
    if 0 <= op < 128:
        return 1

    for i in range(2, 5):
        if op & 128 >> i == 0:
            return i

    return -1


def load_arg():
    result = 0

    for _ in range(3):
        a = load_arg_part()
        b = load_arg_part()
        result += b ** a

    return result


def load_arg_part():
    global ip
    val = load_opcode() - 48
    ptr = opcode_length(code[ip + 1]) + 1
    ip += opcode_length(code[ip + ptr]) + ptr
    return val


def load_opcode():
    op = 0

    for i in range(opcode_length(code[ip])):
        op |= (code[ip + i] << i * 8) & (255 << i * 8)

    return op


def push(val):
    stack.append(val)


def pop():
    return stack.pop()


with open(argv[1], "rb") as f:
    data = bytearray(f.read(0x200))
    code = bytearray(f.read(0x10000))

ip = 0
stack = []

while True:
    opcode = load_opcode()
    ip += opcode_length(code[ip])

    if opcode == OP_EXIT:
        exit(-1)
    elif opcode == OP_LOWEST_BIT:
        push(pop() & 1)
    elif opcode == OP_SHIFT:
        ip += opcode_length(code[ip])
        arg = load_arg()
        push(pop() >> arg)
    elif opcode == OP_DUP:
        ip += opcode_length(code[ip])
        x = pop()
        push(x)
        push(x)
    elif opcode == OP_OR:
        push(pop() | pop())
    elif opcode == OP_WRITE:
        ip += opcode_length(code[ip])
        length = pop()
        offset = pop()
        stdout.buffer.write(data[offset : offset + length])
    elif opcode == OP_READ:
        length = pop()
        offset = pop()
        inp = input().encode()[:length]
        data[offset : offset + len(inp)] = inp
    elif opcode == OP_PUSH_IMMEDIATE:
        arg = load_arg()
        push(arg)
    elif opcode == OP_PUSH_DATA_BYTE:
        arg = load_arg()
        push(data[arg])
    elif opcode == OP_PUSH_DATA_INT:
        arg = load_arg()
        push(struct.unpack("I", data[arg:arg+4])[0])
    elif opcode == OP_XOR:
        push(pop() ^ pop())
    elif opcode == OP_JUMP_EQ:
        arg = load_arg()
        if pop() == pop():
            ip += arg
    else:
        print("Unknown opcode")
