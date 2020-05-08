## Part 2

- Dump process file: `volatility -f memory.dmp --profile=WinXPSP3x86 procdump -p 1920 --dump-dir=./`
- `strings x.exe | grep flag`
  - `That is the correct flag`
  - `Looks like the wrong flag -.-`
- IDA
  - Strings subview
  - Look for `That is the correct flag`
  - Leads to function `TForm1_Button1Click`
- idr Delphi Decompiler

```cpp
int __fastcall TForm1_Button1Click(int a1)
{
  int v1; // ebx
  int v2; // edx
  int v3; // eax
  int v4; // ebx
  int v5; // ebx
  char v6; // zf
  unsigned int v8; // [esp-10h] [ebp-40h]
  unsigned int v9; // [esp-Ch] [ebp-3Ch]
  void *v10; // [esp-8h] [ebp-38h]
  int *v11; // [esp-4h] [ebp-34h]
  int v12; // [esp+4h] [ebp-2Ch]
  char v13; // [esp+8h] [ebp-28h]
  int v14; // [esp+18h] [ebp-18h]
  int v15; // [esp+1Ch] [ebp-14h]
  int v16; // [esp+20h] [ebp-10h]
  int v17; // [esp+24h] [ebp-Ch]
  int v18; // [esp+28h] [ebp-8h]
  int v19; // [esp+2Ch] [ebp-4h]
  int savedregs; // [esp+30h] [ebp+0h]

  v1 = a1;
  v11 = &savedregs;
  v10 = &loc_4554FB;
  v9 = __readfsdword(0);
  __writefsdword(0, (unsigned int)&v9);
  must_be_true = 0;
  Controls::TControl::GetText(*(Controls::TControl **)(a1 + 768));
  dword_458DD8 = unknown_libname_69(v19);
  dword_458DE8 = 0;
  LOBYTE(v2) = 1;
  dword_458DE0 = unknown_libname_42(&off_453B34, v2);
  System::__linkproc__ LStrAsg(&unk_458DFC, &str_1EFC99B6046A0F2[1]);
  if ( dword_458DD8 > 0 )
  {
    Controls::TControl::GetText(*(Controls::TControl **)(v1 + 768));
    v3 = System::__linkproc__ LStrToPChar(v18);
    unknown_libname_65(&dword_458DD4, v3);
    if ( *(_BYTE *)dword_458DD4 == 67 )
    {
      System::__linkproc__ LStrAsg(&unk_458E08, &str_25DB3350B389538[1]);
      if ( *((_BYTE *)dword_458DD4 + 2) == 67 && *((_BYTE *)dword_458DD4 + 3) == 71 )
      {
        System::__linkproc__ LStrAsg(&unk_458E00, &str_C129BD7796F23B9[1]);
        if ( *((_BYTE *)dword_458DD4 + 1) == 83 )
        {
          System::__linkproc__ LStrAsg(&unk_458E0C, &str_40A00CA65772D7D[1]);
          if ( *((_BYTE *)dword_458DD4 + 4) == 123 )
          {
            System::__linkproc__ LStrAsg(&unk_458E04, &str_017EFBC5B1D3FB2[1]);
            if ( *((_BYTE *)dword_458DD4 + dword_458DD8 - 1) == 125 )
            {
              v4 = dword_458DD8;
              if ( dword_458DD8 > 0 )
              {
                dword_458DEC = 1;
                do
                {
                  if ( *((_BYTE *)dword_458DD4 + dword_458DEC - 1) == 95 )
                    ++dword_458DE8;
                  ++dword_458DEC;
                  --v4;
                }
                while ( v4 );
              }
              if ( dword_458DE8 == 4 )
              {
                must_be_true = -1;
                Compprod::TComponentsPageProducer::HandleTag(dword_458DD4, 6, (Classes::TStrings *)(dword_458DD8 - 6));
                System::__linkproc__ LStrAsg(&dword_458DD4, v17);
                v5 = dword_458DE8 + 1;
                if ( dword_458DE8 + 1 > 0 )
                {
                  dword_458DF0 = 1;
                  do
                  {
                    dword_458DEC = sub_425500(&str___5[1], dword_458DD4, 1);
                    dword_458DDC = unknown_libname_69((int)dword_458DD4);
                    if ( !dword_458DEC )
                      dword_458DEC = dword_458DDC + 1;
                    sub_4254AC(dword_458DD4, dword_458DEC - 1, &v16);
                    System::__linkproc__ LStrAsg(&dword_458DF4, v16);
                    sub_4252C8(dword_458DF4, &v15);
                    System::__linkproc__ LStrAsg(&dword_458DF4, v15);
                    unknown_libname_771(dword_458DE0, dword_458DF4, &v13);
                    Idhash::TIdHash128::AsHex(*(_DWORD *)dword_458DE0, &v13, &v14);
                    System::__linkproc__ LStrAsg(&dword_458DE4, v14);
                    System::__linkproc__ LStrCmp(dword_458DF8[dword_458DF0], dword_458DE4);
                    if ( !v6 )
                      must_be_true = 0;
                    sub_4254C4((int)dword_458DD4, dword_458DDC - dword_458DEC, (int)&v12);
                    System::__linkproc__ LStrAsg(&dword_458DD4, v12);
                    ++dword_458DF0;
                    --v5;
                  }
                  while ( v5 );
                }
              }
            }
          }
        }
      }
    }
  }
  if ( (unsigned int)must_be_true >= 1 == 1 )
    Forms::TApplication::MessageBox(*(Forms::TApplication **)off_4577E4, "That is the correct flag", "Correnct", 64);
  else
    Forms::TApplication::MessageBox(
      *(Forms::TApplication **)off_4577E4,
      "Looks like the wrong flag -.-",
      "WRONG :P",
      16);
  __writefsdword(0, v8);
  v10 = &loc_455502;
  System::__linkproc__ LStrClr(&v12);
  System::__linkproc__ LStrArrayClr(&v14, 4);
  return System::__linkproc__ LStrArrayClr(&v18, 2);
}
```

Hashes of words:
1EFC99B6046A0F2C7E8C7EF9DC416323
25DB3350B38953836C36DFB359DB4E27
C129BD7796F23B97DF994576448CAA23
40A00CA65772D7D102BB03C3A83B1F91
017EFBC5B1D3FB2D4BE8A431FA6D6258

Found in hash db:
- `0ld       dl0     1efc99b6046a0f2c7e8c7ef9dc416323`
- `cr4ck     kc4rc   25DB3350B38953836C36DFB359DB4E27`
- `m3!       !3m     40A00CA65772D7D102BB03C3A83B1F91`

Nowhere in memory (reversed, normal, wide-char)
`volatility -f memory.dmp --profile=WinXPSP3x86 memdump -p 1920 --dump-dir=./`
`volatility -f memory.dmp --profile=WinXPSP3x86 memmap -p 1920 --dump-dir=./`

By brute-forcing:
- `sch00l    l00hcs  C129BD7796F23B97DF994576448CAA23`
- `d31ph1    1hp13d  017EFBC5B1D3FB2D4BE8A431FA6D6258`

Code:
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

Flag: `CSCG{0ld_sch00l_d31ph1_cr4ck_m3!}`
