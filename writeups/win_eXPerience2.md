# win_eXPerience 2

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

Using `pstree` we can take a look at the processes that were running when the memory dump was taken:

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

For this challenge the interesting one is `CSCG_Delphi.exe`.

We can use `procdump` to dump the image of the process:

```
$ volatility -f memory.dmp --profile=WinXPSP3x86 procdump -p 1920 --dump-dir=./
```

As a result we get `executable.1920.exe` which immediately gets flagged by `Windows Defender`.

After telling `Windows Defender` to shut up and opening the binary in IDA we can see the binary contains a lot of functions.

Searching around for a bit we can find two interesting strings: `That is the correct flag` and `Looks like the wrong flag -.-`.

Looking for functions that use the strings we can find `TForm1_Button1Click`.

The function decompilation is quite unreadable but it looks like the function
is executed when a button is clicked. It then reads some input from a textbox,
does some check and tells us if the input was the correct flag.

From the process name we can guess that the binary was probably written in Delphi
so maybe we can use some Delphi-specific tools to get a better result.

Using the Interactive Delphi Reconstructor (idr) we indeed get a much better decompilation.
While the decompiled program has some other problems it at least tells us exactly which functions from
the Delphi standard libary get called.

Together with the output from IDA we can reconstruct the program source code to something like this:

```delphi
procedure TForm1.Button1Click(Sender:TObject);
begin
  try
    flag_correct := false;
    user_input := str_edit.GetText;
    user_input_length := Length(user_input);
    word_count := 1;
    tid_hash_msg_digest_5 := TIdHashMessageDigest5.Create;

    gvar_00458DFC := '1EFC99B6046A0F2C7E8C7EF9DC416323';
    gvar_00458E08 := '25DB3350B38953836C36DFB359DB4E27';
    gvar_00458E00 := 'C129BD7796F23B97DF994576448CAA23';
    gvar_00458E0C := '40A00CA65772D7D102BB03C3A83B1F91';
    gvar_00458E04 := '017EFBC5B1D3FB2D4BE8A431FA6D6258';

    if (user_input_length > 0)
        and (user_input[1] = 'C')
        and (user_input[2] = 'S')
        and (user_input[3] = 'C')
        and (user_input[4] = 'G')
        and (user_input[5] = '{')
        and (user_input[user_input_length] = '}') then
    begin
      for i := 1 to user_input_length do
        if user_input[i] = '_' then
          word_count += 1;
        end;
      end

      if word_count = 5 then
      begin

        flag_correct := true;
        user_input := AnsiMidStr(user_input, 6, user_input_length - 6);

        for i := 1 to word_count do
        begin
          underscore_pos := Pos('_', user_input);
          len := Length(user_input);
          if underscore_pos = 0 then
            underscore_pos := len + 1;
          end;
          curr_word := AnsiLeftStr(user_input, underscore_pos - 1);
          curr_word := AnsiReverseString(curr_word);
          hash_val := tid_hash_msg_digest_5.HashValue(curr_word);
          hash := tid_hash_msg_digest_5.AsHex(hash_val);

          if gvar_00458DF8[i] <> hash then
            flag_correct := false;
          end;

          user_input := AnsiRightStr(user_input, len - underscore_pos);
        end;
      end;
    end;

    if flag_correct then
      Application.MessageBox('That is the correct flag', 'Correnct');
      Exit;
    else
      Application.MessageBox('Looks like the wrong flag -.-', 'WRONG :P');
    end;

  finally
    user_input := '';
  end;
end;
```

This isn't quite valid Delphi but it's good enough to see what the function does.

We can see that it checks that the user input starts with `CSCG{` and ends with `}`.

It then splits everything in between by `_`, reverses the words, hashes each using a `TIdHash` and checks if the result is the expected value.

Checking the Delphi documentation we can find out that `TidHash` is just `MD5` and these are the correct hashes in the right order:

```
1EFC99B6046A0F2C7E8C7EF9DC416323
C129BD7796F23B97DF994576448CAA23
017EFBC5B1D3FB2D4BE8A431FA6D6258
25DB3350B38953836C36DFB359DB4E27
40A00CA65772D7D102BB03C3A83B1F91
```

Using some `MD5` hash databases we can easily crack 3 of the five hashes:
```
1efc99b6046a0f2c7e8c7ef9dc416323   dl0     0ld 
25DB3350B38953836C36DFB359DB4E27   kc4rc   cr4ck 
40A00CA65772D7D102BB03C3A83B1F91   !3m     m3!
```

It looks like the words mostly contain lower case letters and numbers so let's try brute-forcing the hashes using some Rust code:

```rust
const ONE: [u8; 16] = *b"\xc1)\xbdw\x96\xf2;\x97\xdf\x99EvD\x8c\xaa#";
const TWO: [u8; 16] = *b"\x01~\xfb\xc5\xb1\xd3\xfb-K\xe8\xa41\xfambX";

const ALPHA: [u8; 36] = *b"abcdefghijklmnopqrstuvwxyz0123456789";

fn main() {
    let one = md5::Digest(ONE);
    let two = md5::Digest(TWO);

    for &a in ALPHA.iter() {println!("{}", a);
    for &b in ALPHA.iter() {
    for &c in ALPHA.iter() {
    for &d in ALPHA.iter() {
    for &e in ALPHA.iter() {
    for &f in ALPHA.iter() {
        let x = &[a,b,c,d,e,f];
        let digest = md5::compute(x);
        if digest == one || digest == two {
            println!("{:?}", x);
        }
    }}}}}}
}
```

After trying combinations with six characters we quickly crack the last two hashes:

```
C129BD7796F23B97DF994576448CAA23    l00hcs    sch00l
017EFBC5B1D3FB2D4BE8A431FA6D6258    1hp13d    d31ph1
```

Reversing and combining them in the correct order gives us the flag: `CSCG{0ld_sch00l_d31ph1_cr4ck_m3!}`

I guess the lesson from this challenge is it's not a good idea to separate something like a flag or a password
into multiple parts and hash them separately.

Cracking the hashes of multiple short strings is much easier than the hash of one large string.
Since we can crack each word independently the search space is much smaller.

If the program would simply hash the whole flag
it would have been easier to reverse but impossible to crack the flag.
