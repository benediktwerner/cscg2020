# StayWoke Shop

The [challenge website](http://staywoke.hax1.allesctf.net/) seems to be an online shop
for everything you ever wanted during the quarantine.

Playing around with the site for a bit we can add items to our cart,
view our cart and remove items again. Then we can go to checkout
where we can enter a coupon and payment method and finish the purchase.

However, if we try to checkout using `w0kecoin` as payment method we always get `Wallet balance too low!`
and if we try to pay with `Desinfektionsmittel` we get `Payment method currently not supported!`


## Broken discounts

In some scrolling text at the top of the page we can read `20% Rabatt mit dem Code I<3CORONA` i.e. 20 percent
off with code `I<3CORONA`.

If we enter the code on the checkout page we indeed get 20 percent off.
Interestingly the discount is added to our cart as an item with a fixed negative price.

This means we can get a higher discount if we add more items to our cart,
enter the coupon code, and then remove some items again. If we add items worth `5€` to our cart
we get a discount of `1€` and we can then buy one of the items that cost `1€`.

However, none of the items give us anything when bought, so let's look around the page some more.


## Buying flags

The products are all shown on subpages with paths like `/products/2`.
But suspiciously there is no product with index `1`.

If we visit `/products/1` we can find a hidden product page
where we can buy a flag for `1337€`.

However, we get an error when we try to use a discount code with the flag in our cart.
If we look at the API response in the developer tools we can see that it contains the error `coupon not eligible for all items in your cart`.

The cart is also limited to only 10 items so we can't just add a ton of items to get a massive discount before adding the flag.

However, we can find something interesting if we take a closer look at the checkout page.


## The payment API

There is a hidden `input` field that specifies the `paymentEndpoint`:

```html
<input type="hidden" name="paymentEndpoint" value="http://payment-api:9090">
```

Let's try changing the value:

If we enter an external URL for the endpoint we get an error: `Timeout awaiting 'request' for 5000ms`.

So let's try an internal URL. The webserver must be running there so let's try `http://localhost`.
We now get the error `connect ECONNREFUSED 127.0.0.1:80`. This means we can reach `localhost` but
the server didn't accept the connection. It might be that the webserver isn't actually running on port `80`
but is behind a reverse-proxy. Trying some typical ports we can get a response from port `8080` but get another error: `Unexpected token < in JSON at position 0`.

This makes sense since the webserver likely responds with HTML.

We can also see what happens if we enter an invalid URL like `AAA`.
This also produces an interesting error: `Invalid URL: AAA/wallets/somerandomwallet/balance`

It looks like the server usually sends a request to `http://payment-api:9090/wallets/<the_wallet>/balance`.

Since using any other server for the payment API doesn't seem to work let's keep the domain as `payment-api` but try
to modify the path. If we append a `#` to the base URL (i.e. `http://payment-api:9090/#`) everything after that will be ignored and we get a
response from `http://payment-api:9090/`.

This produces another error: `"Cannot GET /\n\nTry GETting /help for possible endpoints."`

Intersting. Let's try `http://payment-api:9090/help#`.

As a response we get some JSON in the error:

```json
{
    "endpoints": [
        {
            "method": "GET",
            "path": "/wallets/:id/balance",
            "description": "check wallet balance"
        },
        {
            "method": "GET",
            "path": "/wallets",
            "description": "list all wallets"
        },
        {
            "method": "GET",
            "path": "/help",
            "description": "this help message"
        }
    ]
}
```

We already knew about the first and last one but let's try `http://payment-api:9090/wallets#`.

This is the response:

```json
[{"account":"1337-420-69-93dcbbcd","balance":133500}]
```

There seems to be an account `1337-420-69-93dcbbcd` with balance `133500`.

The balance is likely in cent so the account has `1335€`.
Unfortunately, this is `2€` short of the cost of the flag.

However, `2€` is
exactly the maximum amount we can save by using coupons. If we add 10 items for a total of `10€` to the cart
and use the coupon we will get a discount of `-2€`. If we now remove all the items again and only add the flag
the total comes out to `1335€`. If we now enter `1337-420-69-93dcbbcd` as our `Kontonummer` and checkout we get the flag: `CSCG{c00l_k1ds_st4y_@_/home/}`
