Filling blue background with another color reveals: `s33_m3_1f_y0u_c4n`

```
binwalk chall.png

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 676 x 437, 8-bit/color RGBA, non-interlaced
99            0x63            Zlib compressed data, best compression
299068        0x4903C         Zip archive data, encrypted compressed size: 48, uncompressed size: 28, name: flag.txt
299266        0x49102         End of Zip archive
```

`binwalk -e chall.png` to extract

```
$ tree
.
├── chall.png
├── _chall.png-0.extracted
│   ├── 4903C.zip
│   ├── 63
│   ├── 63.zlib
│   └── flag.txt
└── _chall.png.extracted
    ├── 4903C.zip
    ├── 63
    └── 63.zlib
```

```
$ 7z e -ps33_m3_1f_y0u_c4n _chall.png.extracted/4903C.zip
$ cat flag.txt
CSCG{H1dden_1n_pla1n_s1ght}
```

Flag: `CSCG{H1dden_1n_pla1n_s1ght}`
