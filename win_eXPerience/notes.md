
E:\password.txt
d.txt
cscg-forensic
E:\flag.txt

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

Probably `WinXPSP3x86`

```
$ volatility -f memory.dmp --profile=WinXPSP3x86 pstree
Name                                                  Pid   PPid   Thds   Hnds Time
-------------------------------------------------- ------ ------ ------ ------ ----
 0x81bcca00:System                                      4      0     53    262 1970-01-01 00:00:00 UTC+0000
. 0x81a04da0:smss.exe                                 340      4      3     21 2020-03-22 18:27:38 UTC+0000
.. 0x81a41950:winlogon.exe                            524    340     19    428 2020-03-22 18:27:39 UTC+0000
... 0x81a2d810:lsass.exe                              644    524     23    356 2020-03-22 18:27:39 UTC+0000
... 0x816d8cd8:wpabaln.exe                            988    524      1     66 2020-03-22 18:29:38 UTC+0000
... 0x8197eda0:services.exe                           632    524     16    262 2020-03-22 18:27:39 UTC+0000
.... 0x81abd0f0:svchost.exe                          1024    632     67   1298 2020-03-22 18:27:39 UTC+0000
..... 0x81768310:wuauclt.exe                         1300   1024      7    174 2020-03-22 18:28:35 UTC+0000
..... 0x817a9b28:wscntfy.exe                         1776   1024      1     36 2020-03-22 18:28:51 UTC+0000
.... 0x81a0cda0:VBoxService.exe                       792    632      9    118 2020-03-22 18:27:39 UTC+0000
.... 0x816e41f0:svchost.exe                          1688    632      9     93 2020-03-22 18:28:00 UTC+0000
.... 0x81abf9a8:svchost.exe                           928    632      9    259 2020-03-22 18:27:39 UTC+0000
.... 0x8172abc0:svchost.exe                           548    632      8    129 2020-03-22 18:27:51 UTC+0000
.... 0x8194dc70:svchost.exe                          1076    632      6     74 2020-03-22 18:27:39 UTC+0000
.... 0x817b2318:spoolsv.exe                          1536    632     14    113 2020-03-22 18:27:40 UTC+0000
.... 0x81a16500:svchost.exe                           840    632     20    204 2020-03-22 18:27:39 UTC+0000
.... 0x817da020:svchost.exe                          1120    632     18    219 2020-03-22 18:27:39 UTC+0000
.... 0x81759820:alg.exe                              1176    632      6    100 2020-03-22 18:27:51 UTC+0000
.. 0x81a46928:csrss.exe                               496    340      9    387 2020-03-22 18:27:39 UTC+0000
 0x817b33c0:explorer.exe                             1524   1484     14    353 2020-03-22 18:27:40 UTC+0000
. 0x8173ec08:CSCG_Delphi.exe                         1920   1524      1     29 2020-03-22 18:27:45 UTC+0000
. 0x8176c378:mspaint.exe                              264   1524      4    102 2020-03-22 18:27:48 UTC+0000
. 0x816d8438:TrueCrypt.exe                            200   1524      1     44 2020-03-22 18:28:02 UTC+0000
. 0x817cd690:ctfmon.exe                              1652   1524      1     66 2020-03-22 18:27:40 UTC+0000
. 0x81794608:VBoxTray.exe                            1644   1524     12    122 2020-03-22 18:27:40 UTC+0000
. 0x81791020:msmsgs.exe                              1660   1524      4    169 2020-03-22 18:27:40 UTC+0000
```

Interesting:
- `CSCG_Delphi.exe`
- `mspaint.exe`
- `TrueCrypt.exe`

Interesting:
- `C:\Documents and Settings\CSCG\Desktop\CSCG\CSCG_Delphi.exe`

No output from `cmdscan` and `consoles`.

Dump files: `volatility -f memory.dmp --profile=WinXPSP3x86 filescan`

- `0x0000000001a3c7e8      1      0 R--rwd \Device\TrueCryptVolumeE\flag.zip`
- `0x0000000001717be8      1      0 R--rwd \Device\TrueCryptVolumeE\password.txt`
- `0x000000000178a898      2      1 RW---- \Device\HarddiskVolume1\Program Files\TrueCrypt\true.dmp`

```
$ volatility -f memory.dmp --profile=WinXPSP3x86 clipboard
Session    WindowStation Format                 Handle Object     Data
---------- ------------- ------------------ ---------- ---------- --------------------------------------------------
         0 WinSta0       CF_UNICODETEXT        0x500b5 0xe1d523d8 BorlandDelphiIsReallyCool
```

Dump `flag.zip`: `volatility -f memory.dmp --profile=WinXPSP3x86 dumpfiles -Q 0x0000000001a3c7e8 -n -D ./`
Password protected

Dump `password.txt`
Binary file

```
$ hexdump -C *pa*
00000000  42 6f 72 6c 61 6e 64 44  65 6c 70 68 69 49 73 52  |BorlandDelphiIsR|
00000010  65 61 6c 6c 79 43 6f 6f  6c 00 00 00 00 00 00 00  |eallyCool.......|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00001000
```

Extract `flag.zip` using `BorlandDelphiIsReallyCool` to get the flag.

Flag: `CSCG{c4ch3d_p455w0rd_fr0m_0p3n_tru3_cryp1_c0nt41n3r5}`
