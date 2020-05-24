# Captcha

The [challenge website](http://hax1.allesctf.net:9200/) tells us that we have to solve some captchas to get the flag.

Playing around with the challenge for a bit we can quickly find out that the challenge consists of
4 stages. In each stage we have to solve an increasing number of captchas in 30 seconds.

The first two stages require only 1 and 3 captchas respectively which is still easily achievable by a human
however the third stage already requires us to solve 10 captchas in 30 seconds which seems pretty much impossible.

However, we don't have to solve all the captchas by hand. We can just write a bot to do it for us.


## Collecting data

When failing on the first stage the site helpfully tells us the correct solution.
We can use this information to collect a large set of captchas with their corresponding solution and
use this data to train a bot to solve them.

Here is the Python script I used for the data collection:

```python
import base64, itertools, os, re, time
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
```


## Automatic captcha recognition

We now want to write a program that can automatically solve a captcha for us.

To do this we first split a given captcha into smaller images, each containing only a single character.
We then use the k-nearest neighbours (knn) algorithm trained on the data we just gathered to recognize the characters in the images.
Then we simply combine the characters in the correct order to solve the captcha.

I used the Python bindings of OpenCV to do all this.

First we import OpenCV and NumPy:

```python
import cv2
import numpy as np
```

Then we can load an image as grayscale, since color doesn't really matter for us:

```python
img = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)
```

Now we want to seperate the images into the different characters.

For this we can use OpenCV's contour detection.
Since it only works on binary images consisting only of black and white
we first need to threshold the image.

After finding the contours we
can then use `cv2.boundingRect` to find the coordinates containing the different characters:

```python
_, img_thresh = cv2.threshold(img, 64, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(img_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
rects = [cv2.boundingRect(contour) for contour in contours]
```

However, for some characters this will produce problems.
For example, the character `i` consists of two seperate parts and even for some other
characters the algorithm sometimes finds multiple overlapping rectangles.

Since each captcha only contains a single row of characters we can simply extend
the height of each rectangle and combine all rectangles that overlap.

Since the characters can sometimes have a lot of rotation I
also extend the width of the rectangles a bit before merging.

To prevent overlapping seperate characters that are just close together
we also don't merge rectangles if the result would be very wide:

```python
SIZE = 25
MIN_Y = 4

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
        overlap = b[0] - a[0] - a[2]
        combined_width = max(a[0] + a[2], b[0] + b[2]) - a[0]
        if overlap <= 0 and combined_width <= SIZE:
            a = (a[0], MIN_Y, combined_width, SIZE)
        else:
            result.append(a)
            a = b
    result.append(a)
    return result

rects = list(map(fixRect, rects))
rects = merge_overlapping(rects)
```

Next we invert the image, cut out the characters and center and reshape them:

```python
def center(image, rect):
    x, y, w, h = rect
    size = max(SIZE, w, h)
    new_x = round(size / 2 - w / 2)
    new_y = round(size / 2 - h / 2)
    centered = np.zeros((size, size), np.uint8)
    centered[new_y : new_y + h, new_x : new_x + w] = image[y : y + h, x : x + w]
    return centered

inverted = ~img

chars = []
for rect in rects:
    char = center(inverted, rect)
    char = char.reshape(SIZE * SIZE).astype(np.float32)
    chars.append(char)
```

We need to invert the image since knn assumes that text is white and the background
is black which is the opposite of what we have.

We center each character and add some border around them if needed to make
them all have the same size. We also reshape the image to a one-dimensional array of numbers.

This is all required for the knn to work correctly.

We can now put all that code into a function `load_train_img` which is used to load an image for training the knn.
The function also returns the label of the image (i.e. the correct solution for the captcha).

To use the labels with knn we also convert all the characters to numbers:

```python
def char2num(c):
    if "0" <= c <= "9":
        return ord(c) - ord("0")
    return ord(c) - ord("A") + 10
```

We can now load the images and train the knn:

```python
images, labels = [], []
for fname in os.listdir("images"):
    imgs, lbls = load_train_img(fname)
    images.extend(imgs)
    labels.extend(lbls)

knn = cv2.ml.KNearest_create()
knn.train(np.array(images), cv2.ml.ROW_SAMPLE, np.array(labels))
```

If we take a look at the cut out characters we will see that sometimes
two characters will completely overlap and get categorised as a single character.

To avoid training the knn on bad data we can add a check if the number of cut out
characters is the same as the characters in the label and skip the image if this is not the case.


## Human intervention required

If we now add some code to automatically start the challenge, get the captchas, solve them
and send the result back we will see that the algorithm performs quite well.

Doing some tests I even found out that if the characters get separated correctly
the detection rate is consistently 100%.

However, there is still a problem: It sometimes happens that a captcha contains
two characters that completely overlap. In this case the detection will not separate them correctly
and our algorithm will produce the wrong result.

This doesn't happen too often but it happens often enough that the algorithm
can't solve the last stage that requires us to solve 100 captchas.

To solve this we can use a simple trick: If the algorithm finds a character
that is very wide it is likely that it actually is two characters. In this case
we just show that part of the image to the user and ask him to identify
the characters.

After a few attempts this now gives us an image with the flag: `CSCG{Y0UR_B0T_S0LV3D_THE_CAPTCHA}`.

Here is the complete program:

```python
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
        overlap = b[0] - a[0] - a[2]
        combined_width = max(a[0] + a[2], b[0] + b[2]) - a[0]
        if overlap <= 0 and combined_width <= SIZE:
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
    for rect in rects:
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
```
