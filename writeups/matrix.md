# Matrix

For the challenge we just get a single audio file `matrix.wav`.

The description of the challenge is quite strange. Some letters use a different
style and spell out `ｉｙｒｎｅｔｅ`.
Some of the spaces between the words are also en-spaces, em-spaces or thin-spaces
(`&ensp;`, `&emsp;` and `&thinsp`)
instead of the normal space character.
However I didn't find any hidden meaning in all that and it isn't relevant for the challenge.

## Layer 1

Listening to the audio file we can hear a quote from the Matrix movie that repeats a bunch of times.

Altough sometimes the quote is missing a small part in the beginning this
only happens a few times and doesn't look like a proper pattern.

However looking at the file in `Sonic Visualiser` we can see something
very interesting hidden in the spectogramm:

!(The password is: Th3-R3D-P1ll?)[./pwd.png]

The spectogram spells out `The password is: Th3-R3D-P1ll?`.

There must be some password encrypted data hidden in the file.
And indeed we can find something using `steghide`:

```
$ steghide extract -sf matrix/matrix.wav -p 'Th3-R3D-P1ll?'
wrote extracted data to "redpill.jpg".
```

## Layer 2

We get an image `redpill.jpg` of a German amusement park.

Using `binwalk` we can find a hidden zip archive after the image data that contains a `secret.txt` file:
```
$ binwalk redpill.jpg

DECIMAL       HEXADECIMAL     DESCRIPTION
--------------------------------------------------------------------------------
0             0x0             JPEG image data, JFIF standard 1.01
906949        0xDD6C5         Zip archive data, encrypted at least v1.0 to extract, compressed size: 38, uncompressed size: 26, name: secret.txt
907151        0xDD78F         End of Zip archive, footer length: 22
```

We can extract the file using `binwalk -e redpill.jpg` however the zip archie is password protected.

Taking a close look at the image we can see some strange green and blue dots at the bottom right of the image.

Interpreting the blue dots as `0` and the green as `1` we get: `0110111000100001010000110011001101011111010100000101011100111111`

That's exactly 64 bits so this looks promissing. Using Python we can convert decode the bits as an ASCII string:

```python
>>> bytes.fromhex(f"{0b0110111000100001010000110011001101011111010100000101011100111111:x}")
b'n!C3_PW?'
```

And we get the password: `n!C3_PW?`. We can now extract `secret.txt` from the zip archive.

## Layer 3

The `secret.txt` contains some random looking characters: `6W6?BHW,#BB/FK[?VN@u2e>m8`.

This is probably the flag encoded in some way. It doesn't look like Base64 but
after some searching around I found out there is also the somewhat less known Base85
which uses exactly the characters in the file.

And indeed using an online Base85 decode like [this](https://cryptii.com/pipes/ascii85-encoding) we can get the flag: `CSCG{St3g4n0_M4s7eR}`.
