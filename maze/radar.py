from turtle import *

cords = []

with open("logs/radar.txt") as f:
    for line in f:
        x, y, z, *_ = map(float, line.split(" "))
        cords.append((x, z))


tracer(False)
speed(0)
hideturtle()

penup()
goto(*cords[0])
pendown()

for x, y in cords:
    goto(x, y)

done()
