# Intro to Stegano 3

For the challenge we just get a single image `chall.png` that looks like the drawing of a child.

Running `binwalk` on the challenge shows that there is a zip archive hidden after the image data
and the archive contains a file `flag.txt`:

```
$ binwalk chall.png

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             PNG image, 676 x 437, 8-bit/color RGBA, non-interlaced
99            0x63            Zlib compressed data, best compression
299068        0x4903C         Zip archive data, encrypted compressed size: 48, uncompressed size: 28, name: flag.txt
299266        0x49102         End of Zip archive
```

We can use `binwalk -e chall.png` to extract the archive from the picture.

However the extracted `flag.txt` file is empty and if we check the carved out zip archive
we can see that the reason for this is that the archive is password protected.

To find the password we need to have another look at the image.
The biggest part of the image is covered by a blue sky with a very uniform color.

If we use an image editor like GIMP to fill the sky in with another color
we can see that some parts of the sky have a slightly different color which hides the password:

![s33_m3_1f_y0u_c4n](./chall_filled.png)

We can now extract the zip file using `s33_m3_1f_y0u_c4n` as the password:

```
$ 7z e -ps33_m3_1f_y0u_c4n _chall.png.extracted/4903C.zip
$ cat flag.txt
CSCG{H1dden_1n_pla1n_s1ght}
```

And we get the flag: `CSCG{H1dden_1n_pla1n_s1ght}`
