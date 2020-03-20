# Intro to Reversing 3

When run, the binary asks for a password:
```
$ ./rev3
Give me your password:
abc
Thats not the password!
```

Looking at the binary with `ltrace` we can see an interesting string comparison after entering the password:

```
$ ltrace ./rev3
...
puts("Give me your password: ")                       = 24
read(0, "abc\n", 31)                                  = 4
strcmp("igm", "lp`7a<qLw\036kHopt(f-f*,o}V\017\025J") = -3  <--- HERE
puts("Thats not the password!")                       = 24
+++ exited (status 0) +++
```

The left part of the comparison (`"igm"`) has the same number of letters as the provided password (`"abc"`),
so we can assume that this is the input after going through some kind of transformation or hash function.
It is then compared to what is probably the "hashed" password.

I don't see an immediately obvious connection between the input before and after the transformation, but at least it looks like the number of characters is preserved, so the password probably has `27` letters.

Lets try a few more values:

```
"aaaaaaaaaaaaaaaaaaaaaaaaaaa" => "ihkjmlonqpsrutwvyx{z}|?>A@C"
"bbbbbbbbbbbbbbbbbbbbbbbbbbb" => "fglmjkpqnotursxyvw|}z{@A>?D"
```

It looks like the position of the characters matters, but I still can't see an obvious connection, so let's have a look at the binary in IDA.

This is the decompiled `main` function:

```cpp
int __cdecl main(int argc, const char **argv, const char **envp) {
    int i; // [rsp+8h] [rbp-38h]
    int length; // [rsp+Ch] [rbp-34h]
    char input[40]; // [rsp+10h] [rbp-30h]
    unsigned __int64 v7; // [rsp+38h] [rbp-8h]

    v7 = __readfsqword(0x28u);
    initialize_flag();

    puts("Give me your password: ");
    length = read(0, input, 31uLL);
    input[length - 1] = 0;

    for ( i = 0; i < length - 1; ++i ) {
        input[i] ^= i + 10;
        input[i] -= 2;
    }

    if ( !strcmp(input, passwordHash) ) {
        puts("Thats the right password!");
        printf("Flag: %s", &flagBuffer);
    } else {
        puts("Thats not the password!");
    }

    return 0;
}
```

The first part seems a bit weird:
```cpp
unsigned __int64 v7; // [rsp+38h] [rbp-8h]
v7 = __readfsqword(0x28u);
```

But looking at the assembly, this is just loading the stack canary:
```asm
mov     rax, fs:28h
mov     [rbp-8], rax    ; The decompilation shows [rbp-8h] as v7
```

And the canary is then checked at the end of the function:
```asm
mov     rcx, [rbp-8]
xor     rcx, fs:28h
jz      short locret_9AA
; We reach here only when [rbp-8] != fs:28h which means the canary was overridden
call    ___stack_chk_fail

locret_9AA:
leave
retn
```

Looking at the decompiled code again, the binary then loads the flag and reads the user input:
```cpp
initialize_flag();

puts("Give me your password: ");
length = read(0, input, 31uLL);
input[length - 1] = 0;
```

The next part seems to be responsible for the input transformation:
```cpp
for ( i = 0; i < length - 1; ++i ) {
    input[i] ^= i + 10;
    input[i] -= 2;
}
```

And finally it checks if the transformed input is equal to the flag:
```cpp
if ( !strcmp(input, passwordHash) ) {
    puts("Thats the right password!");
    printf("Flag: %s", &flagBuffer);
} else {
    puts("Thats not the password!");
}
```

As the transformation works on each character separately it is easily reversible:
```python
pwd = bytearray(b"lp`7a<qLw\036kHopt(f-f*,o}V\017\025J")

for i in range(len(pwd)):
    pwd[i] += 2
    pwd[i] ^= i + 10

print(pwd)
```

And this gives us: `dyn4m1c_k3y_gen3r4t10n_y34h`.

And trying that as the password indeed reveals the flag:
```
Give me your password:
dyn4m1c_k3y_gen3r4t10n_y34h
Thats the right password!
Flag: CSCG{pass_1_g3ts_a_x0r_p4ss_2_g3ts_a_x0r_EVERYBODY_GETS_A_X0R}
```

Clearly, `xor`ing characters with their position and adding some constants still isn't a one-way transformation, which is again why this password check was easy to reverse.
A proper oneway transformation to hide the password would be a strong cryptographic hash function like PBKDF2, bcrypt, or scrypt.
