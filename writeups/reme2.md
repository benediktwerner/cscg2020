# Reme Part 2

The challenge gives us a binary for `.NET Core 2.2`.

Because my antivirus immediately flagged the `.dll`,
I didn't have the right `.Net Core` version installed
and this is a Reverse Engineering challenge anyways
I didn't try to run the challenge
and instead immediately started decompiling the binary.

Although I didn't really believe that the challenge was dangerous,
which turned out to be true,
I still wouldn't have learned anything running it anyways.

Decompiling `ReMe.dll` in `ILSpy` shows three classes:
- `ByteArrayRocks`, which seems to implement some extension methods to find the position of a `byte[]` in another `byte[]`
- `StringEncryption`, which seems to provide de-/encryption for strings
- `Program`, the starting point of the binary

Looking at the `Program.Main` function we can see that it immediately calls a function called `InitialCheck`:
```c#
private static void Main(string[] args) {
    InitialCheck(args);
    // ..
}
```

This function checks if any (remote) debuggers are attached to the program and exits if that's the case.
Since we are doing static reverse engineering we can ignore that.
It also checks the first flag which we don't care about for this part.

Let's take a look what happens after that:
```c#
// Get IL bytecode of `InitialCheck` method
byte[] InitialCheckIL = typeof(Program).GetMethod("InitialCheck", 40).GetMethodBody().GetILAsByteArray();

// Get running assembly as bytes
byte[] assemblyBytes = File.ReadAllBytes(Assembly.GetExecutingAssembly().get_Location());
MemoryStream assemblyBytesStream = new MemoryStream(assemblyBytes);

// Locate "THIS_IS_CSCG_NOT_A_MALWARE!" in the assembly
bytes[] searchTerm = Encoding.ASCII.GetBytes("THIS_IS_CSCG_NOT_A_MALWARE!");
int location = assemblyBytes.Locate(searchTerm)[0];

// Extract bytes after "THIS_IS_CSCG_NOT_A_MALWARE!"
assemblyBytesStream.Seek(location + searchTerm.Length, 0);
byte[] encryptedIL = new byte[assemblyBytesStream.Length - assemblyBytesStream.Position];
assemblyBytesStream.Read(encryptedIL, 0, encryptedIL.Length);

// Decrypt and run
byte[] decryptedIL = AES_Decrypt(encryptedIL, InitialCheckIL);
Assembly.Load(decryptedIL).GetTypes()[0].GetMethod("Check", (BindingFlags)24)).Invoke(null, new object[1] { args });
```

The function first gets the `IL`-bytecode of the `InitialCheck` function which is later used as a key for decryption.
I assume this is to prevent any patching of the function at runtime which would enable
us to circumvent the debugger detection but since we are still doing static reverse engineering
we again don't care about that too much.

Next, it opens the running binary and searches for the ASCII-string `THIS_IS_CSCG_NOT_A_MALWARE!`.
It then takes all the bytes after that string, decrypts it with `AES` using the previously mentioned `IL`-bytecode
of `InitialCheck` as the key, then loads the resulting bytes as a `.NET assembly` and runs
the `Check` function of the first type in the assembly passing it the program arguments.

Looking at the binary using `hexdump` we can see that the binary indeed contains the string `THIS_IS_CSCG_NOT_A_MALWARE!`
and everything after that does look like random garbage which is what we would expect from encrypted data.
```
$ hexdump -C ReMe.dll
...
00003400  54 48 49 53 5f 49 53 5f  43 53 43 47 5f 4e 4f 54  |THIS_IS_CSCG_NOT|
00003410  5f 41 5f 4d 41 4c 57 41  52 45 21 46 a0 15 cc 72  |_A_MALWARE!F...r|
00003420  99 4c a2 a7 b1 9c 12 41  18 32 1b 0b ec 1d e1 27  |.L.....A.2.....'|
00003430  62 67 62 af 84 d5 af 11  0e 29 0c 57 d2 ed e7 ab  |bgb......).W....|
00003440  30 74 ed d1 3b bf aa f0  7f 24 aa fb 9f c2 c7 94  |0t..;....$......|
00003450  73 38 5a 2b f8 53 aa 86  07 7a 1f d8 78 f3 93 13  |s8Z+.S...z..x...|
00003460  28 f5 e6 43 ab 2f 27 21  f6 93 cd 0f 81 bb d2 8f  |(..C./'!........|
00003470  48 1d e2 cf da 74 32 b3  04 32 b8 28 80 3f 3a 65  |H....t2..2.(.?:e|
00003480  e7 fb 2a 55 fd 1c 1c 82  e0 d3 ba 27 aa e9 df 38  |..*U.......'...8|
00003490  d5 35 de 6e fb 06 9f c5  cc 8e d8 a5 5d 06 8f bf  |.5.n........]...|
000034a0  2c c2 e6 46 86 90 58 dc  9d f4 d1 d3 ee bd 34 d5  |,..F..X.......4.|
000034b0  ba 75 c0 6f 1c ac 60 d2  c8 fc ab 91 14 ec 6d b4  |.u.o..`.......m.|
...
```

So let's decrypt the data. We just need the key and then we can let `.NET` do the decryption
for us given that we already have all the code for it.

The key is just the `IL`-bytecode of the `InitialCheck` function, so we just need to find that.

Using `ildisasm /hex ReMe.dll` we can get the bytecode for the function as hex.

Then we can use [.NET Fiddle](https://dotnetfiddle.net/) to run the decryption code:
```c#
using System;
using System.IO;
using System.Security.Cryptography;

public class Program {
    public static void Main() {
        byte[] encrypted = new byte[] {/* omitted */};  // The bytes from the binary after "THIS_IS_CSCG_NOT|_A_MALWARE!"
        byte[] pwd = new byte[] {/* omitted */};        // The `IL`-bytecode of `InitialCheck` taken from `ildisasm`
        byte[] decrypted = AES_Decrypt(encrypted, pwd);
        Console.WriteLine(BitConverter.ToString(decrypted).Replace("-", " "));
    }

    public static byte[] AES_Decrypt(byte[] bytesToBeDecrypted, byte[] passwordBytes) {
        byte[] result = null;
        byte[] salt = new byte[8] {1,2,3,4,5,6,7,8};
        MemoryStream val = new MemoryStream();
        try {
            RijndaelManaged val2 = new RijndaelManaged();
            try {
                val2.KeySize = 256;
                val2.BlockSize = 128;
                Rfc2898DeriveBytes rfc2898DeriveBytes = new Rfc2898DeriveBytes(passwordBytes, salt, 1000);
                val2.Key = rfc2898DeriveBytes.GetBytes(val2.KeySize / 8);
                val2.IV = rfc2898DeriveBytes.GetBytes(val2.BlockSize / 8);
                val2.Mode = CipherMode.CBC;
                using (CryptoStream cryptoStream = new CryptoStream(val, val2.CreateDecryptor(), CryptoStreamMode.Write)) {
                    cryptoStream.Write(bytesToBeDecrypted, 0, bytesToBeDecrypted.Length);
                    cryptoStream.Close();
                }
                result = val.ToArray();
            } finally {
                val2?.Dispose();
            }
        } finally {
            val?.Dispose();
        }
        return result;
    }
}
```

This gives us the decrypted data as hex which we can then convert to a binary using a quick Python script:
```
$ cat hex2bytes.py
import fileinput, sys

for line in fileinput.input(sys.argv[1:]):
    print(*(f"0x{x}" for x in line.strip().split()), sep=",")

$ python3 hex2bytes.py decrypted.hex > decrypted.dll
```

Because the decrypted data is again a `.NET` binary we can again use `ILSpy` to decompile it.

It contains a single class `Inner`:
```c#
using System;
using System.Security.Cryptography;
using System.Text;

public class Inner {
    public static void Check(string[] args) {
        if (args.Length <= 1) {
            Console.WriteLine("Nope.");
            return;
        }
        string[] array = args[1].Split(new string[1] { "_" }, StringSplitOptions.RemoveEmptyEntries);
        if (array.Length != 8) {
            Console.WriteLine("Nope.");
        }
        else if (
                "CSCG{" + array[0] == "CSCG{n0w"
                && array[1] == "u"
                && array[2] == "know"
                && array[3] == "st4t1c"
                && array[4] == "and"
                && CalculateMD5Hash(array[5]).ToLower() == "b72f3bd391ba731a35708bfd8cd8a68f"
                && array[6] == "dotNet"
                && array[7] + "}" == "R3333}"
        ) {
            Console.WriteLine("Good job :)");
        }
    }

    public static string CalculateMD5Hash(string input) {
        MD5 md5 = MD5.Create();
        byte[] bytes = Encoding.ASCII.GetBytes(input);
        byte[] array = md5.ComputeHash(bytes);
        StringBuilder stringBuilder = new StringBuilder();
        for (int i = 0; i < array.Length; i++) {
            stringBuilder.Append(array[i].ToString("X2"));
        }
        return stringBuilder.ToString();
    }
}
```

We can see that it splits the provided flag on underscores and then checks if each part is correct.
However, one part is compared to an MD5 hash which we need to reverse.
Luckily, looking the hash up in an [MD5 datbase](https://md5.gromweb.com/?md5=b72f3bd391ba731a35708bfd8cd8a68f)
yields `dynamic`.

We can now reconstruct the complete flag: `CSCG{n0w_u_know_st4t1c_and_dynamic_dotNet_R3333}`.

Well, dynamic `.NET` reversing wasn't really necessary in either part, but ok.

It's just too simple to reconstruct code from `.NET IL` which is why there are great free decompilers like `ILSpy` out
there and it's not really a good idea to think it's secure obfuscation.

Of course, obfuscation should also never be the only security. The use of an `MD5` hash here
actually goes in the right direction, but of course, there are several problems. First, only a part is hashed and that
part is short and an English word, which is probably why it can be found in an `MD5` database.
Even without a database, seven letters of MD5 hash can easily be brute-forced.
If the whole flag where hashed it might be fine but even then `MD5` really shouldn't be used for passwords
as it's too fast to calculate and therefore brute-force.
Instead, a strong cryptographic hash function like PBKDF2, bcrypt, or scrypt should be used.
