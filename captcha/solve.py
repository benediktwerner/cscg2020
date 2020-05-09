#!/usr/bin/env python3

import base64, os, re, time
import cv2
import numpy as np
import requests


SIZE = 25
MIN_Y = 4


def center(image, rect):
    x, y, w, h = rect
    size = max(SIZE, w, h)
    new_x = round(size / 2 - w / 2)
    new_y = round(size / 2 - h / 2)
    centered = np.zeros((size, size), np.uint8)
    centered[new_y : new_y + h, new_x : new_x + w] = image[y : y + h, x : x + w]
    return centered


def fixRect(rect, shape):
    x, _, w, _ = rect
    _, iw = shape
    x -= 1
    w += 2
    if x < 0:
        x = 0
    if x + w > iw:
        w = iw - x
    return (x, MIN_Y, w, SIZE)


def merge_overlapping(rects):
    rects.sort(key=lambda r: r[0])
    result = []
    a = rects[0]
    for b in rects[1:]:
        overlapp = b[0] - a[0] - a[2]
        combined_width = max(a[0] + a[2], b[0] + b[2]) - a[0]
        if overlapp <= 0 and combined_width <= SIZE:
            a = (a[0], MIN_Y, combined_width, SIZE)
        else:
            result.append(a)
            a = b
    result.append(a)
    return result


def char2num(c):
    if "0" <= c <= "9":
        return ord(c) - ord("0")
    return ord(c) - ord("A") + 10


def num2char(n):
    n = int(n)
    if n < 10:
        return str(n)
    return chr(n - 10 + ord("A"))


def find_chars(img):
    _, img_thresh = cv2.threshold(img, 64, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    rects = [fixRect(cv2.boundingRect(contour), img.shape) for contour in contours]
    rects = merge_overlapping(rects)

    inverted = ~img

    chars = []
    for i, rect in enumerate(rects):
        if rect[2] > 23:
            chars.append((False, center(img, rect)))
            continue

        char = center(inverted, rect)
        char = char.reshape(SIZE * SIZE).astype(np.float32)
        chars.append((True, char))

    return chars


def load_train_img(name):
    img = cv2.imread("images/" + name, cv2.IMREAD_GRAYSCALE)
    chars = find_chars(img)

    labels = name[:-4]

    if any(not valid for valid, _ in chars) or len(chars) != len(labels):
        return [], []

    return (char for _, char in chars), map(char2num, labels)


def decode_and_find_chars(img_b64):
    img = base64.b64decode(img_b64)
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
    return find_chars(img)


def solve(chars):
    bot = []
    human = []

    for i, (valid, c) in enumerate(chars):
        if valid:
            bot.append(c)
        else:
            cv2.imshow("x", c)
            cv2.waitKey()
            cv2.destroyAllWindows()
            x = input("Text: ").upper().replace("O", "0")
            human.append((i, x))

    ret, result, neighbours, dist = knn.findNearest(np.array(bot), k=5)
    label = [num2char(d[0]) for d in result]

    for i, x in human:
        label.insert(i, x)

    return "".join(label)


files = os.listdir("images")[:5000]
images, labels = [], []

print("Loading", len(files), "files")

for fname in files:
    imgs, lbls = load_train_img(fname)
    images.extend(imgs)
    labels.extend(lbls)

print("Training on", len(images), "characters")

knn = cv2.ml.KNearest_create()
knn.train(np.array(images), cv2.ml.ROW_SAMPLE, np.array(labels))

regex = re.compile('<img src="data:image/png;base64,([a-zA-Z0-9/+=]+)">')


while True:
    print("Starting attempt")

    r = requests.get("http://hax1.allesctf.net:9200/captcha/0")

    for i in range(4):
        start = time.time()

        imgs = [decode_and_find_chars(img) for img in regex.findall(r.text)]
        print("Got", len(imgs), "images")

        todo = sum(not valid for chars in imgs for valid, _ in chars)

        if todo > 10 or (todo > 0 and i < 2):
            print(f"Skipping: Detection too bad ({todo} bad characters)")
            break
        elif todo > 0:
            print("Human intervention required for", todo, "characters")

        labels = [solve(img) for img in imgs]

        r = requests.post(
            f"http://hax1.allesctf.net:9200/captcha/{i}",
            "&".join(f"{i}={label}" for i, label in enumerate(labels)),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cookies=r.cookies,
        )

        end = time.time()

        if "solution would have been" in r.text or "How can you fail at this" in r.text:
            print("Failed after", round(end - start), "seconds")
            break
    else:
        print("Success!")

        with open("flag.html", "wb") as f:
            f.write(r.content)

        break
