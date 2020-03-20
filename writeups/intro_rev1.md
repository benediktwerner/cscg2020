# Intro to Reversing 1

When run, the binary asks for a password:
```
$ ./rev1
Give me your password:
abc
Thats not the password!
```

Using `strings` on the binary yields some interesting results:

```
$ strings rev1
...
Give me your password:
y0u_5h3ll_p455
Thats the right password!
Flag: %s
Thats not the password!
./flag
flag
File "%s" not found. If this happens on remote, report to an admin. Exiting...
...
```

Trying `y0u_5h3ll_p455` as the password yields the flag:
```
Give me your password:
y0u_5h3ll_p455
Thats the right password!
Flag: CSCG{ez_pz_reversing_squ33zy}
```

Looking at the binary with `ltrace` reveals that the password check is a simple string comparison:

```
$ ltrace ./rev1
...
puts("Give me your password: ")   = 24
read(0, "abc\n", 31)              = 4
strcmp("abc", "y0u_5h3ll_p455")   = -24     <--- HERE
puts("Thats not the password!")   = 24
+++ exited (status 0) +++
```

This obviously means the password is stored as plain text in the binary, which is also why we could find it with `strings`.
It clearly isn't a good idea to store passwords as plain text.
They should instead be hashed with a strong cryptographic hash function like PBKDF2, bcrypt, or scrypt.
When checking for a password the program can then hash the input with the same function and only compare the hashed values.
This way it's pretty much impossible to find out the password, even when you have the hash of the password and the hash alone isn't useful when the password checking is done on a remote server.
