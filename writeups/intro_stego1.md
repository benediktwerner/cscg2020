# Intro to Stegano 1

For the challenge we just get a single image `chall.jpg` of LiveOverflow.

Using the `file` command we can see there is a comment in the EXIF-metadata:
```
$ file chall.jpg
chall.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 72x72, segment length 16, comment: "alm1ghty_st3g4n0_pls_g1v_fl4g", baseline, precision 8, 1024x1128, frames 3
```

This doesn't look like a flag, but it surely has something to do with the challenge.

Indeed, after trying a few of the standard stegano tools we can find some hidden data with `steghide`
using `alm1ghty_st3g4n0_pls_g1v_fl4g` as the password:

```
$ steghide extract -sf chall.jpg -p "alm1ghty_st3g4n0_pls_g1v_fl4g"
wrote extracted data to "flag.txt".
$ cat flag.txt
CSCG{Sup3r_s3cr3t_d4t4}
```

The image contained a hidden file `flag.txt` with the flag: `CSCG{Sup3r_s3cr3t_d4t4}`.
