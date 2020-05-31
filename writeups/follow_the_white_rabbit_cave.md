# Follow The White Rabbit - Cave

The challenge gives us a zip file with a game.

Looking at the extracted files we can see a `UnityCrashHandler.exe` and `UnityPlayer.dll`
so clearly the game was written in Unity.

The challenge seems to be to follow the white rabbit into the large hole on the hill
but the problem is that the damage from the fall always kills us.

There are a number of ways to solve this challenge:


## Solution 1: Patching the fall damage code

Since Unity code is usually written in `C#` using .NET Mono we can easily reverse engineer the code
using a tool like `dnSpy`.

The custom code is in `FollowWhiteRabbit_Data/Managed/Assembly-CSharp.dll`.

Looking through the code a bit or searching for `death` we can quickly find a method `PlayerController.CheckFallDeath()`
that checks if the player hit the ground with too much speed and kills him if that is the case:

```c#
private void CheckFallDeath() {
    if (this.m_IsGrounded && this.m_VerticalSpeed < -(this.maxGravity - 0.1f)) {
        this.Die();
    }
}
```

Using `dnSpy` we can simply replace the method body so it does nothing.

Now we can jump down the hole without dying, follow the rabbit a bit further and see the flag: `CSCG{data_mining_teleport_or_gravity_patch?}`


## Solution 2: Finding the cheat code

If we couldn't simply jump into the hole, e.g. because of an invisible barrier or if we didn't find
the fall damage check there is actually a hidden cheat code in the game.

In the `Update` method of `UILoader` we can find this code:

```c#
if (Input.GetKey(KeyCode.F) && Input.GetKey(KeyCode.L) && Input.GetKey(KeyCode.A) && Input.GetKeyDown(KeyCode.G)) {
    if (this.toggle2.activeSelf) {
        this.toggle2.SetActive(false);
        this.toggle1.SetActive(true);
        this.toggle2.GetComponentInChildren<PlayerInput>().enabled = false;
        this.toggle1.GetComponentInChildren<PlayerInput>().enabled = true;
        return;
    }
    this.toggle1.SetActive(false);
    this.toggle2.SetActive(true);
    this.toggle1.GetComponentInChildren<PlayerInput>().enabled = false;
    this.toggle2.GetComponentInChildren<PlayerInput>().enabled = true;
}
```

It seems to do something when the keys `FLAG` are all pressed at the same time.

This didn't work for me since my keyboard is quite bad and has issues with Ghosting.

You can use a website like [this](https://drakeirving.github.io/MultiKeyDisplay/) to check if your keyboard can do it.

My keyboard isn't able to register all four of the keys at the same time so I'm not able to use the cheat code.

However, we can just use `dnSpy` again to patch the code so the cheat triggers when just the `F` button is pressed:

```c#
if (Input.GetKey(KeyCode.F)) {
    // ...
}
```

If we now run the game and press `F` we are instantly teleported into the hole and can read the flag.


## Solution 3: Datamining

If, for some reason, we couldn't easily read or decompile the source code for example because
it was obfuscated there is also a way to get the flag without touching the code.

Using a tool like [uTinyRipper](https://github.com/mafaca/UtinyRipper) we can extract all the assets from the game.

Looking through the assets we can find a texture at `Assets/Texture2D/flag1.png` which also contains the flag:

![](follow_the_white_rabbit_flag1.png)
