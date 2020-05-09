#!/usr/bin/env python3

import base64
import itertools
import os, re, time

import requests

regex = re.compile('<img src="data:image/png;base64,([a-zA-Z0-9/+=]+)">')
os.makedirs("images", exist_ok=True)

for i in itertools.count():
    print("Collected", i, "images", end="\r")

    r = requests.get(f"http://hax1.allesctf.net:9200/captcha/0")
    img = base64.b64decode(regex.findall(r.text)[0])

    r = requests.post(
        f"http://hax1.allesctf.net:9200/captcha/0",
        "0=garbage",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        cookies=r.cookies,
    )

    sol = re.findall(r"The solution would have been <b>([a-zA-Z0-9]+)<\/b>.", r.text)
    if sol:
        with open(f"images/{sol[0]}.png", "wb") as f:
            f.write(img)

    time.sleep(0.2)
