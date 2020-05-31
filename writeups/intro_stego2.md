# Intro to Stegano 2

For the challenge we just get a single image `chall.jpg` of a city skyline.

The image looks fairly professional so it might be a stock photo.

Searching on https://tineye.com/ leads to [this](https://4.bp.blogspot.com/_fYHWkeTLPCo/TA5JadYuxaI/AAAAAAAACz8/kVschfpWrC4/s1600/Brisbane2.jpg) image which seems to be the original.

Comparing them we can immediately see a difference between which windows are lit in the building on the left.

The change is fairly sloppy so we can clearly see that a rectangle of windows in the top left corner of the building
was changed and it is 8 windows wide and 14 windows tall.

The width of 8 windows looks suspiciously like the 8 bits in a byte.

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

Since the first window/bit is always unlit/`0` taking each row as a bytes produces valid ASCII characters.

Using Python we can convert them to text:

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

And we indeed get the flag: `CSCG{a_Fl4g}`

Next: [Intro to Stegano 3](intro_stego3.md)
