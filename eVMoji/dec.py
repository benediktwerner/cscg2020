#!/usr/bin/env python3

from sys import argv
import struct


OP_BOOL = 0x959EE2
OP_X = 0xA19EE2
OP_DUP = 0xBC80E2
OP_OR = 0x859CE2
OP_WRITE = 0x8F9CE2
OP_EXIT = 0x80929FF0
OP_XOR = 0x80949FF0
OP_JUMP_EQ = 0x94A49FF0
OP_READ = 0x96939FF0
OP_PUSH_POW_I_INT = 0xA08C9FF0
OP_PUSH_POW = 0xAA929FF0
OP_PUSH_POW_I_BYTE = 0xBEA69FF0


def load_arg_pow():
    result = 0

    for _ in range(3):
        a = load_arg()
        b = load_arg()
        result += b ** a

    return result


def load_arg():
    global ip

    val = load_opcode() - 48
    ptr = opcode_len(code[ip + 1]) + 1
    ip += opcode_len(code[ip + ptr]) + ptr
    return val


def load_opcode():
    op = 0

    for i in range(opcode_len(code[ip])):
        op |= (code[ip + i] << i * 8) & (255 << i * 8)

    return op


def opcode_len(op):
    if 0 <= op < 128:
        return 1

    for i in range(2, 5):
        if op & (128 >> i) == 0:
            return i

    assert False
    return -1


with open(argv[1], "rb") as f:
    header = bytearray(f.read(0x200))
    code = bytearray(f.read(0x10000))

ip = 0

while ip < len(code):
    print(f"{ip:4x}", end="  ")
    opcode = load_opcode()
    ip += opcode_len(code[ip])

    if opcode == OP_EXIT:
        print("EXIT")
    elif opcode == OP_BOOL:
        print("BOOL")
    elif opcode == OP_X:
        ip += opcode_len(code[ip])
        arg = load_arg_pow()
        print("TOP >>", arg)
    elif opcode == OP_DUP:
        ip += opcode_len(code[ip])
        print("DUP")
    elif opcode == OP_OR:
        print("OR")
    elif opcode == OP_WRITE:
        ip += opcode_len(code[ip])
        print("WRITE <len> <offset>")
    elif opcode == OP_READ:
        print("READ <len> <offset>")
    elif opcode == OP_PUSH_POW:
        arg = load_arg_pow()
        print("PUSH", hex(arg))
    elif opcode == OP_PUSH_POW_I_BYTE:
        arg = load_arg_pow()
        print("PUSH_BYTE_AT", hex(arg), "(", header[arg], ")")
    elif opcode == OP_PUSH_POW_I_INT:
        arg = load_arg_pow()
        print(
            "PUSH_INT_AT",
            hex(arg),
            "(",
            struct.unpack("I", header[arg : arg + 4])[0],
            ")",
        )
    elif opcode == OP_XOR:
        print("XOR")
    elif opcode == OP_JUMP_EQ:
        arg = load_arg_pow()
        print("if TOP == TOP1: goto", hex(ip + arg))
    else:
        print("Unknown opcode:", hex(opcode))
