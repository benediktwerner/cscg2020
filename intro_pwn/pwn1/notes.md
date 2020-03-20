Vulnerable `gets` in `welcome()` and `AAAAAAAA()`.
Vulnerable `printf` in `welcome()`.

`main()` is at offset `0xaf4`.
`WINgardium_leviosa()` is at offset `0x9ec`, but the code for system only starts at offset `0xa14`.

## Exploit

1. Leak return address using `%39$p`
2. Override return address with address of `WINgardium_leviosa()` in second `gets`

Flag: `CSCG{NOW_PRACTICE_MORE}`
