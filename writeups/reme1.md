# Reme Part 1

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
    // ...
}
```

This is also the only function needed for the first flag.
The first thing that this function does is call another function called `Initialize`:
```c#
private static void InitialCheck(string[] args) {
    Initialize();
    // ...
}
```

That function is `unsafe`, really complicated and doesn't seem to do anything useful besides calling `VirtualProtect` a bunch of times,
so I let's ignore it for now.

The next thing `InitialCheck` does is checking if a debugger is present in three different ways:
```c#
if (Debugger.IsAttached) {
    Console.WriteLine("Nope");
    Environment.Exit(-1);
}
bool isDebuggerPresent = true;
CheckRemoteDebuggerPresent(Process.GetCurrentProcess().Handle, ref isDebuggerPresent);
if (isDebuggerPresent) {
    Console.WriteLine("Nope");
    Environment.Exit(-1);
}
if (IsDebuggerPresent()) {
    Console.WriteLine("Nope");
    Environment.Exit(-1);
}
```

As we are doing static reverse engineering we don't really care about debugger checks.

The function then checks if at least one argument is present and prints a help message otherwise:
```c#
if (args.Length == 0) {
    Console.WriteLine("Usage: ReMe.exe [password] [flag]");
    Environment.Exit(-1);
}
```

It looks like the binary first wants a password and then a flag to check.

The next thing the function does is decrypting a string and checking if the result is the same as the user provided password:

```c#
if (args[0] != StringEncryption.Decrypt("D/T9XRgUcKDjgXEldEzeEsVjIcqUTl7047pPaw7DZ9I=")) {
    Console.WriteLine("Nope");
    Environment.Exit(-1);
} else {
    Console.WriteLine("There you go. Thats the first of the two flags! CSCG{{{0}}}", args[0]);
}
```

It looks like the password is the first flag.

After that the function also does another check for a remote debugger but we still don't care about that.
Although remote debugging could help us find the flag it's probably more complicated to set up
than just solving the first part with static reverse engineering.

```c#
IntPtr moduleHandle = GetModuleHandle("kernel32.dll");
if (moduleHandle != IntPtr.Zero) {
    IntPtr procAddress = GetProcAddress(moduleHandle, "CheckRemoteDebuggerPresent");
    if (Marshal.ReadByte(procAddress) == 233) {
        Console.WriteLine("Nope!");
        Environment.Exit(-1);
    }
}
```

So what we want to do now is decrypt `"D/T9XRgUcKDjgXEldEzeEsVjIcqUTl7047pPaw7DZ9I="`.
Given that we have the code for the decryption function we can just run it to tell us the result.
Because I didn't have `.NET Core 2.2` installed I just used [.NET Fiddle](https://dotnetfiddle.net/) to run the code.

We also have to replace the generated accessor function `Encoding.get_Unicode()` with the original accessor `Encoding.Unicode`,
because we can't directly call the internal accessor functions in real code:

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
            MemoryStream val = new MemoryStream();
            try {
                using (CryptoStream cryptoStream = new CryptoStream(val, aes.CreateDecryptor(), CryptoStreamMode.Write)) {
                    cryptoStream.Write(array, 0, array.Length);
                    cryptoStream.Close();
                }
                cipherText = Encoding.Unicode.GetString(val.ToArray());
            } finally {
                val?.Dispose();
            }
        }
        return cipherText;
    }
}
```

And this gives us the flag: `CSCG{CanIHazFlag?}`

Having a look at the code it seems to use proper builtin (and therefore not self-made) cryptographic functions
and uses `AES` to de-/encrypt the password which in itself is secure but obviously that's as useless as obfuscation
if the password for decryption is stored together with the code.

In this case, a symmetric cipher clearly isn't the right tool for the job. Instead, the password should
be hashed using a strong cryptographic hash function suitable for passwords like PBKDF2, bcrypt, or scrypt.
To check the password the program can then hash the provided password with the same function and check if the results match.
This way only the hashed password must be stored in the binary and the original password can not be reconstructed from that.
