# win_eXPerience 1

This challenge just gives us a 7zip archive `memory.7z`.

Extracting the file gives us a memory dump `memory.dmp`.

Given the challenge name it seems likely that the dump is from a Windows XP machine.

We can use [volatility](https://www.volatilityfoundation.org/) to explore the memory dump.

Let's first try `imageinfo` to see if the dump is really from Windows XP:

```
$ volatility -f memory.dmp imageinfo
          Suggested Profile(s) : WinXPSP2x86, WinXPSP3x86 (Instantiated with WinXPSP2x86)
                     AS Layer1 : IA32PagedMemory (Kernel AS)
                     AS Layer2 : VirtualBoxCoreDumpElf64 (Unnamed AS)
                     AS Layer3 : FileAddressSpace (/mnt/d/pwn/cscg2020/win_eXPerience/memory.dmp)
                      PAE type : No PAE
                           DTB : 0x39000L
                          KDBG : 0x8054c760L
          Number of Processors : 1
     Image Type (Service Pack) : 2
                KPCR for CPU 0 : 0xffdff000L
             KUSER_SHARED_DATA : 0xffdf0000L
           Image date and time : 2020-03-22 18:30:56 UTC+0000
     Image local date and time : 2020-03-22 10:30:56 -0800
```

Indeed, `volatility` suggests `WinXPSP2x86` or `WinXPSP3x86` i.e. 32-bit Windows XP with service pack 2 or 3.

Using `filescan` we can take a look at the files that can be found in the memory dump:

```
$ volatility -f memory.dmp --profile=WinXPSP3x86 filescan
Offset(P)            #Ptr   #Hnd Access Name
------------------ ------ ------ ------ ----
...
0x0000000001a3c7e8      1      0 R--rwd \Device\TrueCryptVolumeE\flag.zip
0x0000000001717be8      1      0 R--rwd \Device\TrueCryptVolumeE\password.txt
0x00000000017c90e8      1      0 R--rwd \Device\HarddiskVolume1\Documents and Settings\CSCG\Desktop\CSCG\cscg.flag.PNG
...
```

There are a lot of files in there but searching for `flag` we can find two interesting ones.

`flag.zip` seems to be on an encrypted `TrueCrypt` volume but it looks like the volume was open and decrypted
when the memory dump was taken so we can still read the files.

We can also find a `password.txt` file on the volume.

The challenge description tells us that the flag in the image is just an old leftover and not a real flag but let's still take a look at it as well.

We can extract the files using `dumpfiles` with the offset:
```
$ volatility -f memory.dmp --profile=WinXPSP3x86 dumpfiles -Q 0x0000000001a3c7e8 -n -D ./
```

The `flag.zip` archive is password protected but `password.txt` contains the password: `BorlandDelphiIsReallyCool`.

Using the password we can extract the archive and get a `flag.txt` file with the flag: `CSCG{c4ch3d_p455w0rd_fr0m_0p3n_tru3_cryp1_c0nt41n3r5}`.

Taking a look at the `cscg.flag.PNG` we can also see the old flag mentioned in the description: `CSCG{f0r3n51c_1ntr0_c0py_4nd_p45t3_buff3r_1n_xp}`.

While it isn't a real flag it still hints at something interesting.

Using `clipboard` we can see the conents of the clipboard when the memory dump was taken and this way we actually also find the password:

```
$ volatility -f memory.dmp --profile=WinXPSP3x86 clipboard
Session    WindowStation Format                 Handle Object     Data
---------- ------------- ------------------ ---------- ---------- --------------------------------------------------
         0 WinSta0       CF_UNICODETEXT        0x500b5 0xe1d523d8 BorlandDelphiIsReallyCool
```
