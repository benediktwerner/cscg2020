# eVMoji

The challenge gives us two files:

```
$ file *
code.bin:   data
eVMoji:     ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked,
            interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=d99414f2e1b78e1beaea5f81e0eb21b1bc2ae3ef, stripped
```

A Linux `ELF` binary `eVMoji` and a binary data file `code.bin`.

Running the binary prints some usage information:

```
$ ./eVMoji
Usage: ./eVMoji <code.bin>
Segmentation fault
```

Running the binary with `code.bin` asks us to give a flag and checks it:

```
$ ./eVMoji code.bin
Welcome to eVMoji 😎
🤝 me the 🏳️
AAAAAA
tRy hArder! 💀💀💀
```

It looks like the binary implements some kind of virtual machine (as the name `eVMoji` suggests) and `code.bin` is the code run by that VM.

Taking a look at `code.bin` we can see some garbage unprintable bytes, some strings and then a bunch of emoji:

```
$ cat code.bin
 ��� ���^������Welcome to eVMoji 😎
🤝 me the 🏳️
tRy hArder! 💀💀💀
Gotta go cyclic ♻️
Thats the flag: CSCG{}
💪1️⃣0️⃣2️⃣4️⃣7️⃣2️⃣💪0️⃣0️⃣1️⃣6️⃣2️⃣4️⃣✏️
...
```

The emoji are probably the opcodes for the VM.

After some reverse engineering using IDA we can find out that the VM works roughly like this:

```python
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
```

We can see that the first `0x200` bytes of `code.bin` are data and the rest is the code.

The VM seems to be stack-based and the opcodes mostly modify the top values on the stack.

Some of them also read or write to the data section.

There are 12 opcode:
- `EXIT`: Exits the program
- `DUP`: Duplicates the value on top of the stack
- `LOWEST_BIT`: `push(pop() & 1)`
- `SHIFT <amount>`: `push(pop() >> amount)`
- `OR`: `push(pop() | pop())`
- `XOR`: `push(pop() ^ pop())`
- `WRITE`: Write some string from `data` to `stdout`. The position and length of the string are taken from the stack.
- `READ`: Read some string from `stdin` to `data`. The position and length to read to are taken from the stack.
- `PUSH <val>`: `push(val)`
- `PUSH_BYTE_AT <pos>`: Push the byte at `pos` in `data` onto the stack
- `PUSH_BYTE_INT <pos>`: Push the int (i.e. 4 bytes) at `pos` in `data` onto the stack
- `JUMP_EQ <amount>`: `if pop() == pop: ip += amount`

With this understanding of the VM we can now easily build a disassembler for `code.bin`:

```python
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


with open(argv[1], "rb") as f:
    data = bytearray(f.read(0x200))
    code = bytearray(f.read(0x10000))

ip = 0

while ip < len(code):
    print(f"{ip:4x}", end="  ")
    opcode = load_opcode()
    ip += opcode_length(code[ip])

    if opcode == OP_EXIT:
        print("EXIT")
    elif opcode == OP_LOWEST_BIT:
        print("LOWEST_BIT")
    elif opcode == OP_SHIFT:
        ip += opcode_length(code[ip])
        arg = load_arg()
        print("TOP >>", arg)
    elif opcode == OP_DUP:
        ip += opcode_length(code[ip])
        print("DUP")
    elif opcode == OP_OR:
        print("OR")
    elif opcode == OP_WRITE:
        ip += opcode_length(code[ip])
        print("WRITE")
    elif opcode == OP_READ:
        print("READ")
    elif opcode == OP_PUSH_IMMEDIATE:
        arg = load_arg()
        print("PUSH", hex(arg))
    elif opcode == OP_PUSH_DATA_BYTE:
        arg = load_arg()
        print("PUSH_BYTE_AT", hex(arg), "(", data[arg], ")")
    elif opcode == OP_PUSH_DATA_INT:
        arg = load_arg()
        print(
            "PUSH_INT_AT",
            hex(arg),
            "(",
            struct.unpack("I", data[arg : arg + 4])[0],
            ")",
        )
    elif opcode == OP_XOR:
        print("XOR")
    elif opcode == OP_JUMP_EQ:
        arg = load_arg()
        print("if TOP == TOP1: goto", hex(ip + arg))
    else:
        print("Unknown opcode:", hex(opcode))
```

Now we can take a look at what's going on in `code.bin`:

```
$ ./dec.py code.bin
   0  PUSH 0x90
  2e  PUSH 0x17
  5c  WRITE
  62  PUSH 0xa7
  90  PUSH 0x14
  be  WRITE
  c4  PUSH 0x0
  f2  PUSH 0x1b
 120  READ
...
```

The first few instructions are just printing the welcome message and read the flag to position `0`.

It looks like the flag is `0x1b = 27` bytes long.

Next, the code pushes a `0` onto the stack:

```
 124  PUSH 0x0
```

And then we see a block repeated 23 times:

```
 152  PUSH 0xf2
 180  PUSH_BYTE_AT 0x0 ( 0 )
 1ae  XOR
 1b2  PUSH 0x9c
 1e0  XOR
 1e4  OR
```

The numbers pushed onto the stack are always different and the position of the byte that is pushed is increasing in every block but everything else is the same.

Remember that the flag was read to position `0` so we are calculating some `xor` together with characters of the flag.

Together with the `0` pushed previously these blocks correspond to this code:

```python
a = 0
a |= 0xf2 ^ data[0x0] ^ 0x9c
a |= 0xea ^ data[0x1] ^ 0xd9
a |= 0x82 ^ data[0x2] ^ 0xf5
a |= 0x36 ^ data[0x3] ^ 0x69
a |= 0x8e ^ data[0x4] ^ 0xef
a |= 0x12 ^ data[0x5] ^ 0x75
a |= 0x18 ^ data[0x6] ^ 0x2b
a |= 0x73 ^ data[0x7] ^ 0x2c
a |= 0x7b ^ data[0x8] ^ 0xd
a |= 0x11 ^ data[0x9] ^ 0x20
a |= 0x5b ^ data[0xa] ^ 0x29
a |= 0x69 ^ data[0xb] ^ 0x1d
a |= 0x38 ^ data[0xc] ^ 0x4d
a |= 0x8a ^ data[0xd] ^ 0xbe
a |= 0xb0 ^ data[0xe] ^ 0xdc
a |= 0x8b ^ data[0xf] ^ 0xe2
a |= 0x8e ^ data[0x10] ^ 0xf4
a |= 0x83 ^ data[0x11] ^ 0xb7
a |= 0xf6 ^ data[0x12] ^ 0x82
a |= 0xc4 ^ data[0x13] ^ 0xf5
a |= 0x39 ^ data[0x14] ^ 0x56
a |= 0xf5 ^ data[0x15] ^ 0x9b
a |= 0xa2 ^ data[0x16] ^ 0xfd
```

After the blocks we have this code:

```
 eb5  PUSH 0x0
 ee3  if TOP == TOP1: goto 0xf77

 f11  PUSH 0xbb
 f3f  PUSH 0x19
 f6d  WRITE

 f73  EXIT

 f77  ...
```

Which translates to:

```python
if a != 0:
    print("try harder")
    exit()
```

Next, we again push a single value onto the stack:

```
 f77  PUSH_INT_AT 0x8c ( 4294967295 )
```

And the we again have a block nearly repeated, this time 32 times:

```
 fa5  DUP
 fab  LOWEST_BIT
 fae  PUSH_INT_AT 0x17 ( 0 )
 fdc  TOP >> 0
100c  LOWEST_BIT
100f  if TOP == TOP1: goto 0x1129

103d  TOP >> 1
106d  PUSH_INT_AT 0x80 ( 3988292384 )
109b  XOR
109f  PUSH 0x0
10cd  PUSH 0x0
10fb  if TOP == TOP1: goto 0x1159

1129  TOP >> 1

1159  ...
```

In this block, we always load an int (so 4 bytes) from position `0x17`, so this is checking the last 4 bytes of the flag.

Each block shifts the value right by an increasing amount and then only looks at the lowest bit, so every block is checking only a single bit of the flag.

All the blocks together translate to this:

```python
x = 4294967295
for bit in range(32):
    if x & 1 != (data[0x17:0x1b] >> bit) & 1:
        x = (x >> 1) ^ 3988292384
    else:
        x >>= 1
```

And after the blocks we again have a check if the result is correct:

```
4625  PUSH_INT_AT 0x88 ( 4094592094 )
4653  XOR
4657  PUSH 0x0
4685  if TOP == TOP1: goto 0x4719

46b3  PUSH 0xd4
46e1  PUSH 0x17
470f  WRITE
4715  EXIT

4719  PUSH 0xeb
4747  PUSH 0x15
4775  WRITE

477b  PUSH 0x0
47a9  PUSH 0x1b
47d7  WRITE

47dd  PUSH 0x100
480b  PUSH 0x2
4839  WRITE

483f  EXIT
```

Which translates roughly to this:

```python
if x != 4094592094:
    print("gotta go cyclic")
    exit()

print("Thats the flag: CSCG{", data[0:27], "}")
```

So this is basically what the whole code does:

```python
flag = input()

a = 0
a |= 0xf2 ^ flag[0x0] ^ 0x9c
a |= 0xea ^ flag[0x1] ^ 0xd9
a |= 0x82 ^ flag[0x2] ^ 0xf5
a |= 0x36 ^ flag[0x3] ^ 0x69
a |= 0x8e ^ flag[0x4] ^ 0xef
a |= 0x12 ^ flag[0x5] ^ 0x75
a |= 0x18 ^ flag[0x6] ^ 0x2b
a |= 0x73 ^ flag[0x7] ^ 0x2c
a |= 0x7b ^ flag[0x8] ^ 0xd
a |= 0x11 ^ flag[0x9] ^ 0x20
a |= 0x5b ^ flag[0xa] ^ 0x29
a |= 0x69 ^ flag[0xb] ^ 0x1d
a |= 0x38 ^ flag[0xc] ^ 0x4d
a |= 0x8a ^ flag[0xd] ^ 0xbe
a |= 0xb0 ^ flag[0xe] ^ 0xdc
a |= 0x8b ^ flag[0xf] ^ 0xe2
a |= 0x8e ^ flag[0x10] ^ 0xf4
a |= 0x83 ^ flag[0x11] ^ 0xb7
a |= 0xf6 ^ flag[0x12] ^ 0x82
a |= 0xc4 ^ flag[0x13] ^ 0xf5
a |= 0x39 ^ flag[0x14] ^ 0x56
a |= 0xf5 ^ flag[0x15] ^ 0x9b
a |= 0xa2 ^ flag[0x16] ^ 0xfd

if a != 0:
    print("try harder")
    exit()

x = 4294967295
for bit in range(32):
    if x & 1 != (data[0x17] >> bit) & 1:
        x = (x >> 1) ^ 3988292384
    else:
        x >>= 1

if x != 4094592094:
    print("gotta go cyclic")
    exit()

print("Thats the flag: CSCG{", data[0:27], "}")
```

With this, we should be able to find the flag.

In the first part, `a` will only ever be zero if every expression `or`'d with it is also zero.

We can easily calculate what the bytes of the flag must be to satisfy this:

If `0xf2 ^ x ^ 0x9c` is zero then `x = 0xf2 ^ 0x9c`.

The second part is a bit more difficult.

There might be a simple way to calculate this and we could probably also use a SAT-solver to solve this.

But since the value space isn't actually that large (only 4 bytes or `2**32 = 4,294,967,296` different values),
we can just brute-force it.
Actually, we can assume the characters are ASCII letters, numbers, or symbols which reduces the search space even further.

In the end, we get the following python script:

```python
import struct 

flag = ""
flag += chr(0xf2 ^ 0x9c)
flag += chr(0xea ^ 0xd9)
flag += chr(0x82 ^ 0xf5)
flag += chr(0x36 ^ 0x69)
flag += chr(0x8e ^ 0xef)
flag += chr(0x12 ^ 0x75)
flag += chr(0x18 ^ 0x2b)
flag += chr(0x73 ^ 0x2c)
flag += chr(0x7b ^ 0xd)
flag += chr(0x11 ^ 0x20)
flag += chr(0x5b ^ 0x29)
flag += chr(0x69 ^ 0x1d)
flag += chr(0x38 ^ 0x4d)
flag += chr(0x8a ^ 0xbe)
flag += chr(0xb0 ^ 0xdc)
flag += chr(0x8b ^ 0xe2)
flag += chr(0x8e ^ 0xf4)
flag += chr(0x83 ^ 0xb7)
flag += chr(0xf6 ^ 0x82)
flag += chr(0xc4 ^ 0xf5)
flag += chr(0x39 ^ 0x56)
flag += chr(0xf5 ^ 0x9b)
flag += chr(0xa2 ^ 0xfd)

for a in range(0x20, 0x7f):
    for b in range(0x20, 0x7f):
        for c in range(0x20, 0x7f):
            for d in range(0x20, 0x7f):
                k = a | b << 8 | c << 16 | d << 24
                x = 4294967295
                for i in range(32):
                    if x & 1 != (k >> i) & 1:
                        x = (x >> 1) ^ 3988292384
                    else:
                        x >>= 1

                if x == 4094592094:
                    print(flag + struct.pack("I", k).decode())
                    exit()
```

And after a few minutes, we will find the flag: `CSCG{n3w_ag3_v1rtu4liz4t1on_l0l?}`.

For extra speed we might want to do the brute-forcing in a faster language like `Rust` then it only takes a few seconds:

```rust
fn main() {
    for a in 0x20..0x7f {
        for b in 0x20..0x7f {
            for c in 0x20..0x7f {
                for d in 0x20..0x7f {
                    let k = a | b<<8 | c<<16 | d<<24;
                    let mut x: u32 = 4294967295;
                    for i in 0..32 {
                        if x & 1 != (k >> i) & 1 {
                            x = (x >> 1) ^ 3988292384;
                        }
                        else {
                            x >>= 1;
                        }
                    }
                    if x == 4094592094 {
                        println!("{}", k);
                        return;
                    }
                }
            }
        }
    }
}
```
