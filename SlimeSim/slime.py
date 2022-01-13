import math
import random

import pyglet
from fishpy.utility.debug import profile

FPS = 60

SLIMES = 3000
SLIME_SIZE = 2.5
SLIME_COLOR = (255, 255, 255)
SLIME_SPEED = 200/FPS

INITIAL_DIRECTION_RANDOM = True
INITIAL_POSITION_RANDOM = True

WALL_BOUNCE_RANDOM_ANGLE = False
RANDOM_DIRECTION_CHANGE_CHANCE = 0.05

DISPERSAL_ENABLED = True
DEGRADATION_STEEPNESS = 1.44
DEGRADATION_OFFSET = 1.07

SENSOR_ANGLE = math.pi/4
SENSOR_OFFSET = 30
ROTATION_ANGLE = math.pi/8

PIXEL_SIZE = (5, 5)
WINDOW_SIZE = (500, 500)
PIXEL_COUNTS = (WINDOW_SIZE[0]//PIXEL_SIZE[0], WINDOW_SIZE[1]//PIXEL_SIZE[1])

window = pyglet.window.Window(
    width=WINDOW_SIZE[0], height=WINDOW_SIZE[1], resizable=False)
batch = pyglet.graphics.Batch()
# color_buffer = [[(0,0,0) for x in range(PIXEL_COUNTS[0])] for y in range(PIXEL_COUNTS[1])]

pixels = []
for y in range(PIXEL_COUNTS[1]):
    row = []
    for x in range(PIXEL_COUNTS[0]):
        row.append(pyglet.shapes.Rectangle(
            x*PIXEL_SIZE[0], y*PIXEL_SIZE[1], PIXEL_SIZE[0], PIXEL_SIZE[1], SLIME_COLOR, batch=batch))
        row[-1].opacity = 0
    pixels.append(row)

slimes = []
for s in range(SLIMES):
    x = random.randint(
        0, WINDOW_SIZE[0]-1) if INITIAL_POSITION_RANDOM else WINDOW_SIZE[0]//2
    y = random.randint(
        0, WINDOW_SIZE[1]-1) if INITIAL_POSITION_RANDOM else WINDOW_SIZE[1]//2
    theta = random.uniform(
        0, 2*math.pi) if INITIAL_DIRECTION_RANDOM else s/SLIMES*2*math.pi
    slimes.append((x, y, theta))


def assess_square(x, y, theta):
    dx, dy = math.cos(theta), math.sin(theta)
    window_x = x+dx*SENSOR_OFFSET
    window_y = y+dy*SENSOR_OFFSET
    pixel_x = min(PIXEL_COUNTS[0]-1, max(0, int(window_x//PIXEL_SIZE[0])))
    pixel_y = min(PIXEL_COUNTS[1]-1, max(0, int(window_y//PIXEL_SIZE[1])))
    return pixels[pixel_y][pixel_x].opacity


def follow_trail(slime):
    x, y, theta = slime[0], slime[1], slime[2]

    forward = assess_square(x, y, theta)
    left = assess_square(x, y, theta+SENSOR_ANGLE)
    right = assess_square(x, y, theta-SENSOR_ANGLE)

    if forward > left and forward > right:
        return 0
    elif forward < left and forward < right:
        return (random.randint(0, 1)*2-1) * ROTATION_ANGLE
    elif left > right:
        return ROTATION_ANGLE
    elif right > left:
        return -ROTATION_ANGLE
    else:
        return 0


def update_slime(slime):
    x, y, theta = slime[0], slime[1], slime[2]
    dx, dy = SLIME_SPEED*math.cos(theta), SLIME_SPEED*math.sin(theta)
    reflect_x, reflect_y = False, False

    if x+dx > WINDOW_SIZE[0] and dx > 0:
        dx = -dx
        reflect_x = True
    elif x+dx < 0 and dx < 0:
        dx = -dx
        reflect_x = True
    if y+dy > WINDOW_SIZE[1] and dy > 0:
        dy = -dy
        reflect_y = True
    elif y+dy < 0 and dy < 0:
        dy = -dy
        reflect_y = True

    if reflect_x:
        if WALL_BOUNCE_RANDOM_ANGLE:
            theta = random.uniform(0, 2*math.pi)
        else:
            theta = (3*math.pi - theta) % (2*math.pi)
    elif reflect_y:
        if WALL_BOUNCE_RANDOM_ANGLE:
            theta = random.uniform(0, 2*math.pi)
        else:
            theta = math.pi*2 - theta
    else:
        if random.random() < RANDOM_DIRECTION_CHANGE_CHANCE:
            theta += random.uniform(-math.pi/4, math.pi/4)
        else:
            theta += follow_trail(slime)
        theta %= 2*math.pi

    x, y = x+dx, y+dy
    return (x, y, theta)


def update(_):
    for i in range(len(slimes)):
        slimes[i] = update_slime(slimes[i])
    window.clear()
    draw()


def degrade(opacity):
    if opacity < 5:
        return 0
    opacity = opacity / 255
    fx = 255 * 0.9 * (opacity ** DEGRADATION_STEEPNESS / (opacity ** DEGRADATION_STEEPNESS +
                      (DEGRADATION_OFFSET * (1-opacity)) ** DEGRADATION_STEEPNESS))
    return fx


def disperse(x, y):
    count = 20
    sum_ = pixels[y][x].opacity*count
    x_min, y_min = max(x-1, 0), max(y-1, 0)
    x_max, y_max = min(x+2, PIXEL_COUNTS[0]), min(y+2, PIXEL_COUNTS[1])
    for y1 in range(y_min, y_max):
        for x1 in range(x_min, x_max):
            sum_ += pixels[y1][x1].opacity
            count += 1
    return sum_/count


def draw():
    for slime in slimes:
        x, y = int(slime[0]//PIXEL_SIZE[0]), int(slime[1]//PIXEL_SIZE[1])
        x = min(PIXEL_COUNTS[0]-1, max(0, x))
        y = min(PIXEL_COUNTS[1]-1, max(0, y))
        pixels[y][x].opacity = 255
    for y in range(len(pixels)):
        for x in range(len(pixels[y])):
            if DISPERSAL_ENABLED:
                old_opacity = disperse(x, y)
            else:
                old_opacity = pixels[y][x].opacity
            new_opacity = int(degrade(old_opacity))
            if old_opacity != new_opacity:
                pixels[y][x].opacity = new_opacity
    batch.draw()


if __name__ == '__main__':
    pyglet.clock.schedule_interval(update, 1/FPS)
    pyglet.app.run()
