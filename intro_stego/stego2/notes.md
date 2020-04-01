Image looks like stock photo.

Searching on https://tineye.com/ lead to [this](https://4.bp.blogspot.com/_fYHWkeTLPCo/TA5JadYuxaI/AAAAAAAACz8/kVschfpWrC4/s1600/Brisbane2.jpg) image which seems to be the original.

Comparing them we can immediately see a difference between which windows are lit in the building on the left.

Taking the lit windows as ones and the unlit windows as zeros we get:

```
01000011
01010011
01000011
01000111
01111011
01100001
01011111
01000110
01101100
00110100
01100111
01111101
00000000
00000000
```

8-bit values => 1 byte => 1 character

```python
vals = [
    0b01000011,
    0b01010011,
    0b01000011,
    0b01000111,
    0b01111011,
    0b01100001,
    0b01011111,
    0b01000110,
    0b01101100,
    0b00110100,
    0b01100111,
    0b01111101,
]
print("".join(map(chr, vals)))
```

Flag: `CSCG{a_Fl4g}`
