# Intro to Crypto 3

For this challenge, we again get four files: A text file `intercepted-message.txt` and three RSA public keys for the German, Russian, and US government.

The message file contains an encrypted message to each of the three governments.

Looking at the challenge description it seems likely that the message sent to each government is the same but each time encrypted with a different key corresponding to the respective government.

Looking at the [Twenty Years of Attacks on the RSA Cryptosystem](https://crypto.stanford.edu/~dabo/papers/RSA-survey.pdf) whitepaper
linked in the description of `Intro to Crypto 1` we can find a section about `Hastad's Broadcast Attack` that seems to apply to our situation.

Among other things, this attack allows one to recover the contents of an encrypted message from three or more ciphertexts
of the same message, each encrypted using a different key with a public exponent of 3.

More generally it allows an attacker to recover a message from `k` ciphertexts of the same message, each encrypted with a different key
with public exponent `e <= k`.

Using `openssl` we can easily see that all the given keys indeed have a public exponent of 3:

```
$ openssl rsa -pubin -in german_governemnt.pem -text -noout
...
Exponent: 3 (0x3)
```

Let's have a look at the details of the attack:

We have three RSA keys with moduli `N_ger`, `N_rus` and `N_us` and since they all have public exponent `e = 3` we have these three ciphertexts:
- `C_ger = M³ mod N_ger`
- `C_rus = M³ mod N_rus`
- `C_us = M³ mod N_us`

`M` denotes the original message we want to recover.

Using the chinese remainder theorem we can calculate `C = M³ mod N_ger * N_rus * N_us`.

This can be implemented with the following Python code:

```python
N = N_us * N_ger * N_rus
C = 0
for c, n in ((C_us, N_us), (C_ger, N_ger), (C_rus, N_rus)):
    m = N // n
    r, s = xgcd(n, m)
    C += c * s * m

C %= N
```

Since `M` must be smaller than all the moduli for RSA to work it follows that `M³ < N_ger * N_rus * N_us`
and therefore `C = M³`.

We can now simply find out `M` by calculating the cube-root of `C`.

Since the Python standard library doesn't contain a method for calculating integer cube-roots
and calculations on floating-point numbers won't be precise enough we have to implement it ourselves.

Luckily, code to calculate arbitrary integer roots in Python can easily be found on the internet.

The complete Python code to decrypt the message looks like this:

```python
from Cryptodome.Util.number import inverse, long_to_bytes
from Cryptodome.PublicKey import RSA

with open("us_government.pem") as f:
    N_us = RSA.import_key(f.read()).n

with open("german_government.pem") as f:
    N_ger = RSA.import_key(f.read()).n

with open("russian_government.pem") as f:
    N_rus = RSA.import_key(f.read()).n

C_ger = 3999545484320691620582760666106855727053549021662410570083429799334896462058097237449452993493720397790227435476345796746350169898032571754431738796344192821893497314910675156060408828511224220581582267651003911249219982138536071681121746144489861384682069580518366312319281158322907487188395349879852550922320727712516788080905540183885824808830769333571423141968760237964225240345978930859865816046424226809982967625093916471686949351836460279672029156397296634161792608413714942060302950192875262254161154196090187563688426890555569975685998994856798884592116345112968858442266655851601596662913782292282171174885

C_us = 7156090217741040585758955899433965707162947606350521948050112381514262664247963697650055668324095568121356193295269338497644168513453950802075729741157428606617001908718212348868412342224351012838448314953813036299391241983248160741119053639242636496528707303681650997650419095909359735261506378554601448197330047261478549324349224272907044375254024488417128064991560328424530705840832289740420282298553780466036967138660308477595702475699772675652723918837801775022118361119700350026576279867546392616677468749480023097012345473460622347587495191385237437474584054083447681853670339780383259673339144195425181149815

C_rus = 9343715678106945233699669787842699250821452729365496523062308278114178149719235923445953522128410659220617418971359137459068077630717894445019972202645078435758918557351185577871693207368250243507266991929090173200996910881754217374691865096976051997491208921880703490275111904577396998775470664002942232492755888378994040358902392803421017545356248082413409915177589953816030273082416979477368273328755386893089597798104163894528521114946660635364704437632205696975201216810929650384600357902888251066301913255240181601332549134854827134537709002733583099558377965114809251454424800517166814936432579406541946707525


def root(x, n):
    high = 1
    while high ** n < x:
        high *= 2
    low = high // 2
    while low < high:
        mid = ((low + high) // 2) + 1
        if low < mid and mid ** n < x:
            low = mid
        elif high > mid and mid ** n > x:
            high = mid
        else:
            return mid
    return mid + 1


def xgcd(a, b):
    """return (x, y) such that a*x + b*y = gcd(a, b)"""
    x0, x1, y0, y1 = 0, 1, 1, 0
    while a != 0:
        (q, a), b = divmod(b, a), a
        y0, y1 = y1, y0 - q * y1
        x0, x1 = x1, x0 - q * x1
    return x0, y0


N = N_us * N_ger * N_rus

C = 0
for c, n in ((C_us, N_us), (C_ger, N_ger), (C_rus, N_rus)):
    m = N // n
    r, s = xgcd(n, m)
    C += c * s * m

C %= N

M = root(C, 3)

print(long_to_bytes(M).decode())
```

Running it decrypts the message which contains some padding and the flag: `CSCG{ch1nes3_g0vernm3nt_h4s_n0_pr0blem_w1th_c0ron4}`.
