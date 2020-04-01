```
$ file chall.jpg
chall.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, comment: "alm1ghty_st3g4n0_pls_g1v_fl4g", baseline, precision 8, 1024x1128, frames 3
```

Comment header: `alm1ghty_st3g4n0_pls_g1v_fl4g`

```
$ steghide extract -sf chall.jpg -p "alm1ghty_st3g4n0_pls_g1v_fl4g"
wrote extracted data to "flag.txt".
$ cat flag.txt
CSCG{Sup3r_s3cr3t_d4t4}
```

Flag: `CSCG{Sup3r_s3cr3t_d4t4}`
