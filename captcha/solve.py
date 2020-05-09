#!/usr/bin/env python3

import os, re, base64, time
import cv2
import numpy as np
import requests


ORD_0 = ord("0")
ORD_9 = ord("9")
ORD_A = ord("A")
SIZE = 25
MIN_Y = 4

HUMAN = 0
BOT = 1


def derotate(img, mask):
    coords = np.column_stack(np.where(mask > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    h, w = img.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return rotated


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
    o = ord(c)
    if ORD_0 <= o <= ORD_9:
        return o - ORD_0
    return o - ORD_A + 10


def num2char(n):
    n = int(n)
    if n < 10:
        return str(n)
    return chr(n - 10 + ORD_A)


def find_digits(img):
    _, img_thresh = cv2.threshold(img, 64, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(
        img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    rects = [fixRect(cv2.boundingRect(contour), img.shape) for contour in contours]
    rects = merge_overlapping(rects)

    inverted = ~img

    digits = []
    for i, rect in enumerate(rects):
        if rect[2] > 23:
            digits.append((HUMAN, center(img, rect)))
            continue

        a = center(inverted, rect)
        # b = center(img_thresh, rect)

        d = a.reshape(SIZE * SIZE).astype(np.float32)
        # d = derotate(a, b).reshape(SIZE * SIZE).astype(np.float32)
        digits.append((BOT, d))

    return digits


def load_img(name):
    img = cv2.imread("images/" + name, cv2.IMREAD_GRAYSCALE)
    digits = find_digits(img)

    labels = name[:-4]

    if any(bot != BOT for bot, _ in digits) or len(digits) != len(labels):
        return [], []

    return (b for a, b in digits), map(char2num, labels)


files = os.listdir("images")[:5100]
images, labels = [], []

print("Loading", len(files), "files")

for fname in files:
    imgs, lbls = load_img(fname)
    images.extend(imgs)
    labels.extend(lbls)

assert len(images) == len(labels)

print("Training on", len(images), "digits")

knn = cv2.ml.KNearest_create()
knn.train(np.array(images), cv2.ml.ROW_SAMPLE, np.array(labels))

# img = cv2.imread("test.png", cv2.IMREAD_GRAYSCALE)
# digits = [b for a,b in find_digits(img)]

# ret, result, neighbours, dist = knn.findNearest(np.array(digits), k=5)
# label = [num2char(d[0]) for d in result]
# print(label[-3], label[-2])

# cv2.imshow("x", digits[-2].reshape(SIZE, SIZE).astype(np.uint8))
# cv2.imshow("z", digits[-3].reshape(SIZE, SIZE).astype(np.uint8))
# cv2.waitKey()
# cv2.destroyAllWindows()
# exit()

print("Solving challenge")

regex = re.compile('<img src="data:image/png;base64,([a-zA-Z0-9/+=]+)">')


def decode_and_find_digits(img_b64):
    img = base64.b64decode(img_b64)
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
    return find_digits(img)


def solve(digits):
    knn_todo = []
    human = []

    for i, (bot, d) in enumerate(digits):
        if bot == HUMAN:
            cv2.imshow("x", d)
            cv2.waitKey()
            cv2.destroyAllWindows()
            x = input("Text: ").upper().replace("O", "0")
            human.append((i, x))
        else:
            knn_todo.append(d)

    ret, result, neighbours, dist = knn.findNearest(np.array(knn_todo), k=5)
    label = [num2char(d[0]) for d in result]

    for i, x in human:
        label.insert(i, x)

    return "".join(label)


while True:
    print("Starting attempt")

    r = requests.get("http://hax1.allesctf.net:9200/captcha/0")

    for i in range(4):
        start = time.time()
        imgs = [decode_and_find_digits(img) for img in regex.findall(r.text)]
        print("Got", len(imgs), "images")

        todo = sum(bot == HUMAN for digits in imgs for bot, _ in digits)

        if todo > 10 or (todo > 0 and i < 2):
            print("Too many mistakes")
            break
        elif todo > 0:
            print("Human intervention required for", todo, "digits")

        labels = [solve(img) for img in imgs]

        if i == 3:
            with open("dump.html", "wb") as f:
                f.write(r.content)

        r = requests.post(
            f"http://hax1.allesctf.net:9200/captcha/{i}",
            "&".join(f"{i}={label}" for i, label in enumerate(labels)),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cookies=r.cookies,
        )
        end = time.time()

        if "solution would have been" in r.text or "How can you fail at this" in r.text:
            print("Failed after", round(end - start), "seconds")
            if i == 3:
                print(r.text)
                for i, label in enumerate(labels):
                    print(i, label)
                exit()
            break
    else:
        print(r.text)
        print(r.cookies)
        break

# cutoff = round(len(images) - 100)

# train_imgs = np.array(images[:cutoff])
# train_labels = np.array(labels[:cutoff])
# test_imgs = np.array(images[cutoff:])
# test_labels = np.array(labels[cutoff:]).reshape(-1, 1)

# print(len(train_imgs), len(train_labels), len(test_imgs), len(test_labels))
# print("Training on", len(train_imgs))

# knn = cv2.ml.KNearest_create()
# knn.train(train_imgs, cv2.ml.ROW_SAMPLE, train_labels)

# print("Testing on", len(test_imgs))

# start = time.time()
# ret, result, neighbours, dist = knn.findNearest(test_imgs, k=5)
# end = time.time()
# correct = np.count_nonzero(result == test_labels)
# accuracy = correct * 100.0 / len(result)
# print(accuracy, "% after", end-start, "seconds")

# for i in range(10):
#     print(num2char(result[i][0]), num2char(test_labels[i][0]))
#     cv2.imshow("x", test_imgs[i].reshape(SIZE, SIZE).astype(np.uint8))
#     cv2.waitKey()

# cv2.destroyAllWindows()
