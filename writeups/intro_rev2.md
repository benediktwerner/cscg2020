# Intro to Reversing 2

When run, the binary asks for a password:
```
$ ./rev2
Give me your password:
abc
Thats not the password!
```

Looking at the binary with `ltrace` we can see an interesting string comparison after entering the password:

```
$ ltrace ./rev2
...
puts("Give me your password: ")   = 24
read(0, "abc\n", 31)              = 4
strcmp("\352\353\354", "\374\375\352\300\272\354\350\375\373\275\367\276\357\271\373\366\275\300\272\271\367\350\362\375\350\362\374") = -18  <--- HERE
puts("Thats not the password!")   = 24
+++ exited (status 0) +++
```

The left part of the comparison (`"\352\353\354"`) has the same number of letters as the provided password (`"abc"`),
so we can assume that this is the input after going through some kind of transformation or hash function.
It is then compared to what is probably the "hashed" password.

Looking at the transformed input we can see that it consists of three characters with consecutive values: octal `352`, `353`, and `354`.
This is similar to the original input "abc" or octal `141`, `142`, and `143`, so it seems likely that the transformation is simply adding a fixed amount to each character code.

A quick calculation reveals this amount to be `137`:
```python
>>> ord("\352") - ord("a")
137
```

So to find out the password from the "hash" we can just subtract that amount from each character:
```python
>>> "".join(chr(ord(c) - 137) for c in "\374\375\352\300\272\354\350\375\373\275\367\276\357\271\373\366\275\300\272\271\367\350\362\375\350\362\374")
'sta71c_tr4n5f0rm4710n_it_is'
```

And trying `sta71c_tr4n5f0rm4710n_it_is` as the password indeed reveals the flag:
```
Give me your password:
sta71c_tr4n5f0rm4710n_it_is
Thats the right password!
Flag: CSCG{1s_th4t_wh4t_they_c4ll_on3way_transf0rmati0n?}
```

Of course, adding a constant amount to each character is not a one-way transformation, which is also why this password check was so easy to reverse.
A proper oneway transformation to hide the password would be a strong cryptographic hash function like PBKDF2, bcrypt, or scrypt.
