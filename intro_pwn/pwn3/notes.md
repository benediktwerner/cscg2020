## One gadgets

```
0xe6b93 execve("/bin/sh", r10, r12)
constraints:
  [r10] == NULL || r10 == NULL
  [r12] == NULL || r12 == NULL

0xe6b96 execve("/bin/sh", r10, rdx)
constraints:
  [r10] == NULL || r10 == NULL
  [rdx] == NULL || rdx == NULL

0xe6b99 execve("/bin/sh", rsi, rdx)
constraints:
  [rsi] == NULL || rsi == NULL
  [rdx] == NULL || rdx == NULL

0x10afa9 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
```

## Libc addresses

```
offset___libc_start_main_ret = 0x271e3
offset_system = 0x00000000000554e0
offset_dup2 = 0x0000000000111b60
offset_read = 0x0000000000111260
offset_write = 0x0000000000111300
offset_str_bin_sh = 0x1b6613
```

Flag: `CSCG{VOLDEMORT_DID_NOTHING_WRONG}`
