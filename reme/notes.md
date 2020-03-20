# Part 1

```python
assert args[0] == StringEncryption.Decrypt("D/T9XRgUcKDjgXEldEzeEsVjIcqUTl7047pPaw7DZ9I=")
```

Use ILSpy to decompile `StringEncryption.Decrypt`:

```c#
using System;
using System.IO;
using System.Security.Cryptography;
using System.Text;

public class Program {
    public static void Main() {
        Console.WriteLine(Decrypt("D/T9XRgUcKDjgXEldEzeEsVjIcqUTl7047pPaw7DZ9I="));
    }

    public static string Decrypt(string cipherText) {
        string password = "A_Wise_Man_Once_Told_Me_Obfuscation_Is_Useless_Anyway";
        cipherText = cipherText.Replace(" ", "+");
        byte[] array = Convert.FromBase64String(cipherText);
        using (Aes aes = Aes.Create()) {
            Rfc2898DeriveBytes rfc2898DeriveBytes = new Rfc2898DeriveBytes(password, new byte[13] {73,118,97,110,32,77,101,100,118,101,100,101,118});
            aes.Key = rfc2898DeriveBytes.GetBytes(32);
            aes.IV = rfc2898DeriveBytes.GetBytes(16);
            MemoryStream val = (MemoryStream)(object)new MemoryStream();
            try {
                using (CryptoStream cryptoStream = new CryptoStream((Stream)(object)val, aes.CreateDecryptor(), CryptoStreamMode.Write))
                {
                    ((Stream)cryptoStream).Write(array, 0, array.Length);
                    ((Stream)cryptoStream).Close();
                }
                cipherText = Encoding.get_Unicode().GetString(val.ToArray());
            } finally {
                ((IDisposable)val)?.Dispose();
            }
        }
        return cipherText;
    }
}
```

Flag: `CSCG{CanIHazFlag?}`


# Part 2

```c#
// Get IL bytecode of `InitialCheck` method
byte[] InitialCheckIL = typeof(Program).GetMethod("InitialCheck", (BindingFlags)40).GetMethodBody().GetILAsByteArray();

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

## InitialCheck IL bytes

Use `ildisasm /hex` and `hexdump` to extract bytes.

```
00 28 10 00 00 06 00 28 2F 00 00 0A 0C 08 2C 14 00 72 C3 00 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 17 0A 28 32 00 00 0A 6F 33 00 00 0A 12 00 28 08 00 00 06 26 06 0D 09 2C 14 00 72 C3 00 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 28 09 00 00 06 13 04 11 04 2C 14 00 72 C3 00 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 02 8E 16 FE 01 13 05 11 05 2C 14 00 72 CD 00 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 02 16 9A 72 11 01 00 70 28 13 00 00 06 28 34 00 00 0A 13 06 11 06 2C 16 00 72 C3 00 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 2B 10 00 72 6B 01 00 70 02 16 9A 28 35 00 00 0A 00 00 72 E3 01 00 70 28 0A 00 00 06 0B 07 7E 36 00 00 0A 28 37 00 00 0A 13 07 11 07 2C 37 00 07 72 FD 01 00 70 28 0B 00 00 06 13 08 11 08 28 38 00 00 0A 20 E9 00 00 00 FE 01 13 09 11 09 2C 14 00 72 33 02 00 70 28 30 00 00 0A 00 15 28 31 00 00 0A 00 00 00 2A
```

# Decrypt IL

```c#
using System;
using System.IO;
using System.Security.Cryptography;

public class Program {
    public static void Main() {
        byte[] encrypted = new byte[] {/* omitted */};
        byte[] pwd = new byte[] {/* omitted */};
        byte[] decrypted = AES_Decrypt(encrypted, pwd);
        Console.WriteLine(BitConverter.ToString(decrypted).Replace("-"," "));
    }

    public static byte[] AES_Decrypt(byte[] bytesToBeDecrypted, byte[] passwordBytes)
    {
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

## Decompile inner

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

## Brute force MD5 hash or loop it up

```python
import hashlib, string, itertools

for i in range(10):
    for g in itertools.product(string.ascii_letters + string.digits, repeat=i):
        if hashlib.md5("".join(g).encode()).hexdigest() == "b72f3bd391ba731a35708bfd8cd8a68f":
            print(g)
            exit()
```

Loop it up: <https://md5.gromweb.com/?md5=b72f3bd391ba731a35708bfd8cd8a68f> => `dynamic`

Flag: `CSCG{n0w_u_know_st4t1c_and_dynamic_dotNet_R3333}`
