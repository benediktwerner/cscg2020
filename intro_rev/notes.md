# Intro to Reversing 1

`strings rev1` shows password: `y0u_5h3ll_p455`

Flag: `CSCG{ez_pz_reversing_squ33zy}`

# Intro to Reversing 2

`ltrace rev2` with password `abc` shows `strcmp("\352\353\354", "\374\375\352\300\272\354\350\375\373\275\367\276\357\271\373\366\275\300\272\271\367\350\362\375\350\362\374")`.

Clearly `"\352\353\354"` is a transformation of the input.
Apparently a constant was added to each character code.
Checking in Python reveals the offset: `137` and the password: `sta71c_tr4n5f0rm4710n_it_is`

```python
>>> ord("\352") - ord("a")
137
>>> "".join(chr(ord(c) - 137) for c in "\374\375\352\300\272\354\350\375\373\275\367\276\357\271\373\366\275\300\272\271\367\350\362\375\350\362\374")
sta71c_tr4n5f0rm4710n_it_is
```

Flag: `CSCG{1s_th4t_wh4t_they_c4ll_on3way_transf0rmati0n?}`

# Intro to Reversing 3

`ltrace rev2` with password `abc` shows ``strcmp("igm", "lp`7a<qLw\036kHopt(f-f*,o}V\017\025J")``.

31 * a  "ihkjmlonqpsrutwvyx{z}|?>A@CBED"
31 * b  "fglmjkpqnotursxyvw|}z{@A>?DEBC"
31 * \0 "\b\t\n\v\f\r\016\017\020\021\022\023\024\025\026\027\030\031\032\033\034\035\036\037 !"#$%"

## Decompiled code

```python
for i in range(len(pwd)):
    pwd[i] ^= i + 10
    pwd[i] -= 2

if pwd == "lp`7a<qLw\036kHopt(f-f*,o}V\017\025J":
    print("win")
```

## Reverse pwd

```python
pwd = bytearray(b"lp`7a<qLw\036kHopt(f-f*,o}V\017\025J")

for i in range(len(pwd)):
    pwd[i] += 2
    pwd[i] ^= i + 10

print(pwd)
```

## Result

Password: `dyn4m1c_k3y_gen3r4t10n_y34h`
Flag: `CSCG{pass_1_g3ts_a_x0r_p4ss_2_g3ts_a_x0r_EVERYBODY_GETS_A_X0R}`
